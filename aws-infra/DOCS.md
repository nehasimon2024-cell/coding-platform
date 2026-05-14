# AWS Infrastructure — Developer Documentation

AWS CDK (Python) deployment for the Coding Assessment Platform.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Repository Structure](#2-repository-structure)
3. [Architecture](#3-architecture)
4. [Prerequisites](#4-prerequisites)
5. [CDK Setup](#5-cdk-setup)
6. [Deploying the Stack](#6-deploying-the-stack)
7. [What Happens on First Boot](#7-what-happens-on-first-boot)
8. [Docker Compose Services](#8-docker-compose-services)
9. [Networking & Ports](#9-networking--ports)
10. [Secrets & Passwords](#10-secrets--passwords)
11. [SSH Access & Management](#11-ssh-access--management)
12. [Post-Deployment Steps](#12-post-deployment-steps)
13. [Stack Outputs](#13-stack-outputs)
14. [Teardown](#14-teardown)
15. [Alternative Stacks (for reference)](#15-alternative-stacks-for-reference)

---

## 1. Overview

The platform is deployed to a **single Ubuntu 22.04 EC2 instance** using AWS CDK (Python). All application services run in Docker containers managed by Docker Compose. An Nginx reverse proxy on the host handles incoming HTTP traffic.

This single-instance approach keeps costs low (eligible for `t3.micro` free tier) while remaining simple to understand and manage.

---

## 2. Repository Structure

```
aws-infra/
├── app.py               # CDK app entry point
├── cdk.json             # CDK toolkit config (context)
├── cdk_stack_ec2.py     # Main stack: VPC, security group, EC2 + user-data
├── requirements.txt     # CDK Python dependencies (aws-cdk-lib, constructs)
├── stacks/
│   ├── ec2_stack.py         # Earlier iteration of the EC2 stack
│   ├── fargate_cdk_stack.py # ECS Fargate variant (not actively deployed)
│   ├── stackv3_ec2.py       # Another EC2 iteration
│   └── stack_v2.json        # CloudFormation template snapshot
├── diff.txt             # Last recorded cdk diff output
└── stack_resources.txt  # Inventory of all deployed resources
```

> **Active stack:** `cdk_stack_ec2.py` (`Ec2SingleInstanceStack`). The files in `stacks/` are historical references — they are **not** deployed by the current `app.py`.

---

## 3. Architecture

```
Internet
   │
   │  :80 (HTTP)   :22 (SSH)   :2358 (Judge0 API)
   ▼
┌──────────────────────────────────────────────────────────┐
│  EC2 Instance (Ubuntu 22.04, t3.micro, 50 GB GP3)        │
│  Public Subnet — 1 AZ — No NAT Gateway                   │
│                                                           │
│  ┌──────────────────────────────────────────────────┐    │
│  │  Nginx (host, :80)                               │    │
│  │  Reverse proxy → localhost:8000                  │    │
│  └──────────────────────┬───────────────────────────┘    │
│                         │ Docker network                  │
│  ┌──────────────────────▼───────────────────────────┐    │
│  │  Docker Compose                                   │    │
│  │                                                   │    │
│  │  ┌─────────────┐  ┌────────────┐                 │    │
│  │  │  postgres   │  │   redis    │                 │    │
│  │  │  :5432      │  │   :6379    │                 │    │
│  │  └──────┬──────┘  └─────┬──────┘                │    │
│  │         │               │                        │    │
│  │  ┌──────▼───────────────▼───────────────────┐   │    │
│  │  │  judge0-server  (:2358)                  │   │    │
│  │  │  judge0-worker  (internal)               │   │    │
│  │  └──────────────────────┬───────────────────┘   │    │
│  │                         │                        │    │
│  │  ┌──────────────────────▼───────────────────┐   │    │
│  │  │  backend (FastAPI + Gunicorn, :8000)     │   │    │
│  │  └──────────────────────────────────────────┘   │    │
│  └──────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────┘
```

---

## 4. Prerequisites

| Requirement | Notes |
|------------|-------|
| AWS account + credentials | `aws configure` or IAM role |
| AWS CDK CLI | `npm install -g aws-cdk` |
| Python 3.8+ | For the CDK app |
| EC2 Key Pair | Must already exist in the target region |

Install Python CDK dependencies:

```bash
cd aws-infra

python -m venv .venv
.venv\Scripts\activate       # Windows
# source .venv/bin/activate  # macOS/Linux

pip install -r requirements.txt
```

Bootstrap CDK in your account/region (one-time per account+region):

```bash
cdk bootstrap aws://<ACCOUNT_ID>/<REGION>
```

---

## 5. CDK Setup

### `app.py`

```python
# Instantiates Ec2SingleInstanceStack with the AWS environment from env vars/config
```

Set your target account and region via environment variables or `~/.aws/config`:

```bash
export AWS_DEFAULT_REGION=ap-south-1
export AWS_ACCOUNT_ID=123456789012
```

### Stack Parameters

The stack accepts **CloudFormation parameters** that can be passed at deploy time:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `InstanceType` | `t3.micro` | EC2 instance type |
| `KeyName` | (required) | Name of an existing EC2 Key Pair for SSH |
| `AdminIpCidr` | `0.0.0.0/0` | CIDR to allow SSH from (restrict this in production) |

---

## 6. Deploying the Stack

```bash
cd aws-infra

# Synthesize CloudFormation template (dry run)
cdk synth

# Preview changes
cdk diff

# Deploy
cdk deploy \
  --parameters KeyName=<your-key-pair-name> \
  --parameters InstanceType=t3.medium \
  --parameters AdminIpCidr=<your-ip>/32
```

> **Tip:** Use `--parameters AdminIpCidr=$(curl -s ifconfig.me)/32` to lock SSH to your current IP.

The deploy will take **3–5 minutes** for CloudFormation to provision the VPC and EC2 instance. First-boot setup (Docker, app bootstrap) then runs automatically as User Data and takes **an additional 10–15 minutes** in the background.

---

## 7. What Happens on First Boot

The EC2 User Data script (`cdk_stack_ec2.py`, embedded bash) runs automatically on the first start and performs the following steps:

1. **System update** — `apt-get update && upgrade`
2. **Install dependencies** — Docker, Docker Compose, Git, Nginx, `jq`, `pwgen`
3. **Enable Docker** and add the `ubuntu` user to the docker group
4. **Add 2 GB swap** — helps `t3.micro` handle Docker image pulls without OOM
5. **Clone the repository** from GitHub (`main` branch) into `/home/ubuntu/coding-platform/repo`
6. **Generate secrets** using `pwgen`:
   - `POSTGRES_PASSWORD`
   - `REDIS_PASSWORD`
   - `SECRET_KEY_BASE`
   - `JWT_SECRET_KEY`
   - `JUDGE0_PROXY_TOKEN`
   - `ADMIN_SEED_KEY`
7. **Write `.env`** file with all generated secrets and service addresses
8. **Write `init-db.sql`** to create the `codingplatform` database on first Postgres start
9. **Write `backend.Dockerfile`** and **`docker-compose.yml`** inline
10. **Configure Nginx** as a reverse proxy (port 80 → localhost:8000)
11. **Start infrastructure containers** — Postgres, Redis
12. **Wait for Postgres** to be ready (up to 2 minutes)
13. **Ensure `codingplatform` database exists**
14. **Start Judge0** server and worker
15. **Build and start the backend**
16. **Run schema bootstrap** — `Base.metadata.create_all()`

---

## 8. Docker Compose Services

The following services are defined in the generated `docker-compose.yml` on the EC2 instance:

| Service | Image | Ports | Description |
|---------|-------|-------|-------------|
| `postgres` | `postgres:13` | 5432 (internal) | Shared database for both Judge0 and the platform |
| `redis` | `redis:6.0` | 6379 (internal) | Required by Judge0 for job queuing |
| `judge0-server` | `judge0/judge0:1.13.1` | 2358 (host) | Judge0 API server |
| `judge0-worker` | `judge0/judge0:1.13.1` | — | Judge0 job executor |
| `backend` | Built from repo | 8000 (host) | FastAPI application |

All services use a shared `.env` file for configuration.

### Useful Docker commands (run on the EC2 instance)

```bash
# SSH into the EC2 instance first (see section 11)
cd /home/ubuntu/coding-platform

# View running services
docker-compose ps

# View backend logs
docker-compose logs -f backend

# View Judge0 logs
docker-compose logs -f judge0-server

# Restart the backend after a code change
docker-compose up -d --build backend

# Restart all services
docker-compose restart

# Pull the latest code and redeploy backend
cd /home/ubuntu/coding-platform/repo
git pull origin main
cd /home/ubuntu/coding-platform
docker-compose up -d --build backend
```

---

## 9. Networking & Ports

### Security Group Inbound Rules (Current Dev Architecture)

| Port | Protocol | Source | Purpose |
|------|----------|--------|---------|
| 22 | TCP | `AdminIpCidr` param | SSH access |
| 80 | TCP | `0.0.0.0/0` | HTTP (Nginx reverse proxy) |
| 443 | TCP | `0.0.0.0/0` | HTTPS (reserved; configure SSL separately) |
| 2358 | TCP | `0.0.0.0/0` | Judge0 API (direct access) |
| 8000 | TCP | `0.0.0.0/0` | FastAPI (direct access, also behind Nginx) |

> **Recommendation:** In production, close port 2358 and 8000 to the public and only expose 80/443 through Nginx. The backend communicates with Judge0 internally via the Docker network.

### VPC Configuration

- Single public subnet in 1 AZ (`max_azs=1`)
- No NAT gateways (cost saving)
- EC2 instance has a public IP assigned automatically

### Production Deployment: Private Subnet + Load Balancer

For production deployments, implement a **secured network architecture** using a **public-facing load balancer** with **private EC2 instance(s)**:

**Architecture Changes:**
1. **Private Subnet** — Place the EC2 instance(s) in a private subnet with **no direct internet access**
   - Security group allows traffic only from the load balancer's security group
   - SSH access via Systems Manager Session Manager or a bastion host in the public subnet
   
2. **Public Subnet** — Deploy an **AWS Application Load Balancer (ALB)** or **Network Load Balancer (NLB)** 
   - Listener on port 80 (HTTP) and 443 (HTTPS)
   - Target group routes traffic to EC2 instances (port 8000)
   - Handles SSL/TLS termination and distributes load

3. **NAT Gateway** — Add a NAT gateway in the public subnet to allow EC2 instances to pull Docker images and software updates
   - Route private subnet traffic through NAT for outbound internet access

**Security Benefits:**
- EC2 instances are not exposed directly to the public internet
- Judge0 API (port 2358) and FastAPI (port 8000) are internal-only
- Load balancer acts as the single point of ingress
- Enables horizontal scaling by adding more EC2 instances behind the load balancer

**CDK Stack Modifications:**
Update `cdk_stack_ec2.py` to:
- Create public and private subnets with proper route tables
- Deploy an ALB in the public subnet
- Place EC2 instance(s) in the private subnet with restricted security groups
- Add NAT gateway for outbound connectivity
- Update security groups to allow ALB → EC2 traffic only

This architecture is suitable for production workloads and is more resilient than the current single-instance public subnet design.

---

## 10. Secrets & Passwords

All secrets are **auto-generated** during first boot using `pwgen -s` and written to `/home/ubuntu/coding-platform/.env`.

> ⚠️ **The `.env` file is the source of truth for all secrets on the instance.** If the instance is terminated and a new one is created, new secrets will be generated and the database will need to be re-seeded.

To retrieve the generated `ADMIN_SEED_KEY` (needed to seed the database):

```bash
ssh ubuntu@<instance-ip>
grep ADMIN_SEED_KEY /home/ubuntu/coding-platform/.env
```

---

## 11. SSH Access & Management

```bash
# Connect to the instance
ssh -i /path/to/your-key.pem ubuntu@<InstancePublicIp>

# Check if bootstrap has completed (look for "backend" container running)
docker ps

# Check bootstrap logs (written during first boot via user-data)
cat /var/log/cloud-init-output.log
```

---

## 12. Post-Deployment Steps

After the stack is deployed and first-boot completes:

### 1. Verify the backend is healthy

```bash
curl http://<InstancePublicIp>/health
```

Expected response:
```json
{
  "status": "healthy",
  "services": {
    "database": { "status": "up", "latency_ms": 2 },
    "judge0": { "status": "up", "latency_ms": 45 }
  }
}
```

### 2. Verify Judge0 execution

```bash
curl http://<InstancePublicIp>/judge0-smoke
```

### 3. Seed the database

The database schema is created automatically on first boot. To seed problems and skills:

```bash
# Get the ADMIN_SEED_KEY
ssh ubuntu@<InstancePublicIp> grep ADMIN_SEED_KEY /home/ubuntu/coding-platform/.env

# Seed the database
curl -X POST http://<InstancePublicIp>/admin/seed \
  -H "X-API-Key: <ADMIN_SEED_KEY>"
```

> **Note:** The seeding script and problem dataset are expected to be located in the project's `scripts/` directory at the repo root. See the root-level `scripts/` folder for up-to-date instructions.

### 4. Create an admin user

Currently, admin users must be inserted directly into the database. SSH into the instance and run:

```bash
docker-compose exec postgres psql -U postgres -d codingplatform
```

Then run an `INSERT INTO users` with a bcrypt-hashed password and `role = 'admin'`.

### 5. Deploy the frontend

The frontend is a static SPA. Build it with the correct `VITE_API_URL` pointing to the EC2 instance's public IP or domain, then serve it from Nginx or a CDN (e.g. CloudFront + S3).

---

## 13. Stack Outputs

After `cdk deploy`, the following outputs are printed:

| Output Key | Description |
|------------|-------------|
| `InstancePublicIp` | Public IPv4 address of the EC2 instance |
| `InstanceId` | EC2 instance ID (for AWS console reference) |
| `InstancePublicDnsName` | Public DNS name (usable as a hostname) |

---

## 14. Teardown

```bash
cdk destroy
```

This will delete the CloudFormation stack, terminating the EC2 instance, VPC, subnets, and security groups.

> ⚠️ **Data loss warning:** All data in Postgres (on the EC2 EBS volume) will be permanently deleted on termination. Take a database snapshot before destroying if you need to preserve data.

---

## 15. Alternative Stacks (for reference)

The `stacks/` subdirectory contains earlier iterations kept for historical reference:

| File | Description |
|------|-------------|
| `ec2_stack.py` | Earlier EC2 stack version |
| `fargate_cdk_stack.py` | ECS Fargate variant with ALB, RDS, and separate task definitions for each service. Higher cost but more scalable. |
| `stackv3_ec2.py` | Another EC2 iteration with slightly different user-data |
| `stack_v2.json` | Synthesized CloudFormation JSON from a previous deploy |

These are **not deployed** by the current `app.py`. They are available for reference if the team wants to migrate to a more scalable architecture in the future.

"""FastAPI backend for the Coding Assessment Platform."""

import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# from mangum import Mangum
from app.routes.admin.core import router as admin_router
from app.routes.auth import router as auth_router
from app.routes.sessions import router as sessions_router
from app.routes.skills import router as skills_router
from app.routes.submissions import router as submissions_router
from app.routes.system import router as system_router

logging.basicConfig(level=logging.INFO)


env = os.getenv("ENV", "").lower()
if env == "production":
    # In production, restrict to configured origins only
    allowed = os.getenv("CORS_ALLOWED_ORIGINS", "")
    if not allowed:
        raise ValueError("CORS_ALLOWED_ORIGINS must be set in production")
    CORS_ORIGINS = [origin.strip() for origin in allowed.split(",") if origin.strip()]
else:
    # Non-production: allow all
    CORS_ORIGINS = ["*"]


app = FastAPI(
    title="Coding Assessment Platform API",
    description="Backend API for the coding assessment platform",
    version="1.0.0",
)

# CORS — allow all during development, restrict in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(skills_router)
app.include_router(sessions_router)
app.include_router(submissions_router)
app.include_router(admin_router)
app.include_router(system_router)


# # ---- Mangum handler for AWS Lambda ----
# handler = Mangum(app, lifespan="off")

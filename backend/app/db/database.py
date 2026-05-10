"""Database configuration and session management."""

import json
import os
import logging
from collections.abc import Generator
from functools import lru_cache


import boto3
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Load local .env from the closest parent directory automatically
load_dotenv()
logger = logging.getLogger(__name__)


def build_database_url() -> str:
    """Construct the database URL from environment variables or AWS Secrets Manager."""
    if direct_url := os.environ.get("DATABASE_URL"):
        return direct_url

    db_user = os.environ.get("DB_USER")
    db_password = os.environ.get("DB_PASSWORD")
    db_host = os.environ.get("DB_HOST")
    db_name = os.environ.get("DB_NAME")
    db_port = os.environ.get("DB_PORT", "5432")

    if not (db_user and db_password) and (secret_arn := os.environ.get("DB_SECRET_ARN")):
        creds = json.loads(boto3.client("secretsmanager").get_secret_value(SecretId=secret_arn)["SecretString"])
        db_user = db_user or creds.get("username")
        db_password = db_password or creds.get("password")
        db_host = db_host or creds.get("host")
        db_name = db_name or creds.get("dbname")

    if not (db_host and db_user and db_password and db_name):
        raise RuntimeError("Missing mandatory database connection fields (Host, User, Password, or Name).")

    return f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


@lru_cache
def get_session_local() -> sessionmaker[Session]:
    database_url = build_database_url()
    engine = create_engine(database_url, pool_pre_ping=True)

    return sessionmaker(
        bind=engine, autocommit=False, autoflush=False, expire_on_commit=False
    )


def get_db() -> Generator[Session, None, None]:
    db = get_session_local()()
    try:
        yield db
    finally:
        db.close()

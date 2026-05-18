"""FastAPI backend for the Coding Assessment Platform."""

import logging

from fastapi import FastAPI

# from mangum import Mangum
from app.routes.admin.core import router as admin_router
from app.routes.auth import router as auth_router
from app.routes.sessions import router as sessions_router
from app.routes.skills import router as skills_router
from app.routes.submissions import router as submissions_router
from app.routes.system import router as system_router

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    root_path="/api",   
    title="Coding Assessment Platform API",
    description="Backend API for the coding assessment platform",
    version="1.0.0",
)


app.include_router(auth_router)
app.include_router(skills_router)
app.include_router(sessions_router)
app.include_router(submissions_router)
app.include_router(admin_router)
app.include_router(system_router)


# # ---- Mangum handler for AWS Lambda ----
# handler = Mangum(app, lifespan="off")

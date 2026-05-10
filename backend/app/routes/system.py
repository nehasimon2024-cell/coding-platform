import os
import time
from typing import Any

import requests
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.database import get_db
from app.judge0_service import Judge0Service

router = APIRouter(tags=["system"])

judge0_service = Judge0Service()

_SMOKE_LANGUAGE_CASES = [
    {
        "name": "python",
        "language_id": 71,
        "code": "print('ok')",
        "expected_output": "ok",
    },
    {
        "name": "java",
        "language_id": 62,
        "code": "public class Main { public static void main(String[] args) { System.out.println('ok'); } }",
        "expected_output": "ok",
    },
    {
        "name": "js",
        "language_id": 63,
        "code": "console.log('ok')",
        "expected_output": "ok",
    },
    {
        "name": "typescript",
        "language_id": 74,
        "code": "console.log('ok')",
        "expected_output": "ok",
    },
]


@router.get("/")
def root() -> dict[str, str]:
    """Root API endpoint."""
    return {
        "name": "Coding Assessment Platform API",
        "status": "running",
        "docs_url": "/docs",
        "health_url": "/health",
    }


@router.get("/health")
def health_check(db: Session = Depends(get_db)) -> JSONResponse:
    """Comprehensive system health check with detailed metrics."""
    health_status = {
        "status": "healthy",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime()),
        "environment": os.getenv("ENV", "development"),
        "services": {
            "database": {"status": "unknown"},
            "judge0": {"status": "unknown"},
        },
    }

    # 1. Check Database with Latency
    db_start = time.perf_counter()
    try:
        db.execute(text("SELECT 1"))
        db_latency = int((time.perf_counter() - db_start) * 1000)
        health_status["services"]["database"] = {
            "status": "up",
            "latency_ms": db_latency,
        }
    except Exception as exc:
        health_status["services"]["database"] = {"status": "down", "error": str(exc)}
        health_status["status"] = "degraded"

    # 2. Check Judge0 with Latency and Metadata
    j0_start = time.perf_counter()
    try:
        url = f"{judge0_service.base_url}/languages"
        response = requests.get(url, headers=judge0_service._headers(), timeout=3)
        response.raise_for_status()
        languages = response.json()
        j0_latency = int((time.perf_counter() - j0_start) * 1000)
        health_status["services"]["judge0"] = {
            "status": "up",
            "latency_ms": j0_latency,
            "languages_count": len(languages) if isinstance(languages, list) else 0,
            "base_url": judge0_service.base_url,
        }
    except Exception as exc:
        health_status["services"]["judge0"] = {
            "status": "down",
            "error": str(exc),
            "base_url": judge0_service.base_url,
        }
        health_status["status"] = "degraded"

    status_code = 200 if health_status["status"] == "healthy" else 503
    return JSONResponse(status_code=status_code, content=health_status)


@router.get("/judge0-smoke")
def judge0_smoke_test() -> JSONResponse:
    """End-to-end Judge0 execution check using multiple tiny language submissions."""
    started = time.perf_counter()
    language_results = []

    for smoke_case in _SMOKE_LANGUAGE_CASES:
        try:
            result = judge0_service.execute(
                code=str(smoke_case["code"]),
                language_id=int(smoke_case["language_id"]),
                test_inputs=[
                    {"input": "", "output": str(smoke_case["expected_output"])}
                ],
            )
            language_results.append(
                {
                    "language": smoke_case["name"],
                    "language_id": smoke_case["language_id"],
                    "passed": bool(result.get("passed", False)),
                    "passed_tests": int(result.get("passed_tests", 0)),
                    "total_tests": int(result.get("total_tests", 0)),
                }
            )
        except (
            requests.RequestException,
            TimeoutError,
            RuntimeError,
            ValueError,
        ) as exc:
            language_results.append(
                {
                    "language": smoke_case["name"],
                    "language_id": smoke_case["language_id"],
                    "passed": False,
                    "passed_tests": 0,
                    "total_tests": 1,
                    "error": str(exc),
                }
            )

    latency_ms = int((time.perf_counter() - started) * 1000)
    total_passed = sum(int(item["passed_tests"]) for item in language_results)
    total_tests = sum(int(item["total_tests"]) for item in language_results)
    overall_passed = all(bool(item["passed"]) for item in language_results) and bool(
        language_results
    )

    return JSONResponse(
        status_code=200 if overall_passed else 503,
        content={
            "status": "ok" if overall_passed else "down",
            "judge0_execution": overall_passed,
            "judge0_base_url": judge0_service.base_url,
            "latency_ms": latency_ms,
            "passed_tests": total_passed,
            "total_tests": total_tests,
            "language_results": language_results,
        },
    )

import base64
import io
import logging
import os
import time
import zipfile
from typing import Any

import requests

try:
    import urllib3

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except Exception:
    pass


logger = logging.getLogger(__name__)

# Text fields that Judge0 base64-encodes in responses when base64_encoded=true
_B64_RESPONSE_FIELDS = ("stdout", "stderr", "compile_output", "message", "source_code")


def _judge0_verify_ssl() -> bool:
    return os.getenv("JUDGE0_VERIFY_SSL", "false").strip().lower() in (
        "1",
        "true",
        "yes",
    )


def _b64_encode(text: str) -> str:
    """UTF-8 → base64 string, safe to send in JSON."""
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


def _b64_decode(value: str) -> str:
    """base64 string → UTF-8, replacing undecodable bytes."""
    try:
        return base64.b64decode(value).decode("utf-8", errors="replace")
    except Exception:
        return value


def _decode_response_fields(result: dict[str, Any]) -> dict[str, Any]:
    """Decode all base64 text fields Judge0 returns when base64_encoded=true."""
    for field in _B64_RESPONSE_FIELDS:
        val = result.get(field)
        if isinstance(val, str):
            result[field] = _b64_decode(val)
    return result


def _truncate_text(value: Any, limit: int = 2000) -> str:
    text = "" if value is None else str(value)
    if len(text) <= limit:
        return text
    return f"{text[:limit]}...<truncated:{len(text) - limit}>"


def map_status(result: dict[str, Any]) -> tuple[str, str | None]:
    compile_output = result.get("compile_output")
    if compile_output:
        return ("compile_error", _truncate_text(compile_output))

    stderr = result.get("stderr")
    if stderr:
        return ("runtime_error", _truncate_text(stderr))

    status_obj = result.get("status")
    status_id = status_obj.get("id") if isinstance(status_obj, dict) else None
    if status_id == 5:
        return ("time_limit_exceeded", _truncate_text(result.get("message")))
    if status_id == 3:
        return ("success", None)

    return ("runtime_error", _truncate_text(result.get("message")))


class Judge0Service:
    """Judge0 CE client — always async (wait=false), always base64_encoded=true."""

    TERMINAL_STATUSES = {3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14}

    def __init__(self, base_url: str | None = None, timeout_seconds: int = 25) -> None:
        self.base_url = (
            base_url or os.getenv("JUDGE0_BASE_URL", "https://ce.judge0.com")
        ).rstrip("/")
        self.timeout_seconds = timeout_seconds

    def _headers(self) -> dict[str, str]:
        return {"Content-Type": "application/json"}

    def _post_submission(self, payload: dict[str, Any]) -> dict[str, Any]:
        """POST a submission with base64_encoded=true & wait=false.

        Text fields (source_code, stdin, expected_output) must already be
        base64-encoded by the caller. additional_files is always a base64 zip.
        """
        url = f"{self.base_url}/submissions?base64_encoded=true&wait=false"
        verify = _judge0_verify_ssl()
        response = requests.post(
            url,
            json=payload,
            headers=self._headers(),
            timeout=self.timeout_seconds,
            verify=verify,
        )
        if not response.ok:
            detail = (response.text or "").strip() or response.reason
            logger.error(
                "Judge0 submission rejected: status=%s detail=%s",
                response.status_code,
                detail[:500],
            )
            raise requests.HTTPError(
                f"{response.status_code} {response.reason} — Judge0 says: {detail[:500]}",
                response=response,
            )
        return response.json()

    def _get_submission(self, token: str) -> dict[str, Any]:
        """Poll GET /submissions/{token} with base64_encoded=true; auto-decodes text fields."""
        url = f"{self.base_url}/submissions/{token}?base64_encoded=true"
        verify = _judge0_verify_ssl()
        response = requests.get(
            url,
            headers=self._headers(),
            timeout=self.timeout_seconds,
            verify=verify,
        )
        response.raise_for_status()
        return _decode_response_fields(response.json())

    def _poll_until_done(
        self,
        token: str,
        *,
        max_attempts: int = 40,
        interval_seconds: float = 1.0,
    ) -> dict[str, Any]:
        """Poll until a terminal status or timeout. Logs one line per poll at DEBUG."""
        result: dict[str, Any] = {"token": token}
        for attempt in range(max_attempts):
            time.sleep(interval_seconds)
            polled = self._get_submission(token)
            status_id = (polled.get("status") or {}).get("id")
            logger.debug(
                "Judge0 poll %s/%s token=%s status_id=%s",
                attempt + 1,
                max_attempts,
                token,
                status_id,
            )
            result = polled
            if status_id in self.TERMINAL_STATUSES:
                return result
        raise TimeoutError(
            f"Judge0 timed out after {max_attempts} poll attempts (token={token})"
        )

    # ------------------------------------------------------------------
    # Single-file execution
    # ------------------------------------------------------------------

    def _execute_one(
        self,
        code: str,
        language_id: int,
        stdin: str,
        expected_output: str | None,
        setup_sql: str | None = None,
        problem_id: str | None = None,
        request_id: str | None = None,
    ) -> dict[str, Any]:

        user_code = (code if code is not None else "") or ""
        user_code_stripped = user_code.strip()

        if not user_code_stripped:
            raise ValueError(
                "No program was sent to the code runner. Enter your solution in the editor, then run again."
            )

        if language_id == 82:
            # SQLite: prepend hidden setup so the candidate's query runs against a seeded DB.
            setup = (
                (setup_sql.rstrip() + "\n\n") if setup_sql and setup_sql.strip() else ""
            )
            final_code = f"{setup}{user_code_stripped}"
            stdin_to_send = ""
        else:
            final_code = user_code_stripped
            stdin_to_send = stdin if stdin is not None else ""

        payload: dict[str, Any] = {
            "source_code": _b64_encode(final_code),
            "language_id": language_id,
            "stdin": _b64_encode(stdin_to_send),
        }
        if expected_output is not None:
            payload["expected_output"] = _b64_encode(expected_output)

        token_response = self._post_submission(payload)
        token = token_response.get("token")
        if not token:
            raise RuntimeError("Judge0 did not return a submission token")

        logger.debug(
            "Judge0 single-file submitted: lang=%s token=%s req=%s",
            language_id,
            token,
            request_id,
        )
        result = self._poll_until_done(token, max_attempts=40, interval_seconds=0.5)
        status_id = (result.get("status") or {}).get("id")
        logger.debug(
            "Judge0 single-file done: token=%s status_id=%s req=%s",
            token,
            status_id,
            request_id,
        )
        return result

    # ------------------------------------------------------------------
    # Multi-file execution (language_id=89)
    # ------------------------------------------------------------------

    def _build_multifile_archive(
        self,
        *,
        files: list[dict[str, Any]],
        entry_point: str,
    ) -> str:
        if not files:
            raise ValueError("Multi-file execution requires at least one file.")

        entry_path = (entry_point or "").strip() or "test_solution.py"
        entry_present = any(
            isinstance(entry, dict)
            and str(entry.get("path") or "").strip() == entry_path
            for entry in files
        )
        if not entry_present:
            found = [str(e.get("path") or "") for e in files if isinstance(e, dict)]
            raise ValueError(f"Entry point '{entry_path}' not found in files {found}")

        # Detect runner by scanning all files — for React, entry_point is the solution
        # file (e.g. "App.js"), not the test file, so we can't rely on entry_path alone.
        has_js_tests = any(
            str(e.get("path") or "")
            .strip()
            .endswith((".test.js", ".test.jsx", ".test.ts", ".test.tsx"))
            for e in files
            if isinstance(e, dict)
        )
        if has_js_tests:
            run_script = (
                "#!/usr/bin/env bash\n"
                "set -e\n"
                "export NODE_PATH=$(npm root -g)\n"
                "npx -y jest --no-coverage\n"
            )
        else:
            run_script = "#!/usr/bin/env bash\n" "set -e\n" "python3 -m pytest\n"

        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("run", run_script)
            for entry in files:
                if not isinstance(entry, dict):
                    continue
                path = str(entry.get("path") or "").strip()
                content = entry.get("content")
                if not path or not isinstance(content, str):
                    continue
                zf.writestr(path, content)

        return base64.b64encode(buffer.getvalue()).decode("ascii")

    def execute_multifile(
        self,
        *,
        files: list[dict[str, Any]],
        entry_point: str,
        problem_id: str | None = None,
        request_id: str | None = None,
    ) -> dict[str, Any]:
        additional_files = self._build_multifile_archive(
            files=files, entry_point=entry_point
        )

        payload: dict[str, Any] = {
            "language_id": 89,
            "additional_files": additional_files,
        }

        token_response = self._post_submission(payload)
        token = token_response.get("token")
        if not token:
            raise RuntimeError(
                "Judge0 did not return a submission token for multifile job"
            )

        logger.info(
            "Judge0 multifile submitted: problem=%s token=%s req=%s",
            problem_id,
            token,
            request_id,
        )
        result = self._poll_until_done(token, max_attempts=40, interval_seconds=1.0)

        normalized_status, normalized_error = map_status(result)
        status_obj = result.get("status")
        status = (
            status_obj
            if isinstance(status_obj, dict)
            else {"id": 0, "description": "Unknown"}
        )
        status_id = status.get("id")
        passed = status_id == 3

        logger.info(
            "Judge0 multifile done: problem=%s token=%s status=[%s]%s passed=%s req=%s",
            problem_id,
            token,
            status_id,
            status.get("description", ""),
            passed,
            request_id,
        )

        case_result = {
            "token": result.get("token"),
            "stdin": "",
            "expected_output": None,
            "stdout": result.get("stdout"),
            "stderr": result.get("stderr"),
            "compile_output": result.get("compile_output"),
            "message": result.get("message"),
            "status": status,
            "time": result.get("time"),
            "memory": result.get("memory"),
            "normalized_status": normalized_status,
            "normalized_error": normalized_error,
            "passed": passed,
        }

        try:
            seconds = float(case_result.get("time") or 0)
        except (TypeError, ValueError):
            seconds = 0
        total_millis = int(seconds * 1000)

        return {
            "passed": passed,
            "passed_tests": 1 if passed else 0,
            "total_tests": 1,
            "score": 100 if passed else 0,
            "time_taken": total_millis,
            "cases": [case_result],
        }

    # ------------------------------------------------------------------
    # Public single-file entry point
    # ------------------------------------------------------------------

    def execute(
        self,
        code: str,
        language_id: int,
        test_inputs: list[Any],
        setup_sql: str | None = None,
        problem_id: str | None = None,
        request_id: str | None = None,
    ) -> dict[str, Any]:
        if not isinstance(language_id, int) or language_id <= 0:
            raise ValueError(f"Invalid Judge0 language id: {language_id}")

        normalized_cases = test_inputs if test_inputs else [{"input": "", "output": ""}]
        case_results: list[dict[str, Any]] = []

        for case in normalized_cases:
            if isinstance(case, dict):
                stdin = str(case.get("input", ""))
                out_raw = case.get("output", "")
                if setup_sql and str(setup_sql).strip():
                    expected_output = (
                        None
                        if out_raw is None or not str(out_raw).strip()
                        else str(out_raw)
                    )
                else:
                    expected_output = "" if out_raw is None else str(out_raw)
            else:
                stdin = str(case)
                expected_output = None

            result = self._execute_one(
                code=code,
                language_id=language_id,
                stdin=stdin,
                expected_output=expected_output,
                setup_sql=setup_sql,
                problem_id=problem_id,
                request_id=request_id,
            )
            normalized_status, normalized_error = map_status(result)
            status_obj = result.get("status")
            status = (
                status_obj
                if isinstance(status_obj, dict)
                else {"id": 0, "description": "Unknown"}
            )
            status_id = status.get("id")
            stdout_value = result.get("stdout")
            stderr_value = result.get("stderr")
            if expected_output is None:
                passed = status_id == 3
            else:
                passed = (
                    status_id == 3
                    and (result.get("stdout") or "").strip()
                    == (expected_output or "").strip()
                )

            case_results.append(
                {
                    "token": result.get("token"),
                    "stdin": stdin,
                    "expected_output": expected_output,
                    "stdout": stdout_value,
                    "stderr": stderr_value,
                    "compile_output": result.get("compile_output"),
                    "message": result.get("message"),
                    "status": status,
                    "time": result.get("time"),
                    "memory": result.get("memory"),
                    "normalized_status": normalized_status,
                    "normalized_error": normalized_error,
                    "passed": passed,
                }
            )

        passed_count = sum(1 for item in case_results if item["passed"])
        total_tests = len(case_results)
        score = int((passed_count / total_tests) * 100) if total_tests > 0 else 0

        total_millis = 0
        for item in case_results:
            try:
                seconds = float(item.get("time") or 0)
            except (TypeError, ValueError):
                seconds = 0
            total_millis += int(seconds * 1000)

        logger.info(
            "Judge0 execute done: lang=%s problem=%s passed=%s/%s score=%s time_ms=%s req=%s",
            language_id,
            problem_id,
            passed_count,
            total_tests,
            score,
            total_millis,
            request_id,
        )
        return {
            "passed": passed_count == total_tests,
            "passed_tests": passed_count,
            "total_tests": total_tests,
            "score": score,
            "time_taken": total_millis,
            "cases": case_results,
        }

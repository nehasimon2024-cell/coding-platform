"""Session business logic — problem selection, execution, scoring, and DB writes.

Imported by ``app.routes.sessions`` which contains only the FastAPI route handlers.
"""
import json
import logging
import os
import random
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

import requests
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import (
    AssessmentSession,
    Badge,
    Level,
    Problem,
    QuestionType,
    SessionStatus,
    SessionViolation,
    Skill,
    Submission,
    SubmissionStatus,
    User,
    UserBadge,
    UserSkillProgress,
    ViolationType,
)
from app.judge0_service import Judge0Service
from app.schemas import SessionProblemPayload, ExecutionStatus

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ALLOWED_VIOLATION_TYPES = {
    "tab_switch",
    "window_blur",
    "tab_switch_shortcut",
    "fullscreen_exit",
    "paste",
    "paste_attempt",
    "copy",
    "cut",
    "select_all",
    "devtools_shortcut",
    "devtools",
    "devtools_open",
    "right_click",
    "unknown",
}

LEVEL_ORDER = [
    Level.BEGINNER,
    Level.INTERMEDIATE_1,
    Level.INTERMEDIATE_2,
    Level.SPECIALIST_1,
    Level.SPECIALIST_2,
]



# Judge0 client — one instance shared across all request handlers.
judge0_service = Judge0Service()

# ---------------------------------------------------------------------------
# Problem selection helpers
# ---------------------------------------------------------------------------


def preferred_difficulty_pair(level: Level) -> tuple[str, str]:
    return ("easy", "hard") if level == Level.BEGINNER else ("medium", "hard")


def _as_utc(dt: datetime) -> datetime:
    """Return *dt* as a UTC-aware datetime.

    DateTime(timezone=True) columns always yield tz-aware datetimes from SQLAlchemy,
    so the astimezone path is the common one; the fallback handles bare datetimes.
    """
    return dt.astimezone(timezone.utc) if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _redact_hidden_cases(cases: list[dict[str, Any]]) -> list[Any]:
    """Strip input/output from hidden test cases before sending to the frontend."""
    result: list[Any] = []
    for case in cases:
        if case.get("is_hidden"):
            result.append(
                {
                    "stdin": "",
                    "passed": case.get("passed", False),
                    "is_hidden": True,
                    "status": ExecutionStatus.SUCCESS if case.get("passed") else ExecutionStatus.WRONG_ANSWER,
                    "time": case.get("time"),
                    "memory": case.get("memory"),
                }
            )
        else:
            result.append(case)
    return result


def choose_two_problems(problems: list[Problem], level: Level) -> list[Problem]:
    if len(problems) < 2:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="At least 2 questions are required to start this assessment level",
        )

    grouped: dict[str, list[Problem]] = {}
    for problem in problems:
        difficulty = (problem.difficulty_label or "").strip().lower() or "unknown"
        grouped.setdefault(difficulty, []).append(problem)

    preferred_first, preferred_second = preferred_difficulty_pair(level)

    if len(grouped) >= 2:
        ordered_labels: list[str] = []
        for label in [
            preferred_first,
            preferred_second,
            "easy",
            "medium",
            "hard",
            *sorted(grouped.keys()),
        ]:
            if label in grouped and label not in ordered_labels:
                ordered_labels.append(label)

        first = random.choice(grouped[ordered_labels[0]])

        second_candidates: list[Problem] = []
        for label in ordered_labels[1:]:
            candidates = [p for p in grouped[label] if p.id != first.id]
            if candidates:
                second_candidates = candidates
                break

        if second_candidates:
            second = random.choice(second_candidates)
            return [first, second]

    sampled = random.sample(problems, 2)
    return [sampled[0], sampled[1]]


def build_question_set_payload(problem_ids: list[UUID]) -> str:
    return json.dumps(
        {
            "format": "multi_question_v1",
            "problem_ids": [str(pid) for pid in problem_ids],
        }
    )


def parse_question_ids(raw: str | None, primary_problem_id: UUID) -> list[UUID]:
    ordered_ids: list[UUID] = [primary_problem_id]
    if not raw:
        return ordered_ids

    try:
        parsed = json.loads(raw)
    except (TypeError, ValueError):
        return ordered_ids

    if not isinstance(parsed, dict) or parsed.get("format") != "multi_question_v1":
        return ordered_ids

    values = parsed.get("problem_ids")
    if not isinstance(values, list):
        return ordered_ids

    for value in values:
        try:
            parsed_id = UUID(str(value))
        except (TypeError, ValueError):
            continue
        if parsed_id not in ordered_ids:
            ordered_ids.append(parsed_id)
        if len(ordered_ids) >= 2:
            break

    return ordered_ids


# ---------------------------------------------------------------------------
# Payload / template helpers
# ---------------------------------------------------------------------------


def resolve_multifile_template_code(starter_code: Any) -> str | None:
    if not isinstance(starter_code, dict):
        return None

    files = starter_code.get("files")
    if not isinstance(files, list):
        return None

    readonly = starter_code.get("readonly_files")
    readonly_set = {str(p) for p in readonly} if isinstance(readonly, list) else set()

    def read_file_content(target_path: str) -> str | None:
        for entry in files:
            if not isinstance(entry, dict):
                continue
            if str(entry.get("path") or "").strip() == target_path:
                content = entry.get("content")
                return content if isinstance(content, str) else None
        return None

    preferred = read_file_content("solution.py")
    if preferred:
        return preferred

    for entry in files:
        if not isinstance(entry, dict):
            continue
        path = str(entry.get("path") or "").strip()
        if not path or path in readonly_set:
            continue
        content = entry.get("content")
        if isinstance(content, str):
            return content

    for entry in files:
        if not isinstance(entry, dict):
            continue
        content = entry.get("content")
        if isinstance(content, str):
            return content

    return None


def resolve_template_code(starter_code: object) -> str | None:
    if isinstance(starter_code, dict):
        for key in ("python", "default", "javascript", "java"):
            value = starter_code.get(key)
            if isinstance(value, str) and value.strip():
                return value
        for value in starter_code.values():
            if isinstance(value, str) and value.strip():
                return value
        return None
    if isinstance(starter_code, str) and starter_code.strip():
        return starter_code
    return None


def build_problem_payload(problem: Problem) -> SessionProblemPayload:
    is_sql_problem = problem.question_type == QuestionType.SQL
    is_framework_problem = problem.question_type == QuestionType.FRAMEWORK

    if is_sql_problem:
        schema_tables = [
            entry
            for entry in (problem.database_schema or [])
            if isinstance(entry, dict)
            and entry.get("table")
            and isinstance(entry.get("columns"), list)
        ]
    else:
        schema_tables = []

    if is_sql_problem:
        template_code = None
        sanitized_starter = None
    elif is_framework_problem:
        sanitized_starter = problem.starter_code if isinstance(problem.starter_code, dict) else None
        template_code = None
        if isinstance(problem.starter_files, list) and problem.starter_files:
            first_file = problem.starter_files[0]
            if isinstance(first_file, dict):
                val = first_file.get("content")
                if isinstance(val, str):
                    template_code = val
    else:
        sanitized_starter = problem.starter_code if isinstance(problem.starter_code, dict) else None
        template_code = resolve_multifile_template_code(
            sanitized_starter
        ) or resolve_template_code(sanitized_starter or problem.starter_code)

    # SQL problems expose no sample test cases to the frontend (setup SQL is hidden).
    sanitized_samples: list = [] if is_sql_problem else list(problem.sample_test_cases or [])

    return SessionProblemPayload(
        problem_id=problem.id,
        title=problem.title,
        description=problem.description,
        templateCode=template_code,
        starter_code=sanitized_starter,
        tags=[str(tag) for tag in (problem.tags or [])],
        sample_test_cases=sanitized_samples,
        time_limit_minutes=problem.time_limit_minutes,
        schema_tables=schema_tables,
        question_type=problem.question_type,
        options=problem.options,
        starter_files=problem.starter_files,
        entry_point=problem.entry_point,
        test_harness=problem.test_harness,
        database_schema=problem.database_schema,
    )


# ---------------------------------------------------------------------------
# Session resolution helpers
# ---------------------------------------------------------------------------


def get_session_problem_set(db: Session, session_obj: AssessmentSession) -> list[Problem]:
    ordered_ids = parse_question_ids(session_obj.last_draft_code, session_obj.problem_id)

    # Single IN query instead of N individual SELECTs.
    rows = db.scalars(select(Problem).where(Problem.id.in_(ordered_ids))).all()
    by_id = {p.id: p for p in rows}

    resolved = [
        by_id[pid]
        for pid in ordered_ids
        if pid in by_id
        and by_id[pid].skill_id == session_obj.skill_id
        and by_id[pid].level == session_obj.level
    ]

    if not resolved:
        # Fallback: return the primary problem even if skill/level check fails
        # (defensive; in practice this branch shouldn't be reached).
        primary = by_id.get(session_obj.problem_id)
        if primary is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")
        resolved.append(primary)

    return resolved


def resolve_problem_from_session(
    db: Session,
    session_obj: AssessmentSession,
    requested_problem_id: UUID | None,
) -> Problem:
    problems = get_session_problem_set(db, session_obj)
    if requested_problem_id is None:
        return problems[0]

    for problem in problems:
        if problem.id == requested_problem_id:
            return problem

    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="Problem is not part of this session",
    )


def load_problem_for_session_run(
    db: Session,
    session_obj: AssessmentSession,
    requested_problem_id: UUID | None,
) -> Problem:
    """Load the Problem row for POST /sessions/.../run.

    Multi-question sessions must send ``problem_id`` so the correct SQL setup
    is matched to the active editor tab.
    """
    allowed = get_session_problem_set(db, session_obj)
    if not allowed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")

    if len(allowed) >= 2:
        if requested_problem_id is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="problem_id is required when the session has multiple questions",
            )
        target_id = requested_problem_id
    elif requested_problem_id is not None:
        target_id = requested_problem_id
        if not any(p.id == target_id for p in allowed):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Problem is not part of this session",
            )
    else:
        target_id = allowed[0].id

    problem = db.scalar(select(Problem).where(Problem.id == target_id))
    if problem is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")
    if not any(p.id == problem.id for p in allowed):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Problem is not part of this session",
        )
    return problem


def ensure_session_owner(session_obj: AssessmentSession, current_user: User) -> None:
    if session_obj.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Session does not belong to current user",
        )


def log_violation(
    db: Session,
    session_obj: AssessmentSession,
    violation_type: ViolationType,
    metadata: dict[str, Any] | None = None,
) -> None:
    violation = SessionViolation(
        session_id=session_obj.id,
        user_id=session_obj.user_id,
        type=violation_type,
        metadata_=metadata,
    )
    db.add(violation)
    db.commit()


def resolve_language_from_skill(
    language: str, allowed_languages: list[Any]
) -> tuple[str, int]:
    requested = (language or "").strip().lower()
    if not requested:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Language is required",
        )

    for item in allowed_languages or []:
        if not isinstance(item, dict):
            continue
        lang_id = item.get("id")
        monaco = str(item.get("monaco") or "").strip().lower()
        name = str(item.get("name") or "").strip().lower()
        if lang_id is None:
            continue
        if (
            requested == monaco
            or requested == name
            or requested == str(lang_id).strip().lower()
        ):
            try:
                return (monaco or requested), int(lang_id)
            except (TypeError, ValueError):
                continue

    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="Selected language is not allowed for this skill",
    )


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------


def build_framework_payload_files(
    problem: Problem,
    updated_solution: str,
) -> list[dict[str, Any]]:
    payload_files: list[dict[str, Any]] = []

    files = problem.starter_files if isinstance(problem.starter_files, list) else []
    for i, entry in enumerate(files):
        if not isinstance(entry, dict):
            continue
        path = str(entry.get("path") or "").strip()
        content = entry.get("content")
        if not path:
            continue
        if i == 0:
            payload_files.append({"path": path, "content": updated_solution})
            continue
        if isinstance(content, str):
            payload_files.append({"path": path, "content": content})

    # Inject the test harness only when it contains actual code content.
    # For FastAPI-style problems: test_harness holds the full pytest source → inject at entry_point.
    # For React-style problems: test_harness is just a filename (e.g. "App.test.jsx") already
    # present in starter_files → skip to avoid overwriting it with a bare path string.
    harness = str(problem.test_harness or "").strip()
    entry_point = str(problem.entry_point or "test_main.py").strip() or "test_main.py"
    if harness:
        existing_paths = {
            str(f.get("path") or "").strip()
            for f in payload_files
            if isinstance(f, dict)
        }
        harness_is_path_ref = "\n" not in harness and harness in existing_paths
        if not harness_is_path_ref:
            payload_files.append({"path": entry_point, "content": harness})
    else:
        logger.warning(
            "No test_harness for problem %s — multifile execution will likely fail",
            problem.id,
        )

    return payload_files


def execute_problem(
    problem: Problem,
    skill: Skill,
    code: str,
    language: str,
    *,
    use_hidden_cases: bool,
) -> dict[str, Any]:
    if problem.question_type == "mcq":
        selected_index_str = (code or "").strip()
        passed = False
        try:
            if selected_index_str and problem.correct_option_index is not None:
                passed = int(selected_index_str) == problem.correct_option_index
        except ValueError:
            pass

        score = 100 if passed else 0
        case = {
            "stdin": selected_index_str,
            "expected_output": (
                str(problem.correct_option_index)
                if problem.correct_option_index is not None
                else ""
            ),
            "stdout": selected_index_str,
            "stderr": None,
            "compile_output": None,
            "status": ExecutionStatus.SUCCESS if passed else ExecutionStatus.WRONG_ANSWER,
            "passed": passed,
            "time": "0",
            "memory": "0",
        }
        return {
            "resolved_monaco": (language or "mcq").strip().lower() or "mcq",
            "passed": passed,
            "passed_tests": 1 if passed else 0,
            "total_tests": 1,
            "score": score,
            "time_taken": 0,
            "cases": [case],
        }

    resolved_monaco, resolved_language_id = resolve_language_from_skill(
        language, skill.allowed_languages or []
    )

    sample_cases_list = list(problem.sample_test_cases or [])
    hidden_cases_list = list(problem.hidden_test_cases or []) if use_hidden_cases else []
    test_inputs = sample_cases_list + hidden_cases_list if use_hidden_cases else sample_cases_list
    sample_count = len(sample_cases_list)

    is_sql = problem.question_type == QuestionType.SQL
    is_framework = problem.question_type == QuestionType.FRAMEWORK
    setup_snapshot = ""

    if is_framework:
        request_id = uuid4().hex[:8]
        files = build_framework_payload_files(problem, code)
        entry = str(problem.entry_point or "test_main.py").strip()
        effective_entry = entry if entry else "test_main.py"

        execution_result = judge0_service.execute_multifile(
            files=files,
            entry_point=effective_entry,
            problem_id=str(problem.id),
            request_id=request_id,
        )

        cases: list[Any] = list(execution_result.get("cases") or [])
        return {
            "resolved_monaco": resolved_monaco,
            "score": int(execution_result.get("score", 0)),
            "passed_tests": int(execution_result.get("passed_tests", 0)),
            "total_tests": int(execution_result.get("total_tests", 0)),
            "time_taken": int(execution_result.get("time_taken", 0)),
            "cases": cases,
            "is_sql_execution": False,
        }

    if is_sql:
        # Signal SQL mode by passing an empty string (not None).
        # judge0_service.execute() will use each test case's own "input"
        # field as the per-case DDL setup, so hidden cases with different
        # seed data work correctly without extra coupling here.
        setup_snapshot = ""

    request_id = uuid4().hex[:8]

    try:
        if resolved_monaco in ("html_css_js", "html", "css", "javascript_web"):
            cases = [
                {
                    "stdin": str(case.get("input", "")),
                    "expected_output": str(case.get("output", "")),
                    "stdout": "Pending AI feedback",
                    "stderr": None,
                    "compile_output": None,
                    "message": None,
                    "status": ExecutionStatus.SUCCESS,
                    "time": "0",
                    "memory": None,
                    "passed": True,
                }
                for case in (test_inputs or [])
                if isinstance(case, dict)
            ]
            execution_result = {
                "score": 100,
                "passed_tests": len(cases),
                "total_tests": len(cases),
                "time_taken": 0,
                "cases": cases,
            }
        else:
            execution_result = judge0_service.execute(
                code=code,
                language_id=resolved_language_id,
                test_inputs=test_inputs or [],
                setup_sql=setup_snapshot if is_sql else None,
                problem_id=str(problem.id),
                request_id=request_id,
            )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    except (requests.RequestException, TimeoutError, RuntimeError) as exc:
        logger.error("Judge0 execution failed: problem=%s error=%s", problem.id, exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Judge0 execution failed: {str(exc)}",
        ) from exc
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Unexpected execution error: problem=%s", problem.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Execution failed: {str(exc)}",
        ) from exc

    cases: list[Any] = list(execution_result.get("cases") or [])

    for idx, case in enumerate(cases):
        if isinstance(case, dict):
            case["is_hidden"] = idx >= sample_count

    sql_stdout: str | None = None
    if is_sql and cases and isinstance(cases[0], dict):
        raw = cases[0].get("stdout")
        sql_stdout = None if raw is None else str(raw)

    out: dict[str, Any] = {
        "resolved_monaco": resolved_monaco,
        "score": int(execution_result.get("score", 0)),
        "passed_tests": int(execution_result.get("passed_tests", 0)),
        "total_tests": int(execution_result.get("total_tests", 0)),
        "time_taken": int(execution_result.get("time_taken", 0)),
        "cases": cases,
        "is_sql_execution": is_sql,
        "sample_count": sample_count,
    }
    if is_sql:
        out["stdout"] = sql_stdout
        out["expected_output"] = None
    return out


def _compute_overall_status(cases: list[dict[str, Any]]) -> ExecutionStatus:
    statuses = [
        case.get("status")
        for case in cases
    ]
    if any(s == ExecutionStatus.COMPILE_ERROR for s in statuses):
        return ExecutionStatus.COMPILE_ERROR
    if any(s == ExecutionStatus.RUNTIME_ERROR for s in statuses):
        return ExecutionStatus.RUNTIME_ERROR
    if any(s == ExecutionStatus.TIME_LIMIT_EXCEEDED for s in statuses):
        return ExecutionStatus.TIME_LIMIT_EXCEEDED
    if any(s == ExecutionStatus.WRONG_ANSWER for s in statuses):
        return ExecutionStatus.WRONG_ANSWER
    if statuses and all(s == ExecutionStatus.SUCCESS for s in statuses):
        return ExecutionStatus.SUCCESS
    return ExecutionStatus.WRONG_ANSWER


# ---------------------------------------------------------------------------
# Scoring, badges, progress
# ---------------------------------------------------------------------------


def get_max_attempts() -> int:
    try:
        return int(os.getenv("MAX_ATTEMPTS_PER_LEVEL", "5"))
    except ValueError:
        return 5


def get_pass_threshold() -> int:
    try:
        return int(os.getenv("SCORE_PASS_THRESHOLD", "70"))
    except ValueError:
        return 70


def get_next_level(level: Level) -> Level | None:
    index = LEVEL_ORDER.index(level)
    if index + 1 >= len(LEVEL_ORDER):
        return None
    return LEVEL_ORDER[index + 1]


def award_level_badge(
    db: Session,
    *,
    user_id: UUID,
    skill: Skill,
    level: Level,
    awarded_at: datetime,
) -> None:
    level_label = level.value
    badge_name = f"{skill.name} - {level_label} Cleared"
    description = f"Awarded for clearing {level_label} level in {skill.name}."
    criteria = json.dumps(
        {
            "event": "level_cleared",
            "skill_id": str(skill.id),
            "skill_name": skill.name,
            "level": level.value,
        }
    )

    badge = db.scalar(select(Badge).where(Badge.name == badge_name))
    if badge is None:
        badge = Badge(name=badge_name, description=description, criteria=criteria)
        db.add(badge)
        db.flush()

    existing_award = db.scalar(
        select(UserBadge).where(
            UserBadge.user_id == user_id,
            UserBadge.badge_id == badge.id,
        )
    )
    if existing_award is None:
        db.add(UserBadge(user_id=user_id, badge_id=badge.id, awarded_at=awarded_at))


def score_submission(
    db: Session,
    session_obj: AssessmentSession,
    code: str,
    language: str,
    forced_status: SubmissionStatus | None = None,
) -> Submission:
    already_submitted = db.scalar(
        select(func.count(Submission.id)).where(Submission.session_id == session_obj.id)
    )
    if already_submitted:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Session already submitted"
        )

    problem = resolve_problem_from_session(db, session_obj, None)
    skill = session_obj.skill

    execution_result = execute_problem(
        problem=problem,
        skill=skill,
        code=code,
        language=language,
        use_hidden_cases=True,
    )

    score = int(execution_result.get("score", 0))
    passed_tests = int(execution_result.get("passed_tests", 0))
    total_tests = int(execution_result.get("total_tests", 0))

    default_status = (
        SubmissionStatus.CLEARED if score >= get_pass_threshold() else SubmissionStatus.FAILED
    )
    submission_status = forced_status or default_status

    current_time = datetime.now(timezone.utc)
    started_at = _as_utc(session_obj.started_at)
    time_taken_seconds = max(0, int((current_time - started_at).total_seconds()))

    submission = Submission(
        session_id=session_obj.id,
        user_id=session_obj.user_id,
        problem_id=session_obj.problem_id,
        skill_id=session_obj.skill_id,
        level=session_obj.level,
        code=code,
        language=execution_result["resolved_monaco"],
        status=submission_status,
        score=score,
        passed_tests=passed_tests,
        total_tests=total_tests,
        time_taken_seconds=time_taken_seconds,
        judge_result={"cases": execution_result.get("cases", [])},
    )
    db.add(submission)

    if submission_status == SubmissionStatus.TIMED_OUT:
        session_obj.status = SessionStatus.TIMED_OUT
        session_obj.submitted_at = current_time
    else:
        session_obj.status = SessionStatus.SUBMITTED
        session_obj.submitted_at = current_time

    if submission_status == SubmissionStatus.CLEARED:
        progress = db.scalar(
            select(UserSkillProgress).where(
                UserSkillProgress.user_id == session_obj.user_id,
                UserSkillProgress.skill_id == session_obj.skill_id,
                UserSkillProgress.level == session_obj.level,
            )
        )
        if progress is None:
            progress = UserSkillProgress(
                user_id=session_obj.user_id,
                skill_id=session_obj.skill_id,
                level=session_obj.level,
                unlocked=True,
                cleared=True,
                cleared_at=current_time,
            )
            db.add(progress)
        else:
            progress.unlocked = True
            progress.cleared = True
            progress.cleared_at = current_time

        next_level = get_next_level(session_obj.level)
        if next_level is not None:
            next_progress = db.scalar(
                select(UserSkillProgress).where(
                    UserSkillProgress.user_id == session_obj.user_id,
                    UserSkillProgress.skill_id == session_obj.skill_id,
                    UserSkillProgress.level == next_level,
                )
            )
            if next_progress is None:
                next_progress = UserSkillProgress(
                    user_id=session_obj.user_id,
                    skill_id=session_obj.skill_id,
                    level=next_level,
                    unlocked=True,
                    cleared=False,
                )
                db.add(next_progress)
            else:
                next_progress.unlocked = True

        award_level_badge(
            db,
            user_id=session_obj.user_id,
            skill=skill,
            level=session_obj.level,
            awarded_at=current_time,
        )

    return submission

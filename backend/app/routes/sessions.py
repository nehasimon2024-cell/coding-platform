import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.dependencies import require_candidate
from app.db.models import (
    AssessmentSession,
    Level,
    Problem,
    SessionStatus,
    SessionViolation,
    Skill,
    Submission,
    SubmissionStatus,
    User,
    UserSkillProgress,
    ViolationType,
)
from app.schemas import (
    SessionDetailResponse,
    SessionDraftRequest,
    SessionDraftResponse,
    SessionRunRequest,
    SessionRunResponse,
    SessionStartRequest,
    SessionStartResponse,
    SessionSubmitRequest,
    SessionSubmitResponse,
    ViolationCreate,
)
from app.services.session_service import (
    _as_utc,
    _compute_overall_status,
    _redact_hidden_cases,
    award_level_badge,
    build_problem_payload,
    build_question_set_payload,
    choose_two_problems,
    ensure_session_owner,
    execute_problem,
    get_max_attempts,
    get_next_level,
    get_pass_threshold,
    get_session_problem_set,
    load_problem_for_session_run,
    resolve_problem_from_session,
    score_submission,
)

router = APIRouter(tags=["sessions"])
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# POST /sessions/start
# ---------------------------------------------------------------------------


@router.post(
    "/sessions/start",
    response_model=SessionStartResponse,
    status_code=status.HTTP_201_CREATED,
)
def start_session(
    payload: SessionStartRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_candidate),
) -> SessionStartResponse:
    skill = db.scalar(select(Skill).where(Skill.id == payload.skill_id))
    if skill is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found"
        )

    progress = db.scalar(
        select(UserSkillProgress).where(
            UserSkillProgress.user_id == current_user.id,
            UserSkillProgress.skill_id == payload.skill_id,
            UserSkillProgress.level == payload.level,
        )
    )
    if progress is None:
        progress = UserSkillProgress(
            user_id=current_user.id,
            skill_id=payload.skill_id,
            level=payload.level,
            unlocked=payload.level == Level.BEGINNER,
            cleared=False,
        )
        db.add(progress)
        db.flush()

    if not progress.unlocked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Level is locked"
        )

    attempts_used = (
        db.scalar(
            select(func.count(AssessmentSession.id)).where(
                AssessmentSession.user_id == current_user.id,
                AssessmentSession.skill_id == payload.skill_id,
                AssessmentSession.level == payload.level,
            )
        )
        or 0
    )
    max_attempts = get_max_attempts()
    if int(attempts_used) >= max_attempts:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Max attempts reached"
        )

    problems = db.scalars(
        select(Problem).where(
            Problem.skill_id == payload.skill_id, Problem.level == payload.level
        )
    ).all()
    if not problems:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found"
        )

    selected_problems = choose_two_problems(problems, payload.level)
    selected_problem = selected_problems[0]
    started = datetime.now(timezone.utc)
    expires_at = started + timedelta(minutes=selected_problem.time_limit_minutes)

    session_obj = AssessmentSession(
        user_id=current_user.id,
        problem_id=selected_problem.id,
        skill_id=payload.skill_id,
        level=payload.level,
        status=SessionStatus.ACTIVE,
        started_at=started,
        expires_at=expires_at,
        attempt_number=int(attempts_used) + 1,
        last_draft_code=build_question_set_payload([p.id for p in selected_problems]),
    )

    try:
        db.add(session_obj)
        db.commit()
        db.refresh(session_obj)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create session",
        ) from exc

    attempts_remaining = max(0, max_attempts - session_obj.attempt_number)
    return SessionStartResponse(
        session_id=session_obj.id,
        problem_id=selected_problem.id,
        expires_at=_as_utc(session_obj.expires_at),
        attempt_number=session_obj.attempt_number,
        attempts_remaining=attempts_remaining,
        problem=build_problem_payload(selected_problem),
        problems=[build_problem_payload(p) for p in selected_problems],
        allowed_languages=skill.allowed_languages or [],
    )


@router.get("/sessions/{session_id}", response_model=SessionDetailResponse)
def get_session(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_candidate),
) -> SessionDetailResponse:
    session_obj = db.scalar(
        select(AssessmentSession).where(AssessmentSession.id == session_id)
    )
    if session_obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )
    ensure_session_owner(session_obj, current_user)

    current_time = datetime.now(timezone.utc)
    expires_at = _as_utc(session_obj.expires_at)
    if session_obj.status == SessionStatus.ACTIVE and expires_at <= current_time:
        session_obj.status = SessionStatus.TIMED_OUT
        db.commit()

    seconds_remaining = max(0, int((expires_at - current_time).total_seconds()))
    problems = get_session_problem_set(db, session_obj)
    primary_problem = problems[0]
    skill = session_obj.skill

    return SessionDetailResponse(
        session_id=session_obj.id,
        status=session_obj.status,
        expires_at=expires_at,
        seconds_remaining=seconds_remaining,
        problem=build_problem_payload(primary_problem),
        problems=[build_problem_payload(p) for p in problems],
        allowed_languages=skill.allowed_languages or [],
        last_draft_code=session_obj.last_draft_code,
        last_draft_lang=session_obj.last_draft_lang,
    )


@router.post("/sessions/{session_id}/draft", response_model=SessionDraftResponse)
def save_draft(
    session_id: UUID,
    payload: SessionDraftRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_candidate),
) -> SessionDraftResponse:
    session_obj = db.scalar(
        select(AssessmentSession).where(AssessmentSession.id == session_id)
    )
    if session_obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )
    ensure_session_owner(session_obj, current_user)

    if session_obj.status not in (SessionStatus.ACTIVE, SessionStatus.SUBMITTED):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Session is not active"
        )

    session_obj.last_draft_code = payload.code
    session_obj.last_draft_lang = payload.language
    session_obj.draft_saved_at = datetime.now(timezone.utc)
    db.commit()

    return SessionDraftResponse(saved_at=session_obj.draft_saved_at)


@router.post("/sessions/{session_id}/violation")
def log_violation(
    session_id: UUID,
    payload: ViolationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_candidate),
) -> dict[str, str]:
    session_obj = db.scalar(
        select(AssessmentSession).where(AssessmentSession.id == session_id)
    )
    if session_obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )
    ensure_session_owner(session_obj, current_user)

    violation_type = payload.type

    now_utc = datetime.now(timezone.utc)
    try:
        client_time = payload.timestamp
    except Exception:
        client_time = None

    final_time = now_utc
    if isinstance(client_time, datetime):
        if client_time.tzinfo is None:
            client_time = client_time.replace(tzinfo=timezone.utc)
        try:
            drift_seconds = abs(
                (now_utc - client_time.astimezone(timezone.utc)).total_seconds()
            )
            if drift_seconds <= 300:
                final_time = client_time.astimezone(timezone.utc)
        except Exception:
            final_time = now_utc

    dedupe_since = now_utc - timedelta(seconds=2)
    existing = db.scalar(
        select(SessionViolation).where(
            SessionViolation.session_id == session_obj.id,
            SessionViolation.type == violation_type,
            SessionViolation.timestamp >= dedupe_since,
        )
    )
    if existing is not None:
        return {"status": "duplicate_skipped"}

    try:
        violation = SessionViolation(
            session_id=session_obj.id,
            user_id=current_user.id,
            type=violation_type,
            timestamp=final_time,
            metadata_=payload.metadata,
        )
        db.add(violation)
        db.commit()
        return {"status": "logged"}
    except SQLAlchemyError as exc:
        db.rollback()
        logger.warning(
            "Failed to log violation: session_id=%s user_id=%s type=%s error=%s",
            session_id,
            current_user.id,
            violation_type,
            exc,
        )
        return {"status": "failed"}
    except Exception as exc:
        db.rollback()
        logger.warning(
            "Unexpected violation logging failure: session_id=%s user_id=%s type=%s error=%s",
            session_id,
            current_user.id,
            violation_type,
            exc,
        )
        return {"status": "failed"}



@router.post("/sessions/{session_id}/submit", response_model=SessionSubmitResponse)
def submit_session(
    session_id: UUID,
    payload: SessionSubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_candidate),
) -> SessionSubmitResponse:
    logger.info(
        "POST /submit session=%s lang=%s user=%s",
        session_id,
        payload.language,
        current_user.id,
    )
    session_obj = db.scalar(
        select(AssessmentSession).where(AssessmentSession.id == session_id)
    )
    if session_obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )
    ensure_session_owner(session_obj, current_user)

    prior_submissions = int(
        db.scalar(
            select(func.count(Submission.id)).where(Submission.session_id == session_id)
        )
        or 0
    )

    current_time = datetime.now(timezone.utc)
    expires_at = _as_utc(session_obj.expires_at)
    answer_items = payload.answers or []
    if expires_at <= current_time:
        try:
            score_submission(
                db=db,
                session_obj=session_obj,
                code=payload.code,
                language=payload.language,
                forced_status=SubmissionStatus.TIMED_OUT,
            )
            db.commit()
        except SQLAlchemyError as exc:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to persist submission",
            ) from exc
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"status": "expired", "message": "Session has expired"},
        )

    try:
        if answer_items:
            skill = session_obj.skill

            session_problem_set = get_session_problem_set(db, session_obj)
            allowed_problem_ids = {p.id for p in session_problem_set}
            deduped_answers: list[tuple[Problem, str, str]] = []
            seen_problem_ids: set[UUID] = set()

            for answer in answer_items:
                if answer.problem_id in seen_problem_ids:
                    continue
                if answer.problem_id not in allowed_problem_ids:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail="Answer contains an invalid problem",
                    )
                # Use the already-loaded set — avoids re-running get_session_problem_set
                # per answer (which would be 1 extra IN query per resolve call).
                problem = next((p for p in session_problem_set if p.id == answer.problem_id), None)
                if problem is None:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail="Problem not found in session",
                    )
                deduped_answers.append((problem, answer.code, answer.language))
                seen_problem_ids.add(answer.problem_id)

            if len(deduped_answers) < 2:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Please submit solutions for both questions",
                )

            executions = [
                execute_problem(
                    problem=problem,
                    skill=skill,
                    code=code,
                    language=language,
                    use_hidden_cases=True,
                )
                for problem, code, language in deduped_answers
            ]

            score = int(round(sum(e["score"] for e in executions) / len(executions)))
            passed_tests = int(sum(e["passed_tests"] for e in executions))
            total_tests = int(sum(e["total_tests"] for e in executions))
            merged_cases: list[Any] = []
            for execution in executions:
                merged_cases.extend(execution.get("cases", []))

            submission_status = (
                SubmissionStatus.CLEARED
                if score >= get_pass_threshold()
                else SubmissionStatus.FAILED
            )
            started_at = _as_utc(session_obj.started_at)
            time_taken_seconds = max(
                0, int((datetime.now(timezone.utc) - started_at).total_seconds())
            )

            primary_execution = executions[0]
            combined_code = json.dumps(
                [
                    {"problem_id": str(problem.id), "code": code, "language": language}
                    for problem, code, language in deduped_answers
                ]
            )

            submission = Submission(
                session_id=session_obj.id,
                user_id=session_obj.user_id,
                problem_id=session_obj.problem_id,
                skill_id=session_obj.skill_id,
                level=session_obj.level,
                code=combined_code,
                language=primary_execution["resolved_monaco"],
                status=submission_status,
                score=score,
                passed_tests=passed_tests,
                total_tests=total_tests,
                time_taken_seconds=time_taken_seconds,
                judge_result={"cases": merged_cases},
            )
            db.add(submission)

            session_obj.status = SessionStatus.SUBMITTED
            session_obj.submitted_at = datetime.now(timezone.utc)

            if submission_status == SubmissionStatus.CLEARED:
                current_time = datetime.now(timezone.utc)
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
                    awarded_at=datetime.now(timezone.utc),
                )
        else:
            submission = score_submission(
                db=db,
                session_obj=session_obj,
                code=payload.code,
                language=payload.language,
            )

        db.commit()
        db.refresh(submission)
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("Submit DB error: session=%s", session_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to persist submission: {str(exc)}",
        ) from exc
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        logger.exception("Submit unexpected error: session=%s", session_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Submit failed: {str(exc)}",
        ) from exc

    raw_cases = (
        submission.judge_result.get("cases", [])
        if isinstance(submission.judge_result, dict)
        else []
    )
    normalized_cases = [case for case in raw_cases if isinstance(case, dict)]
    sanitized_cases = _redact_hidden_cases(normalized_cases)

    response_payload = SessionSubmitResponse(
        submission_id=submission.id,
        session_id=session_obj.id,
        status=submission.status,
        score=submission.score,
        passed_tests=submission.passed_tests,
        total_tests=submission.total_tests,
        time_taken_seconds=submission.time_taken_seconds,
        cases=sanitized_cases,
    )
    logger.info(
        "Submit done: session=%s submission=%s status=%s score=%s passed=%s/%s attempt=%s",
        session_id,
        response_payload.submission_id,
        response_payload.status,
        submission.score,
        response_payload.passed_tests,
        response_payload.total_tests,
        prior_submissions + 1,
    )
    return response_payload


@router.post(
    "/sessions/{session_id}/run",
    response_model=SessionRunResponse,
)
def run_session_code(
    session_id: UUID,
    payload: SessionRunRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_candidate),
) -> SessionRunResponse:
    session_obj = db.scalar(
        select(AssessmentSession).where(AssessmentSession.id == session_id)
    )
    if session_obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )
    ensure_session_owner(session_obj, current_user)

    current_time = datetime.now(timezone.utc)
    expires_at = _as_utc(session_obj.expires_at)
    if expires_at <= current_time:
        session_obj.status = SessionStatus.TIMED_OUT
        db.commit()
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"status": "expired", "message": "Session has expired"},
        )

    problem = load_problem_for_session_run(db, session_obj, payload.problem_id)
    skill = session_obj.skill

    try:
        execution_result = execute_problem(
            problem=problem,
            skill=skill,
            code=payload.code,
            language=payload.language,
            use_hidden_cases=payload.use_hidden,
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(
            "Run unexpected error: session=%s problem=%s",
            session_id,
            payload.problem_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Run failed: {str(exc)}",
        ) from exc

    raw_cases = execution_result.get("cases", [])
    normalized_cases = [case for case in raw_cases if isinstance(case, dict)]
    overall_status = _compute_overall_status(normalized_cases)

    cases_for_response = _redact_hidden_cases(normalized_cases)

    payload_kwargs: dict[str, Any] = {
        "cases": cases_for_response,
        "time_taken_ms": int(execution_result.get("time_taken", 0)),
        "sql_run": bool(execution_result.get("is_sql_execution")),
        "overall_status": overall_status,
    }
    if "stdout" in execution_result:
        payload_kwargs["stdout"] = execution_result["stdout"]
    if "expected_output" in execution_result:
        payload_kwargs["expected_output"] = execution_result["expected_output"]

    response_payload = SessionRunResponse(**payload_kwargs)
    logger.info(
        "Run done: session=%s problem=%s status=%s cases=%s time_ms=%s",
        session_id,
        payload.problem_id,
        overall_status,
        len(response_payload.cases),
        response_payload.time_taken_ms,
    )
    return response_payload

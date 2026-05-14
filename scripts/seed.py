import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS_DIR.parent
BACKEND_DIR = REPO_ROOT / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Load backend .env so DATABASE_URL etc. are available before importing app modules
from dotenv import load_dotenv  

load_dotenv(dotenv_path=BACKEND_DIR / ".env", override=False)

from app.db.database import get_session_local  
from app.db.models import (  
    Base,
    Difficulty,
    Level,
    Problem,
    Skill,
    User,
    UserRole,
    UserSkillProgress,
)
from app.security import hash_password  

LEVEL_ORDER = [
    Level.BEGINNER,
    Level.INTERMEDIATE_1,
    Level.INTERMEDIATE_2,
    Level.SPECIALIST_1,
    Level.SPECIALIST_2,
]

CANONICAL_LEVEL_KEYS = {
    "Beginner": Level.BEGINNER,
    "Intermediate_1": Level.INTERMEDIATE_1,
    "Intermediate_2": Level.INTERMEDIATE_2,
    "Specialist_1": Level.SPECIALIST_1,
    "Specialist_2": Level.SPECIALIST_2,
}

CANONICAL_DIFFICULTIES = [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]

DEFAULT_JSON_FILE = SCRIPTS_DIR / "problem_dataset_new.json"


def to_str(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def resolve_allowed_languages(skill_obj: dict[str, Any]) -> list[dict[str, Any]]:
    return skill_obj.get("allowed_languages", [])


def create_user(
    db,
    email: str,
    password: str,
    role: UserRole,
    name: str,
    employee_id: str,
    gender: str,
    department: str,
    exp_indium_years: int,
    exp_overall_years: int,
) -> User:
    user = User(
        email=email,
        password_hash=hash_password(password),
        role=role,
        name=name,
        employee_id=employee_id,
        gender=gender,
        department=department,
        exp_indium_years=exp_indium_years,
        exp_overall_years=exp_overall_years,
    )
    db.add(user)
    db.flush()
    return user


def create_skills_from_payload(db, skills_payload: list[dict[str, Any]]) -> list[Skill]:
    skills: list[Skill] = []
    for skill_obj in skills_payload:
        skill_name = to_str(skill_obj.get("skill"))
        if not skill_name:
            continue

        skill = Skill(
            name=skill_name,
            description=to_str(skill_obj.get("description"))
            or "Imported from seed JSON",
            allowed_languages=resolve_allowed_languages(skill_obj),
        )
        db.add(skill)
        skills.append(skill)

    db.flush()
    return skills


def create_progress_for_candidate(db, user: User, skills: list[Skill]) -> int:
    inserted = 0
    for skill in skills:
        for level in LEVEL_ORDER:
            progress = UserSkillProgress(
                user_id=user.id,
                skill_id=skill.id,
                level=level,
                unlocked=(level == Level.BEGINNER),
                cleared=False,
                cleared_at=None,
            )
            db.add(progress)
            inserted += 1
    return inserted


def seed_problems_from_payload(
    db,
    skills_by_name: dict[str, Skill],
    skills_payload: list[dict[str, Any]],
) -> dict[str, int]:
    counts = {
        "problems_created": 0,
        "problems_skipped_invalid": 0,
        "problems_skipped_unknown_skill": 0,
        "problems_skipped_unknown_level": 0,
    }

    for skill_obj in skills_payload:
        skill_name = to_str(skill_obj.get("skill"))
        if not skill_name:
            continue

        skill = skills_by_name.get(skill_name)
        if skill is None:
            counts["problems_skipped_unknown_skill"] += 1
            continue

        levels = skill_obj.get("levels")
        if not isinstance(levels, dict):
            counts["problems_skipped_invalid"] += 1
            continue

        for level_key, level_payload in levels.items():
            level = CANONICAL_LEVEL_KEYS.get(level_key)
            if level is None:
                counts["problems_skipped_unknown_level"] += 1
                continue

            if not isinstance(level_payload, dict):
                counts["problems_skipped_invalid"] += 1
                continue

            for difficulty in CANONICAL_DIFFICULTIES:
                bucket = level_payload.get(difficulty, [])
                if not isinstance(bucket, list):
                    counts["problems_skipped_invalid"] += 1
                    continue

                for question in bucket:
                    if not isinstance(question, dict):
                        counts["problems_skipped_invalid"] += 1
                        continue

                    title = to_str(question.get("title")) or "Untitled Problem"
                    description = to_str(question.get("description"))
                    question_type = (
                        str(question.get("question_type") or "coding").strip().lower()
                    )

                    problem = Problem(
                        skill_id=skill.id,
                        level=level,
                        title=title[:255],
                        description=description,
                        sample_test_cases=question.get("test_cases")
                        or question.get("sample_test_cases")
                        or [],
                        hidden_test_cases=question.get("hidden_test_cases", []),
                        time_limit_minutes=45,
                        tags=question.get("tags", []),
                        starter_code=question.get("starter_code", None),
                        difficulty_label=to_str(question.get("difficulty"))
                        or difficulty.value,
                        solution_text=to_str(question.get("solution")) or None,
                        question_type=question_type,
                        options=question.get("options", None),
                        correct_option_index=question.get("correct_option_index", None),
                        starter_files=question.get("starter_files", None),
                        entry_point=question.get("entry_point", None),
                        test_harness=question.get("test_harness", None),
                        database_schema=question.get("schema", None),
                    )

                    db.add(problem)
                    counts["problems_created"] += 1

    return counts


def run_seed(input_json: Path) -> None:
    if not input_json.exists():
        raise FileNotFoundError(f"Input JSON file not found: {input_json}")

    raw_payload = json.loads(input_json.read_text(encoding="utf-8"))

    skills_payload = (
        raw_payload.get("skills") if isinstance(raw_payload, dict) else raw_payload
    )
    if not isinstance(skills_payload, list):
        raise ValueError("Input JSON must contain a 'skills' array.")

    admin_email = "admin@example.com"
    admin_password = "AdminPass123!"
    admin_name = "Local Admin"

    candidate_email = "candidate@example.com"
    candidate_password = "Passw0rd!"
    candidate_name = "Local Candidate"

    session_local = get_session_local()

    # Always start from a clean database for deterministic local seed data.
    reset_db_session = session_local()
    try:
        engine = reset_db_session.get_bind()
        reset_db_session.close()
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
    finally:
        reset_db_session.close()

    db = session_local()

    counts = {
        "users_created": 0,
        "skills_created": 0,
        "problems_created": 0,
        "progress_created": 0,
        "problems_skipped_invalid": 0,
        "problems_skipped_unknown_skill": 0,
        "problems_skipped_unknown_level": 0,
    }

    try:
        create_user(
            db=db,
            email=admin_email,
            password=admin_password,
            role=UserRole.ADMIN,
            name=admin_name,
            employee_id="ADM-1001",
            gender="Male",
            department="Engineering",
            exp_indium_years=5,
            exp_overall_years=10,
        )
        counts["users_created"] += 1

        candidate_user = create_user(
            db=db,
            email=candidate_email,
            password=candidate_password,
            role=UserRole.CANDIDATE,
            name=candidate_name,
            employee_id="IND-1001",
            gender="Female",
            department="Engineering",
            exp_indium_years=2,
            exp_overall_years=4,
        )
        counts["users_created"] += 1

        skills = create_skills_from_payload(db, skills_payload)
        counts["skills_created"] = len(skills)

        skills_by_name = {skill.name: skill for skill in skills}

        problem_counts = seed_problems_from_payload(
            db=db,
            skills_by_name=skills_by_name,
            skills_payload=skills_payload,
        )
        counts["problems_created"] += problem_counts["problems_created"]
        counts["problems_skipped_invalid"] += problem_counts["problems_skipped_invalid"]
        counts["problems_skipped_unknown_skill"] += problem_counts[
            "problems_skipped_unknown_skill"
        ]
        counts["problems_skipped_unknown_level"] += problem_counts[
            "problems_skipped_unknown_level"
        ]

        counts["progress_created"] = create_progress_for_candidate(
            db, candidate_user, skills
        )

        db.commit()

        print("Seeding complete.")
        print(f"  Input JSON : {input_json.resolve()}")
        print(f"  Users      : {counts['users_created']}")
        print(f"  Skills     : {counts['skills_created']}")
        print(f"  Problems   : {counts['problems_created']}")
        print(f"  Progress   : {counts['progress_created']}")
        if counts["problems_skipped_invalid"]:
            print(f"  Skipped (invalid)        : {counts['problems_skipped_invalid']}")
        if counts["problems_skipped_unknown_skill"]:
            print(
                f"  Skipped (unknown skill)  : {counts['problems_skipped_unknown_skill']}"
            )
        if counts["problems_skipped_unknown_level"]:
            print(
                f"  Skipped (unknown level)  : {counts['problems_skipped_unknown_level']}"
            )
        print(f"  Admin     : {admin_email} / {admin_password}")
        print(f"  Candidate : {candidate_email} / {candidate_password}")
        print(f"  Timestamp : {datetime.now(timezone.utc).isoformat()}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_seed(DEFAULT_JSON_FILE)

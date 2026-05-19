import os
import uuid
import logging
import httpx

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy import select
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.db.database import get_db
from app.db.models import User, UserRole
from app.schemas import LoginRequest, LoginResponse, LoginUser, SSOLoginRequest
from app.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
    verify_password,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

IS_PROD = os.getenv("ENV", "").lower() == "production"

# ── Azure AD / Microsoft Entra ID settings ──────────────────────────────────
AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID", "")
AZURE_CLIENT_ID = os.getenv("AZURE_CLIENT_ID", "")

# Microsoft's JWKS endpoint for your tenant
_AZURE_JWKS_URL = (
    f"https://login.microsoftonline.com/{AZURE_TENANT_ID}/discovery/v2.0/keys"
)

# Simple in-process JWKS cache (refreshed on every cold start / per-worker)
_jwks_cache: dict | None = None


async def _get_azure_jwks() -> dict:
    """Fetch and cache Azure AD public keys used to verify id_tokens."""
    global _jwks_cache
    if _jwks_cache is not None:
        return _jwks_cache
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(_AZURE_JWKS_URL)
        resp.raise_for_status()
        _jwks_cache = resp.json()
        return _jwks_cache


def _verify_azure_id_token(id_token: str, jwks: dict) -> dict:
    """
    Validate a Microsoft id_token (RS256) against the tenant's JWKS.
    Returns the decoded claims on success, raises ValueError on any failure.
    """
    if not AZURE_TENANT_ID or not AZURE_CLIENT_ID:
        raise ValueError("AZURE_TENANT_ID and AZURE_CLIENT_ID must be set in the environment.")

    try:
        # python-jose can match the correct key from a JWKS dict automatically.
        claims = jwt.decode(
            id_token,
            jwks,
            algorithms=["RS256"],
            audience=AZURE_CLIENT_ID,
            # Allow some clock drift
            options={"leeway": 60},
        )
    except JWTError as exc:
        raise ValueError(f"id_token validation failed: {exc}") from exc

    # Enforce single-tenant: only @indium.tech accounts allowed.
    # The 'tid' claim is the tenant ID — must match ours.
    if AZURE_TENANT_ID and claims.get("tid") != AZURE_TENANT_ID:
        raise ValueError("Token tenant does not match the configured tenant.")

    return claims


# ── Helpers shared by /login and /sso ───────────────────────────────────────

def _build_login_response(user: User, response: Response) -> LoginResponse:
    """Issue access + refresh tokens and return the LoginResponse."""
    token, _ = create_access_token(
        subject=str(user.id),
        extra_claims={
            "role": user.role.value,
            "name": user.name,
            "email": user.email,
        },
    )
    refresh_token, _ = create_refresh_token(subject=str(user.id))

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=IS_PROD,
        samesite="lax",
        path="/api/auth/refresh",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
    )

    return LoginResponse(
        access_token=token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=LoginUser(
            user_id=user.id,
            role=user.role,
            name=user.name,
            email=user.email,
            employee_id=user.employee_id or "",
            gender=user.gender or "",
            department=user.department or "",
        ),
    )


# ── Routes ───────────────────────────────────────────────────────────────────

@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)) -> LoginResponse:
    user = db.scalar(select(User).where(User.email == payload.email))
    if user is None or user.password_hash is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )
    return _build_login_response(user, response)


@router.post("/sso", response_model=LoginResponse)
async def sso_login(payload: SSOLoginRequest, response: Response, db: Session = Depends(get_db)) -> LoginResponse:
    """
    Exchange a Microsoft Entra ID id_token for a platform JWT.

    Flow:
      1. Frontend (MSAL) completes the OAuth2/OIDC popup → gets id_token.
      2. Frontend POSTs id_token here.
      3. We validate it against Azure's JWKS (RS256).
      4. We find or auto-create the user by email.
      5. We issue our own access + refresh tokens and return the standard LoginResponse.
    """
    if not AZURE_TENANT_ID or not AZURE_CLIENT_ID:
        logger.error("SSO endpoint called but AZURE_TENANT_ID / AZURE_CLIENT_ID are not configured.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="SSO is not configured on this server.",
        )

    # 1. Fetch JWKS and validate the token
    try:
        jwks = await _get_azure_jwks()
        claims = _verify_azure_id_token(payload.id_token, jwks)
    except (ValueError, httpx.HTTPError) as exc:
        logger.warning("SSO token validation failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="SSO token is invalid or expired. Please try again.",
        )

    email: str | None = claims.get("email") or claims.get("preferred_username")
    name: str = claims.get("name") or email or "Unknown"

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Microsoft account did not provide an email address.",
        )

    # Normalise to lowercase for lookup
    email = email.lower().strip()

    # 2. Enforce @indium.tech domain — belt-and-suspenders check.
    if not email.endswith("@indium.tech"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only @indium.tech accounts are allowed.",
        )

    # 3. Find or auto-create the user
    user = db.scalar(select(User).where(User.email == email))

    if user is None:
        # Check for Azure App Roles in the token
        azure_roles = claims.get("roles", [])
        is_admin = any(role.lower() == "admin" for role in azure_roles)
        assigned_role = UserRole.ADMIN if is_admin else UserRole.CANDIDATE

        logger.info("SSO: auto-provisioning new %s for %s", assigned_role.value, email)
        user = User(
            id=uuid.uuid4(),
            email=email,
            name=name,
            password_hash=None,       # SSO user — no platform password
            role=assigned_role,
            employee_id=None,
            gender=None,
            department=None,
            exp_indium_years=0,
            exp_overall_years=0,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info("SSO: created user %s (%s)", user.id, email)

    # 4. Issue platform tokens
    return _build_login_response(user, response)


@router.post("/refresh", response_model=LoginResponse)
def refresh(request: Request, response: Response, db: Session = Depends(get_db)) -> LoginResponse:
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing")

    try:
        payload = decode_refresh_token(token)
        user_id = payload.get("sub")
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    new_token, _ = create_access_token(
        subject=str(user.id),
        extra_claims={
            "role": user.role.value,
            "name": user.name,
            "email": user.email,
        },
    )

    expires_in = ACCESS_TOKEN_EXPIRE_MINUTES * 60

    return LoginResponse(
        access_token=new_token,
        expires_in=expires_in,
        user=LoginUser(
            user_id=user.id,
            role=user.role,
            name=user.name,
            email=user.email,
            employee_id=user.employee_id or "",
            gender=user.gender or "",
            department=user.department or "",
        ),
    )


@router.post("/logout")
def logout(response: Response) -> dict[str, str]:
    response.delete_cookie(
        key="refresh_token",
        path="/api/auth/refresh",
        httponly=True,
        secure=IS_PROD,
        samesite="lax"
    )
    return {"message": "Logged out successfully"}

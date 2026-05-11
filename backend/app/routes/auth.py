import os
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User
from app.schemas import LoginRequest, LoginResponse, LoginUser
from app.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])

IS_PROD = os.getenv("ENV", "").lower() == "production"


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)) -> LoginResponse:
    user = db.scalar(select(User).where(User.email == payload.email))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

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
        path="/auth/refresh",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
    )

    expires_in = ACCESS_TOKEN_EXPIRE_MINUTES * 60

    return LoginResponse(
        access_token=token,
        expires_in=expires_in,
        user=LoginUser(
            user_id=user.id,
            role=user.role,
            name=user.name,
            email=user.email,
            employee_id=user.employee_id,
            gender=user.gender,
            department=user.department,
        ),
    )

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
            employee_id=user.employee_id,
            gender=user.gender,
            department=user.department,
        ),
    )

@router.post("/logout")
def logout(response: Response) -> dict[str, str]:
    response.delete_cookie(
        key="refresh_token", 
        path="/auth/refresh", 
        httponly=True, 
        secure=IS_PROD, 
        samesite="lax"
    )
    return {"message": "Logged out successfully"}

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Request, Response
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import get_current_user
from app.auth.security import (
    blacklist_refresh_token,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    is_token_blacklisted,
    verify_password,
)
from app.database.session import get_db_session
from app.exceptions.custom_exceptions import AuthenticationException, DuplicateEntityException
from app.logging.config import logger
from app.middleware.rate_limit import check_login_rate_limit, check_password_reset_rate_limit
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import (
    ForgotPasswordRequest,
    LoginRequest,
    RefreshTokenRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=201, summary="Register new SaaS user")
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db_session)) -> User:
    user_repo = UserRepository(db)

    # Check for duplicate email checks
    existing_user = await user_repo.get_by_email(user_in.email, include_deleted=True)
    if existing_user:
        logger.warning("registration_failed_email_taken", email=user_in.email)
        raise DuplicateEntityException("An account with this email already exists")

    new_user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        password_hash=hash_password(user_in.password),
        role=user_in.role,
        phone=user_in.phone,
        company_name=user_in.company_name,
        profile_image=user_in.profile_image,
        is_active=True,
        is_verified=False,
    )

    created_user = await user_repo.create(new_user)
    logger.info("user_registration_successful", user_id=str(created_user.id), email=created_user.email)
    return created_user

@router.post("/login", response_model=TokenResponse, summary="Login and acquire access & refresh tokens")
async def login(
    credentials: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db_session),
    _ = Depends(check_login_rate_limit),
) -> dict:
    user_repo = UserRepository(db)
    user = await user_repo.get_by_email(credentials.email)

    if not user or not verify_password(credentials.password, user.password_hash):
        logger.warning("login_failed_invalid_credentials", email=credentials.email)
        raise AuthenticationException("Incorrect email or password")

    if not user.is_active:
        logger.warning("login_failed_inactive_account", email=credentials.email)
        raise AuthenticationException("Your account has been deactivated")

    # Generate JWT tokens
    access_token = create_access_token(subject=str(user.id))
    refresh_token = create_refresh_token(subject=str(user.id))

    # Update last login timestamp
    user.last_login = datetime.now(timezone.utc)
    await user_repo.update(user)

    # Store Access Token in secure HttpOnly cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=3600,  # 1 hour matching access expiration
    )

    logger.info("login_successful", user_id=str(user.id), email=user.email, role=user.role)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user,
    }

@router.post("/logout", summary="Logout user and revoke active tokens")
async def logout(
    response: Response,
    body: RefreshTokenRequest,
    current_user: User = Depends(get_current_user),
) -> dict:
    try:
        payload = decode_refresh_token(body.refresh_token)
        exp = payload.get("exp")
        await blacklist_refresh_token(body.refresh_token, exp)
    except JWTError:
        pass  # If the token is already invalid, suppress the error

    # Delete access token cookie
    response.delete_cookie(key="access_token")
    logger.info("logout_successful", user_id=str(current_user.id))
    return {"success": True, "message": "Successfully logged out user session"}

@router.post("/refresh", response_model=TokenResponse, summary="Rotate expired access & refresh tokens")
async def refresh_tokens(
    response: Response,
    body: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    # Verify token is not blacklisted
    if await is_token_blacklisted(body.refresh_token):
        logger.warning("revoked_refresh_token_replay_detected", token_prefix=body.refresh_token[:10])
        raise AuthenticationException("Refresh token is blacklisted or revoked")

    try:
        payload = decode_refresh_token(body.refresh_token)
        user_id = payload.get("sub")
        exp = payload.get("exp")
    except JWTError:
        raise AuthenticationException("Invalid or expired refresh token")

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    if not user or not user.is_active:
        raise AuthenticationException("User is inactive or does not exist")

    # Rotation: Blacklist the old refresh token, generate a brand new pair
    await blacklist_refresh_token(body.refresh_token, exp)

    new_access_token = create_access_token(subject=str(user.id))
    new_refresh_token = create_refresh_token(subject=str(user.id))

    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=3600,
    )

    logger.info("tokens_rotated_successfully", user_id=str(user.id))
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "user": user,
    }

@router.post("/forgot-password", summary="Request password recovery link (Stub)")
async def forgot_password(
    body: ForgotPasswordRequest,
    _ = Depends(check_password_reset_rate_limit),
) -> dict:
    logger.info("forgot_password_request_received", email=body.email)
    # Stub implementation as requested
    return {"success": True, "message": "If the email is registered, a password recovery link has been dispatched"}

@router.post("/reset-password", summary="Execute password reset (Stub)")
async def reset_password(
    body: ResetPasswordRequest,
    _ = Depends(check_password_reset_rate_limit),
) -> dict:
    logger.info("reset_password_request_received")
    # Stub implementation as requested
    return {"success": True, "message": "Password reset execution completed successfully"}

@router.get("/me", response_model=UserResponse, summary="Fetch profile profile of active user")
async def get_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user

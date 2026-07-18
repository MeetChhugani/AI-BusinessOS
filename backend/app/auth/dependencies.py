from typing import List
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.security import decode_access_token
from app.database.session import get_db_session
from app.exceptions.custom_exceptions import AuthenticationException, PermissionDeniedException
from app.models.user import User
from app.repositories.user_repository import UserRepository

# Configured to look for Bearer token in requests. Auto-error is false to allow cookie fallbacks.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login", auto_error=False)

async def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db_session),
) -> User:
    """Dependency injector to parse, decode, and authenticate user tokens."""
    # Fallback: check secure cookie if Authorization header is not set
    if not token:
        token = request.cookies.get("access_token")

    if not token:
        raise AuthenticationException("Missing authentication token")

    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationException("Invalid token payload credentials")
    except JWTError:
        raise AuthenticationException("Invalid or expired authentication token")

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise AuthenticationException("User account does not exist")

    if not user.is_active:
        raise AuthenticationException("User account is inactive")

    return user

class RoleChecker:
    def __init__(self, allowed_roles: List[str]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        """Enforces RBAC access control. Super Admin always bypasses verification."""
        if current_user.role == "SUPER_ADMIN":
            return current_user

        if current_user.role not in self.allowed_roles:
            raise PermissionDeniedException(
                f"Role '{current_user.role}' lacks sufficient privileges to access this route"
            )
        return current_user

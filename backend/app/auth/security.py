from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from app.config.settings import settings
from app.services.redis_service import redis_service

import bcrypt

ALGORITHM = "HS256"

def hash_password(password: str) -> str:
    """Hashes a plain text password using bcrypt."""
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain text password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False

def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    """Generates a JWT access token for a subject."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    """Generates a JWT refresh token for a subject."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    return jwt.encode(to_encode, settings.JWT_REFRESH_SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict:
    """Decodes and validates a JWT access token."""
    payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[ALGORITHM])
    if payload.get("type") != "access":
        raise JWTError("Token type is not access")
    return payload

def decode_refresh_token(token: str) -> dict:
    """Decodes and validates a JWT refresh token."""
    payload = jwt.decode(token, settings.JWT_REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
    if payload.get("type") != "refresh":
        raise JWTError("Token type is not refresh")
    return payload

async def blacklist_refresh_token(token: str, exp_timestamp: int) -> None:
    """Blacklists a refresh token in Redis to prevent replay attacks."""
    now = datetime.now(timezone.utc).timestamp()
    ttl = int(exp_timestamp - now)
    if ttl > 0:
        await redis_service.set(f"blacklist:{token}", "1", expire=ttl)

async def is_token_blacklisted(token: str) -> bool:
    """Checks if a token has been blacklisted in Redis."""
    return await redis_service.exists(f"blacklist:{token}")

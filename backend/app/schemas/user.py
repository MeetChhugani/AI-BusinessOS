import re
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

# Regex rules for names (alphabetic/space/hyphen) and E.164 phones
NAME_REGEX = re.compile(r"^[a-zA-Z\s\-']+$")
PHONE_REGEX = re.compile(r"^\+?[1-9]\d{1,14}$")

class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    phone: Optional[str] = Field(None, description="E.164 formatted international phone number")
    company_name: Optional[str] = Field(None, max_length=100)
    profile_image: Optional[str] = Field(None, max_length=1024)

    @field_validator("full_name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not NAME_REGEX.match(v):
            raise ValueError("Name can only contain alphabetic letters, spaces, hyphens, and apostrophes")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not PHONE_REGEX.match(v):
            raise ValueError("Phone number must match E.164 format (e.g. +1234567890)")
        return v

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    role: str = Field("EMPLOYEE", description="Assigned role in System")

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one number")
        if not any(char in "!@#$%^&*()_+-=[]{}|;':\",./<>?`~" for char in v):
            raise ValueError("Password must contain at least one special character")
        return v

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        allowed = {"SUPER_ADMIN", "ADMIN", "MANAGER", "HR", "FINANCE", "SALES", "EMPLOYEE"}
        v_upper = v.upper().strip()
        if v_upper not in allowed:
            raise ValueError(f"Role must be one of the following: {allowed}")
        return v_upper

class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = None
    company_name: Optional[str] = Field(None, max_length=100)
    profile_image: Optional[str] = Field(None, max_length=1024)

    @field_validator("full_name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not NAME_REGEX.match(v):
            raise ValueError("Name can only contain alphabetic letters, spaces, hyphens, and apostrophes")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not PHONE_REGEX.match(v):
            raise ValueError("Phone number must match E.164 format")
        return v

class UserResponse(UserBase):
    id: UUID
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one number")
        if not any(char in "!@#$%^&*()_+-=[]{}|;':\",./<>?`~" for char in v):
            raise ValueError("Password must contain at least one special character")
        return v

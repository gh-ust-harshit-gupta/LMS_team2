from datetime import date
from pydantic import BaseModel, EmailStr,Field
from app.core.Constants import UserRole,LoginMethod

class CustomerRegisterSchema(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    phone_number: str
    dob: date
    gender: str
    pan_number: str
    mpin: str= Field(min_length=4, max_length=6)


class LoginSchema(BaseModel):
    role: UserRole
    login_method: LoginMethod # "PASSWORD" or "MPIN"

    email: EmailStr | None = None
    password: str | None = None

    mpin: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    role: UserRole

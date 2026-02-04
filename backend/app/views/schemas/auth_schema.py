from datetime import date
from pydantic import BaseModel, EmailStr
from app.core.Constants import UserRole

class CustomerRegisterSchema(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    phone_number: str
    dob: date
    gender: str
    pan_number: str


class LoginSchema(BaseModel):
    email: EmailStr
    password: str
    role:UserRole


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    role: UserRole

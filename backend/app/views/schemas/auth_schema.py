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
    # Accept role as a string for flexibility (e.g., "CUSTOMER")
    role: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    role: str
    # Full authorization header value ready for copy-paste ("Bearer <token>")
    authorization: str | None = None

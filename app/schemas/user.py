
from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None
    dob: Optional[str] = None
    gender: Optional[str] = None
    pan_number: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: str = Field(alias="_id")
    full_name: str
    email: EmailStr
    role: str
    is_active: bool
    is_kyc_verified: bool


class RegisterResponse(BaseModel):
    customer_id: int | str
    account_number: int
    ifsc: str
    balance: float

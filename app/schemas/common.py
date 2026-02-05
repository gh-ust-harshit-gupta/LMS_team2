
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: str

class Message(BaseModel):
    detail: str

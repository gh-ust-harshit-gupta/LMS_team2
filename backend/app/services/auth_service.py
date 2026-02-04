from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)
from app.repositories.user_repository import UserRepository
from datetime import datetime

class AuthService:

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    # -------- CUSTOMER REGISTRATION --------
    def register_customer(self, data):
        if self.user_repo.find_by_email(data.email):
            raise ValueError("User already exists")

        user = {
            "full_name": data.full_name,
            "email": data.email,
            "password_hash": hash_password(data.password),
            "phone_number": data.phone_number,
            "dob": datetime.combine(data.dob, datetime.min.time()),
            "gender": data.gender,
            "pan_number": data.pan_number,
            "role": "CUSTOMER",
            "status": "ACTIVE"
        }

        return self.user_repo.create(user)

    # -------- LOGIN (ALL ROLES) --------
    def login(self, email: str, password: str,role):
        user = self.user_repo.find_by_email(email)
        if not user:
            return None
        if user["role"] != role.value:
            return None
        
        if user["status"] != "ACTIVE":
            return None

        if not verify_password(password, user["password_hash"]):
            return None

        token = create_access_token(
            {
                "sub": str(user["_id"]),
                "role": user["role"]
            }
        )

        return token, user["role"]

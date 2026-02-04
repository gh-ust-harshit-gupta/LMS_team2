from datetime import datetime
from app.repositories.user_repository import UserRepository
from app.core.security import hash_password, verify_password, create_access_token
from app.core.Constants import UserRole

class AuthService:

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    # ---------- CUSTOMER REGISTRATION ----------
    def register_customer(self, data):
        if self.user_repo.find_by_email(data.email):
            raise ValueError("User already exists")

        user = {
            "full_name": data.full_name,
            "email": data.email,
            "password_hash": hash_password(data.password),
            "mpin_hash": hash_password(data.mpin),  # ✅ MPIN HASHED
            "phone_number": data.phone_number,
            "dob": datetime.combine(data.dob, datetime.min.time()),
            "gender": data.gender,
            "pan_number": data.pan_number,
            "role": UserRole.CUSTOMER.value,
            "status": "ACTIVE"
        }

        return self.user_repo.create(user)

    # ---------- LOGIN ----------
    def login(self, data):

        # ❌ MPIN NOT ALLOWED FOR STAFF
        if data.login_method == "MPIN" and data.role != UserRole.CUSTOMER:
            return None

        user = self.user_repo.find_by_email(data.email)
        if not user:
            return None

        if user["role"] != data.role.value:
            return None

        if user["status"] != "ACTIVE":
            return None

        # PASSWORD LOGIN
        if data.login_method == "PASSWORD":
            if not verify_password(data.password, user["password_hash"]):
                return None

        # MPIN LOGIN (CUSTOMER ONLY)
        elif data.login_method == "MPIN":
            if not verify_password(data.mpin, user["mpin_hash"]):
                return None

        else:
            return None

        token = create_access_token({
            "sub": str(user["_id"]),
            "role": user["role"]
        })

        return token, user["role"]

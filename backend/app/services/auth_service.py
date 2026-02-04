from datetime import datetime
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)
from app.core.Constants import UserRole
from app.repositories.user_repository import UserRepository

# 🔥 NEW IMPORTS (for customer auto creation)
from app.repositories.counter_repository import CounterRepository
from app.repositories.customer_repository import CustomerRepository
from app.services.customer_service import CustomerService


class AuthService:

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    # ---------- CUSTOMER REGISTRATION ----------
    def register_customer(self, data):
        # 1️⃣ Check if user already exists
        if self.user_repo.find_by_email(data.email):
            raise ValueError("User already exists")

        # 2️⃣ Create user record
        user = {
            "full_name": data.full_name,
            "email": data.email,
            "password_hash": hash_password(data.password),
            "mpin_hash": hash_password(data.mpin),
            "phone_number": data.phone_number,
            "dob": datetime.combine(data.dob, datetime.min.time()),
            "gender": data.gender,
            "pan_number": data.pan_number,
            "role": UserRole.CUSTOMER.value,
            "status": "ACTIVE",
            "created_at": datetime.utcnow()
        }

        # 3️⃣ Save user to DB
        user_id = self.user_repo.create(user)

        # 🔥 4️⃣ AUTO-CREATE CUSTOMER PROFILE (NEW)
        customer_service = CustomerService(
            CounterRepository(self.user_repo.db),
            CustomerRepository(self.user_repo.db)
        )

        customer_service.create_customer_profile(user)

        # 5️⃣ Return user id
        return user_id

    # ---------- LOGIN ----------
    def login(self, data):
        # ❌ MPIN NOT ALLOWED FOR NON-CUSTOMER ROLES
        if data.login_method == "MPIN" and data.role != UserRole.CUSTOMER:
            return None

        # 1️⃣ Fetch user by email
        user = self.user_repo.find_by_email(data.email)
        if not user:
            return None

        # 2️⃣ Role check
        if user["role"] != data.role.value:
            return None

        # 3️⃣ Status check
        if user["status"] != "ACTIVE":
            return None

        # 4️⃣ PASSWORD LOGIN
        if data.login_method == "PASSWORD":
            if not verify_password(data.password, user["password_hash"]):
                return None

        # 5️⃣ MPIN LOGIN (CUSTOMER ONLY)
        elif data.login_method == "MPIN":
            if not verify_password(data.mpin, user["mpin_hash"]):
                return None

        else:
            return None

        # 6️⃣ Generate JWT
        token = create_access_token(
            {
                "sub": str(user["_id"]),
                "role": user["role"]
            }
        )

        return token, user["role"]

from datetime import datetime
from typing import Optional, Tuple
import re

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)
from app.core.Constants import UserRole
from app.repositories.user_repository import UserRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.verification_user_repository import VerificationUserRepository
from app.repositories.counter_repository import CounterRepository
from app.services.customer_service import CustomerService


# =====================================================
# ROLE NORMALIZER
# =====================================================
def _normalize_role(role_in: str) -> str:
    if not role_in:
        raise ValueError("role is required")

    r = re.sub(r"[^a-z0-9]", "_", role_in.lower()).strip("_")

    mapping = {
        "customer": UserRole.CUSTOMER.value,
        "admin": UserRole.ADMIN.value,
        "manager": UserRole.MANAGER.value,
        "verification": UserRole.VERIFICATION_TEAM.value,
        "verification_team": UserRole.VERIFICATION_TEAM.value,
        "verificationteam": UserRole.VERIFICATION_TEAM.value,
    }

    if r in mapping:
        return mapping[r]

    up = role_in.upper()
    if up in UserRole._value2member_map_:
        return up

    raise ValueError(f"Unknown role: {role_in}")


# =====================================================
# AUTH SERVICE
# =====================================================
class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    # -------------------------------------------------
    # CUSTOMER REGISTRATION
    # -------------------------------------------------
    def register_customer(self, data) -> str:
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
            "role": UserRole.CUSTOMER.value,
            "status": "ACTIVE",
            "created_at": datetime.utcnow()
        }

        user_id = self.user_repo.create(user)

        # Auto-create customer profile
        customer_service = CustomerService(
            CounterRepository(self.user_repo.db),
            CustomerRepository(self.user_repo.db)
        )
        customer_service.create_customer_profile(user)

        return user_id

    # -------------------------------------------------
    # LOGIN (JSON BODY)
    # -------------------------------------------------
    def login(self, data) -> Optional[Tuple[str, str]]:
        # If role is provided, use it. If not provided, try to resolve automatically
        if data.role:
            try:
                role = _normalize_role(data.role)
            except ValueError:
                return None
        else:
            role = None

        # If role explicitly VERIFICATION_TEAM, check verification_users
        if role == UserRole.VERIFICATION_TEAM.value:
            verifier_repo = VerificationUserRepository(self.user_repo.db)
            verifier = verifier_repo.find_by_email(data.email)

            if not verifier or verifier.get("status") != "ACTIVE":
                return None

            if not verify_password(data.password, verifier["password_hash"]):
                return None

            token = create_access_token({
                "sub": str(verifier["verifier_id"]),
                "role": UserRole.VERIFICATION_TEAM.value
            })

            return token, UserRole.VERIFICATION_TEAM.value

        # If role explicitly CUSTOMER or role is None, try customer login first
        if role == UserRole.CUSTOMER.value or role is None:
            user = self.user_repo.find_by_email(data.email)
            if user and user.get("status") == "ACTIVE":
                if user.get("password_hash") and verify_password(data.password, user["password_hash"]):
                    customer = CustomerRepository(self.user_repo.db).find_by_user_id(
                        str(user["_id"])
                    )

                    token = create_access_token({
                        "sub": str(user["_id"]),
                        "role": user["role"],
                        "customer_id": customer["customer_id"] if customer else None
                    })

                    return token, user["role"]

        # If role is None and customer login failed, try verification users as fallback
        if role is None:
            verifier_repo = VerificationUserRepository(self.user_repo.db)
            verifier = verifier_repo.find_by_email(data.email)

            if verifier and verifier.get("status") == "ACTIVE":
                if verify_password(data.password, verifier["password_hash"]):
                    token = create_access_token({
                        "sub": str(verifier["verifier_id"]),
                        "role": UserRole.VERIFICATION_TEAM.value
                    })
                    return token, UserRole.VERIFICATION_TEAM.value

        return None

    # -------------------------------------------------
    # LOGIN (SWAGGER / FORM LOGIN)
    # -------------------------------------------------
    def login_with_identifier(
        self,
        identifier: str,
        password: str,
        role: str | None
    ) -> Optional[Tuple[str, str]]:

        """Support login with either email or username/company_name as identifier.

        If role is provided, the method enforces it; otherwise it will try to
        resolve the correct role automatically (customer first, then verification).
        """
        canonical = None
        if role:
            try:
                canonical = _normalize_role(role)
            except ValueError:
                return None

        # If a canonical role is VERIFICATION_TEAM, check verification repo
        if canonical == UserRole.VERIFICATION_TEAM.value:
            verifier_repo = VerificationUserRepository(self.user_repo.db)
            verifier = verifier_repo.find_by_email(identifier)

            if not verifier or verifier.get("status") != "ACTIVE":
                return None

            if not verify_password(password, verifier["password_hash"]):
                return None

            token = create_access_token({"sub": str(verifier["verifier_id"]), "role": UserRole.VERIFICATION_TEAM.value})
            return token, UserRole.VERIFICATION_TEAM.value

        # Otherwise, attempt customer login first
        user = self.user_repo.find_by_email(identifier)

        # fallback: try common username/company fields
        if not user:
            user = self.user_repo.collection.find_one({"username": identifier})
        if not user:
            user = self.user_repo.collection.find_one({"company_name": identifier})

        if user and user.get("status") == "ACTIVE":
            pwd_hash = user.get("password_hash") or user.get("password")
            if pwd_hash and verify_password(password, pwd_hash):
                token = create_access_token({"sub": str(user["_id"]), "role": user["role"]})
                return token, user["role"]

        # If still not found and role was not specified, try verification_users as fallback
        if canonical is None:
            verifier_repo = VerificationUserRepository(self.user_repo.db)
            verifier = verifier_repo.find_by_email(identifier)

            if verifier and verifier.get("status") == "ACTIVE" and verify_password(password, verifier.get("password_hash")):
                token = create_access_token({"sub": str(verifier["verifier_id"]), "role": UserRole.VERIFICATION_TEAM.value})
                return token, UserRole.VERIFICATION_TEAM.value

        return None

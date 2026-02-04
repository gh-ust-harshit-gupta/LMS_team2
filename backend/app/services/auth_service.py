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

# customer auto creation
from app.repositories.counter_repository import CounterRepository
from app.repositories.customer_repository import CustomerRepository
from app.services.customer_service import CustomerService


def _normalize_role(role_in: str) -> str:
    """Turn common role inputs into canonical UserRole.value strings.

    Accepts inputs like: 'customer', 'CUSTOMER', 'verification-team', 'verification_team', 'verificationteam', 'verification'.
    Returns one of the UserRole values (e.g., 'CUSTOMER', 'VERIFICATION_TEAM').
    Raises ValueError if role is unknown.
    """
    if not role_in:
        raise ValueError("role is required")

    r = re.sub(r"[^a-z0-9]", "_", role_in.lower()).strip("_")

    mapping = {
        "customer": UserRole.CUSTOMER.value,
        "customers": UserRole.CUSTOMER.value,
        "admin": UserRole.ADMIN.value,
        "manager": UserRole.MANAGER.value,
        "verification": UserRole.VERIFICATION_TEAM.value,
        "verification_team": UserRole.VERIFICATION_TEAM.value,
        "verificationteam": UserRole.VERIFICATION_TEAM.value,
        "verification-team": UserRole.VERIFICATION_TEAM.value,
        "verification_team": UserRole.VERIFICATION_TEAM.value,
        "verificationteam": UserRole.VERIFICATION_TEAM.value,
    }

    if r in mapping:
        return mapping[r]

    # If input already matches a canonical value (upper-case), accept it
    up = role_in.upper()
    if up in [v for v in UserRole._value2member_map_.keys()]:
        return up

    raise ValueError(f"Unknown role: {role_in}")


class AuthService:
    """Authentication service for registering customers and logging in users.

    Supports login for different roles (e.g., CUSTOMER, VERIFICATION_TEAM) using
    email + password + role. Returns (token, role) on success or None on failure.
    """

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    # ----------------------------------------
    # CUSTOMER REGISTRATION
    # ----------------------------------------
    def register_customer(self, data) -> str:
        # check existing user
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

        # save user
        user_id = self.user_repo.create(user)

        # auto create customer profile
        customer_service = CustomerService(
            CounterRepository(self.user_repo.db),
            CustomerRepository(self.user_repo.db)
        )
        customer_service.create_customer_profile(user)

        return user_id

    # ----------------------------------------
    # LOGIN (EMAIL + PASSWORD + ROLE)
    # ----------------------------------------
    def login(self, data) -> Optional[Tuple[str, str]]:
        """Login using LoginSchema-like object with attributes: email, password, role

        Returns tuple (token, role) on success or None on failure.
        """
        user = self.user_repo.find_by_email(data.email)
        if not user:
            return None

        try:
            canonical = _normalize_role(data.role)
        except ValueError:
            return None

        # role check (allow case-insensitive match)
        if user.get("role", "").upper() != canonical.upper():
            return None

        # status check
        if user.get("status") != "ACTIVE":
            return None

        # password may be stored as 'password_hash' or legacy 'password'
        pwd_hash = user.get("password_hash") or user.get("password")
        if not pwd_hash:
            return None

        # verify password (verify_password handles exceptions)
        if not verify_password(data.password, pwd_hash):
            return None

        token = create_access_token(
            {
                "sub": str(user["_id"]),
                "role": user["role"]
            }
        )

        return token, user["role"]

    # ----------------------------------------
    # IDENTIFIER-BASED LOGIN (HANDY FOR SWAGGER FORM)
    # ----------------------------------------
    def login_with_identifier(self, identifier: str, password: str, role: str) -> Optional[Tuple[str, str]]:
        """Support login with either email or username/company_name as identifier.

        This mirrors the reference implementation's behavior for accepting a single
        "username" form field in Swagger UI.
        """
        try:
            canonical = _normalize_role(role)
        except ValueError:
            return None

        # try email
        user = self.user_repo.find_by_email(identifier)

        # fallback: try common username/company fields
        if not user:
            user = self.user_repo.collection.find_one({"username": identifier})
        if not user:
            user = self.user_repo.collection.find_one({"company_name": identifier})

        if not user:
            return None

        if user.get("role", "").upper() != canonical.upper():
            return None

        if user.get("status") != "ACTIVE":
            return None

        pwd_hash = user.get("password_hash") or user.get("password")
        if not pwd_hash or not verify_password(password, pwd_hash):
            return None

        token = create_access_token({"sub": str(user["_id"]), "role": user["role"]})
        return token, user["role"]

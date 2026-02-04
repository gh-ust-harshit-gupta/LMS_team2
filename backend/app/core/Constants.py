from enum import Enum


class UserRole(str, Enum):
    CUSTOMER = "CUSTOMER"
    MANAGER = "MANAGER"
    ADMIN = "ADMIN"
    VERIFICATION_TEAM = "VERIFICATION_TEAM"


class LoginMethod(str, Enum):
    PASSWORD = "PASSWORD"
    MPIN = "MPIN"
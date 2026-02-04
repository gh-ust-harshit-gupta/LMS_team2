from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

from app.views.schemas.auth_schema import (
    CustomerRegisterSchema,
    LoginSchema,
    TokenResponse
)
from app.services.auth_service import AuthService
from app.repositories.user_repository import UserRepository
from app.database import get_db
from app import config

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


# ---------- Dependency ----------
def get_auth_service(db=Depends(get_db)):
    return AuthService(UserRepository(db))


# ---------- CUSTOMER REGISTRATION ----------
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_customer(
    request: CustomerRegisterSchema,
    service: AuthService = Depends(get_auth_service)
):
    try:
        user_id = service.register_customer(request)
        return {
            "message": "Customer registered successfully",
            "user_id": user_id
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ---------- LOGIN (PASSWORD / MPIN) ----------
@router.post("/login", response_model=TokenResponse)
def login(
    request: LoginSchema,
    service: AuthService = Depends(get_auth_service)
):
    # 🔥 CHANGED: login now supports PASSWORD or MPIN via schema
    result = service.login(request)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials or role"
        )

    token, role = result
    return {
        "access_token": token,
        "role": role
    }


# ---------- JWT DEPENDENCY ----------
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        payload = jwt.decode(
            credentials.credentials,
            config.JWT_SECRET_KEY,
            algorithms=[config.JWT_ALGORITHM]
        )

        return {
            "user_id": payload.get("sub"),
            "role": payload.get("role")
        }

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

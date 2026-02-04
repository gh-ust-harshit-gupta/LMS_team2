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


def get_auth_service(db=Depends(get_db)):
    return AuthService(UserRepository(db))


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_customer(
    request: CustomerRegisterSchema,
    service: AuthService = Depends(get_auth_service)
):
    try:
        user_id = service.register_customer(request)
        return {"message": "Customer registered successfully", "user_id": user_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=TokenResponse)
def login(
    request: LoginSchema,
    service: AuthService = Depends(get_auth_service)
):
    result = service.login(request.email, request.password,request.role)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credential or role"
        )

    token, role = result
    return {"access_token": token, "role": role}


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
            "user_id": payload["sub"],
            "role": payload["role"]
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

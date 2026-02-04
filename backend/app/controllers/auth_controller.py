from fastapi import APIRouter, Depends, HTTPException, status, Form, Request
# OAuth2PasswordRequestForm is not required for the unified endpoint; we parse form data manually

from app.views.schemas.auth_schema import (
    CustomerRegisterSchema,
    LoginSchema,
    TokenResponse
)
from app.services.auth_service import AuthService
from app.repositories.user_repository import UserRepository
from app.database import get_db
from app.core.security import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_customer(
    request: CustomerRegisterSchema,
    db=Depends(get_db)
):
    service = AuthService(UserRepository(db))
    try:
        user_id = service.register_customer(request)
        return {"message": "Customer registered successfully", "user_id": user_id}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


from fastapi import Request
from pydantic import ValidationError


# Unified login endpoint: accepts either JSON {email,password,role} or
# form-encoded OAuth2 fields (username,password) plus a required 'role' form field.
@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    role: str | None = Form(None),
    db=Depends(get_db)
):
    service = AuthService(UserRepository(db))

    content_type = request.headers.get("content-type", "")

    # JSON body (API clients)
    if content_type.startswith("application/json"):
        try:
            body = await request.json()
        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON body")

        try:
            login_data = LoginSchema(**body)
        except ValidationError as e:
            # return first error message
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

        result = service.login(login_data)

    # Form body (Swagger / OAuth2 clients)
    else:
        form = await request.form()
        identifier = form.get("username") or form.get("email")
        password = form.get("password")
        # role may be omitted (OAuth2 flows typically don't include role). Default to CUSTOMER.
        form_role = form.get("role") or form.get("scope")
        final_role = role or form_role or "CUSTOMER"

        if not identifier or not password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Form login requires 'username' (or 'email') and 'password'"
            )

        result = service.login_with_identifier(
            identifier=identifier,
            password=password,
            role=final_role
        )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials or role"
        )

    token, role = result

    return {
        "access_token": token,
        "token_type": "Bearer",
        "role": role,
        "authorization": f"Bearer {token}"
    }

@router.get("/me")
def get_me(user=Depends(get_current_user)):
    return user


from fastapi import APIRouter, Depends, Request, HTTPException
from ..schemas.user import UserCreate, UserLogin, RegisterResponse
from ..schemas.common import TokenResponse
from ..services.auth_service import register_customer, login
from ..services.account_service import auto_create_account_for

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post('/register', response_model=RegisterResponse)
async def register(payload: UserCreate):
    user = await register_customer(payload.dict())
    # use numeric customer_id if provided
    cid = user.get("customer_id") or user.get("_id")
    acc = await auto_create_account_for(cid)
    return {
        "customer_id": cid,
        "account_number": acc.get("account_number"),
        "ifsc": acc.get("ifsc_code"),
        "balance": acc.get("balance"),
    }

@router.post('/login', response_model=TokenResponse)
async def login_route(request: Request):
    """Accept JSON {email,password} or form data (username/password) for compatibility.

    If `python-multipart` is not installed, parse `application/x-www-form-urlencoded` manually
    and raise a helpful error for multipart requests.
    """
    ctype = request.headers.get("content-type", "")
    email = None
    password = None
    if "application/json" in ctype:
        body = await request.json()
        email = body.get("email")
        password = body.get("password")
    else:
        # Handle multipart/form-data (requires python-multipart) or urlencoded forms
        if "multipart/form-data" in ctype:
            try:
                form = await request.form()
            except Exception:
                raise HTTPException(status_code=500, detail="Missing dependency 'python-multipart'. Install with: pip install python-multipart")
            email = form.get("username") or form.get("email")
            password = form.get("password")
        else:
            # fallback for application/x-www-form-urlencoded without multipart parser
            body_bytes = await request.body()
            try:
                from urllib.parse import parse_qs
                parsed = parse_qs(body_bytes.decode())
                email = (parsed.get("username") or parsed.get("email") or [None])[0]
                password = (parsed.get("password") or [None])[0]
            except Exception:
                # as last resort, try json
                try:
                    body = await request.json()
                    email = body.get("email")
                    password = body.get("password")
                except Exception:
                    pass
    if not email or not password:
        raise HTTPException(status_code=422, detail="email and password are required")
    token = await login(email, password)
    return token

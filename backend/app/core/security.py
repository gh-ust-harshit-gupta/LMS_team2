# from datetime import datetime, timedelta
# from jose import jwt
# from argon2 import PasswordHasher
# from argon2.exceptions import VerifyMismatchError
# from app import config
# from fastapi.security import HTTPBearer

# ph = PasswordHasher()
# jwt_bearer = HTTPBearer()


# def hash_password(password: str) -> str:
#     return ph.hash(password)


# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     try:
#         # PasswordHasher.verify raises exceptions on mismatch or invalid hash.
#         ph.verify(hashed_password, plain_password)
#         return True
#     except Exception:
#         # Treat any verification failure as a non-match.
#         return False


# def create_access_token(data: dict):
#     payload = data.copy()
#     expire = datetime.utcnow() + timedelta(minutes=config.JWT_EXPIRE_MINUTES)
#     # Use numeric timestamps for exp/iat for better interoperability
#     payload.update({
#         "exp": int(expire.timestamp()),
#         "iat": int(datetime.utcnow().timestamp())
#     })

#     return jwt.encode(
#         payload,
#         config.JWT_SECRET_KEY,
#         algorithm=config.JWT_ALGORITHM
#     )
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app import config

# ========================
# CONFIG (use app config)
# ========================
SECRET_KEY = getattr(config, "JWT_SECRET_KEY", "CHANGE_THIS_SECRET_KEY")
ALGORITHM = getattr(config, "JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = getattr(config, "JWT_EXPIRE_MINUTES", 60)

# ========================
# PASSWORD HASHING (argon2)
# ========================
ph = PasswordHasher()


def hash_password(password: str) -> str:
    return ph.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        ph.verify(hashed_password, plain_password)
        return True
    except VerifyMismatchError:
        return False
    except Exception:
        # Any other error treat as verification failure
        return False


# ========================
# JWT
# ========================
def create_access_token(data: dict) -> str:
    payload = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # numeric timestamps for compatibility (use timezone-aware datetimes)
    payload.update({"exp": int(expire.timestamp()), "iat": int(now.timestamp())})

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

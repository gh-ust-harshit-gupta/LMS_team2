
import time
from datetime import datetime, timedelta
from typing import Optional
import bcrypt
import jwt
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from ..core.config import settings
from ..database.mongo import get_db
from bson import ObjectId
from ..utils.id import to_object_id

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PREFIX}/auth/login")


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception:
        return False


def create_access_token(subject: dict, expires_minutes: int | None = None) -> str:
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes or settings.JWT_EXPIRE_MINUTES)
    payload = {**subject, "exp": expire}
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("user_id")
    role = payload.get("role")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    db = await get_db()
    # support numeric user ids or ObjectId strings
    user = None
    try:
        uid = int(user_id)
        user = await db.users.find_one({"_id": uid})
    except Exception:
        user = await db.users.find_one({"_id": to_object_id(user_id)})
    if not user or not user.get("is_active", True):
        raise HTTPException(status_code=401, detail="User inactive or not found")
    user["_id"] = str(user["_id"])  # for response use
    return user


def require_roles(*allowed_roles: str):
    async def dep(user = Depends(get_current_user)):
        if user.get("role") not in allowed_roles:
            raise HTTPException(status_code=403, detail="Not authorized for this operation")
        return user
    return dep

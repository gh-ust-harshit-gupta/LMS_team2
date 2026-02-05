
from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException
from ..database.mongo import get_db
from ..core.security import hash_password, verify_password, create_access_token
from ..core.config import settings
from ..models.enums import Roles
from ..utils.sequences import next_customer_id

async def register_customer(payload: dict) -> dict:
    db = await get_db()
    existing = await db.users.find_one({"email": payload["email"]})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    # assign a numeric customer id for easier external referencing
    customer_id = await next_customer_id()

    user_doc = {
        "full_name": payload["full_name"],
        "email": payload["email"],
        "password": hash_password(payload["password"]),
        "phone": payload.get("phone"),
        "dob": payload.get("dob"),
        "gender": payload.get("gender"),
        "pan_number": payload.get("pan_number"),
        "customer_id": customer_id,
        "_id": customer_id,
        "role": Roles.CUSTOMER,
        "is_active": True,
        "is_kyc_verified": False,
        "created_at": datetime.utcnow(),
    }
    res = await db.users.insert_one(user_doc)
    user_id = res.inserted_id
    from ..utils.serializers import normalize_doc
    out = {"_id": user_id, **user_doc}
    return normalize_doc(out)

async def login(email: str, password: str) -> dict:
    db = await get_db()
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not verify_password(password, user.get("password", "")):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"user_id": str(user["_id"]), "role": user["role"]})
    return {"access_token": token, "token_type": "bearer", "role": user["role"], "user_id": str(user["_id"]) }

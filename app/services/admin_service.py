
from ..database.mongo import get_db

async def list_pending_admin_approvals():
    db = await get_db()
    loans = await db.personal_loans.find({"status": "pending_admin_approval"}).to_list(length=200)
    loans += await db.vehicle_loans.find({"status": "pending_admin_approval"}).to_list(length=200)
    from ..utils.serializers import normalize_doc
    return [normalize_doc(l) for l in loans]


from datetime import datetime
from fastapi import HTTPException
from ..core.security import hash_password
from ..models.enums import Roles
from ..utils.sequences import next_customer_id

async def create_staff_user(email: str, full_name: str, password: str, role: str):
    if role not in [Roles.MANAGER, Roles.VERIFICATION]:
        raise HTTPException(status_code=400, detail="Invalid role")
    db = await get_db()
    existing = await db.users.find_one({"email": email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")
    doc = {
        "full_name": full_name,
        "email": email,
        "password": hash_password(password),
        "role": role,
        "_id": await next_customer_id(),
        "is_active": True,
        "is_kyc_verified": False,
        "created_at": datetime.utcnow(),
    }
    res = await db.users.insert_one(doc)
    from ..utils.serializers import normalize_doc
    out = {"_id": doc["_id"], **doc}
    return normalize_doc(out)


from datetime import datetime
from ..database.mongo import get_db

async def get_settings():
    db = await get_db()
    s = await db.system_settings.find_one({})
    if not s:
        s = {
            "personal_loan_interest": 12.0,
            "vehicle_loan_interest": 10.0,
            "min_cibil_required": 650,
            "updated_by": None,
            "updated_at": datetime.utcnow(),
        }
        await db.system_settings.insert_one(s)
    # stringify _id if present to avoid ObjectId serialization errors
    if s and "_id" in s:
        s["_id"] = str(s["_id"])
    return s

async def update_settings(admin_id: str, payload: dict):
    db = await get_db()
    await db.system_settings.update_one({}, {"$set": {**payload, "updated_by": admin_id, "updated_at": datetime.utcnow()}}, upsert=True)
    return await get_settings()

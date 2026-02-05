
from pymongo import ReturnDocument
from ..database.mongo import get_db

async def next_account_number() -> int:
    db = await get_db()
    doc = await db.counters.find_one_and_update(
        {"_id": "account_number"},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return int(doc["seq"])  # starts at 1000000001 after first increment


async def next_customer_id() -> int:
    db = await get_db()
    doc = await db.counters.find_one_and_update(
        {"_id": "customer_id"},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return int(doc["seq"])  # starts at 1


async def next_loan_id() -> int:
    db = await get_db()
    doc = await db.counters.find_one_and_update(
        {"_id": "loan_id"},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return int(doc["seq"])  # starts at 1


async def next_transaction_id() -> int:
    db = await get_db()
    doc = await db.counters.find_one_and_update(
        {"_id": "transaction_id"},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return int(doc["seq"])  # starts at 1


from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING
from ..core.config import settings

client: AsyncIOMotorClient | None = None

def get_client() -> AsyncIOMotorClient:
    global client
    if client is None:
        client = AsyncIOMotorClient(settings.MONGODB_URI)
    return client

async def get_db():
    return get_client()[settings.MONGODB_DB]

async def init_indexes():
    db = await get_db()
    # Unique index on user email
    await db.users.create_index([("email", ASCENDING)], unique=True, name="uniq_email")
    # Unique account number
    await db.bank_accounts.create_index([("account_number", ASCENDING)], unique=True, name="uniq_account")
    # Common indexes
    await db.personal_loans.create_index([("customer_id", ASCENDING)], name="pl_cust_idx")
    await db.vehicle_loans.create_index([("customer_id", ASCENDING)], name="vl_cust_idx")
    await db.transactions.create_index([("customer_id", ASCENDING)], name="txn_cust_idx")
    await db.transactions.create_index([("loan_id", ASCENDING)], name="txn_loan_idx")
    await db.kyc_details.create_index([("customer_id", ASCENDING)], unique=True, name="uniq_kyc_customer")
    # Counter for account numbers
    await db.counters.update_one(
        {"_id": "account_number"},
        {"$setOnInsert": {"seq": 1000000000}},
        upsert=True,
    )

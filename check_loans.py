import asyncio
from app.database.mongo import get_db

async def check():
    db = await get_db()
    loans = await db.personal_loans.find({}).to_list(None)
    print(f"Total loans in personal_loans: {len(loans)}")
    for l in loans:
        print(f"  _id={l.get('_id')}, loan_id={l.get('loan_id')}, customer_id={l.get('customer_id')}, status={l.get('status')}")

asyncio.run(check())

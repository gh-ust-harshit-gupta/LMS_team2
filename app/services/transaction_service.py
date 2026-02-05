
from ..database.mongo import get_db

async def list_transactions(customer_id: str):
    db = await get_db()
    txns = await db.transactions.find({"customer_id": customer_id}).sort("created_at", -1).to_list(length=200)
    out = []
    for t in txns:
        out.append({
            "id": str(t["_id"]),
            "loan_id": t.get("loan_id"),
            "loan_type": t.get("loan_type"),
            "type": t.get("type"),
            "amount": float(t.get("amount", 0)),
            "balance_after": float(t.get("balance_after", 0)),
            "created_at": t.get("created_at").isoformat(),
        })
    return out

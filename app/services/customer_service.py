
from ..database.mongo import get_db


async def profile_dashboard(customer_id: str):
    db = await get_db()
    # customer_id is the numeric identifier assigned at registration
    user = await db.users.find_one({"customer_id": customer_id})
    acc = await db.bank_accounts.find_one({"customer_id": customer_id})
    kyc = await db.kyc_details.find_one({"customer_id": customer_id})
    # active loans
    active_personal = await db.personal_loans.find({"customer_id": customer_id, "status": {"$in": ["active", "admin_approved", "manager_approved"]}}).to_list(length=50)
    active_vehicle = await db.vehicle_loans.find({"customer_id": customer_id, "status": {"$in": ["active", "admin_approved", "manager_approved"]}}).to_list(length=50)
    def agg(loans):
        remaining_tenure = sum([int(l.get("remaining_tenure", 0)) for l in loans])
        remaining_amount = sum([float(l.get("remaining_amount", 0)) for l in loans])
        return remaining_tenure, remaining_amount
    rt1, ra1 = agg(active_personal)
    rt2, ra2 = agg(active_vehicle)
    profile = {
        "name": user.get("full_name") if user else None,
        "email": user.get("email") if user else None,
        "account_number": acc.get("account_number") if acc else None,
        "ifsc": acc.get("ifsc_code") if acc else None,
        "balance": acc.get("balance") if acc else 0.0,
        "cibil_score": kyc.get("cibil_score") if kyc else None,
        "kyc_status": kyc.get("kyc_status") if kyc else "not_submitted",
        "active_loans": len(active_personal) + len(active_vehicle),
        "remaining_tenure": rt1 + rt2,
        "remaining_amount": ra1 + ra2,
    }
    return profile

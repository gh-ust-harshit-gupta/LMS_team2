
from datetime import datetime
from bson import ObjectId
from ..utils.id import to_object_id, loan_id_filter
from fastapi import HTTPException
from ..database.mongo import get_db
from ..utils.serializers import normalize_doc
from ..models.enums import LoanStatus
from ..utils.sequences import next_loan_id, next_transaction_id
from ..utils.dates import next_month_date


def compute_emi(amount: float, interest_rate: float, tenure_months: int) -> float:
    # Validate tenure
    if tenure_months <= 0:
        raise HTTPException(status_code=400, detail="Invalid tenure_months; must be greater than 0")
    # Simple flat interest EMI approximation for zero interest
    monthly_interest = interest_rate / 12 / 100
    if monthly_interest == 0:
        return round(amount / tenure_months, 2)
    # Standard EMI formula
    r = monthly_interest
    n = tenure_months
    denom = (1 + r) ** n - 1
    if denom == 0:
        raise HTTPException(status_code=400, detail="Invalid parameters for EMI calculation")
    emi = amount * r * (1 + r) ** n / denom
    return round(emi, 2)

async def apply_loan(collection: str, customer_id: str, payload: dict, interest_rate: float):
    db = await get_db()
    # ensure KYC approved
    kyc = await db.kyc_details.find_one({"customer_id": customer_id, "kyc_status": "approved"})
    if not kyc:
        raise HTTPException(status_code=400, detail="KYC not approved")
    amount = float(payload["loan_amount"]) 
    tenure = int(payload["tenure_months"]) 
    if tenure <= 0:
        raise HTTPException(status_code=400, detail="tenure_months must be greater than 0")
    emi = compute_emi(amount, interest_rate, tenure)
    # assign a simple incremental loan_id for easier references
    loan_seq = await next_loan_id()
    doc = {
        **payload,
        "loan_id": loan_seq,
        "_id": loan_seq,
        "customer_id": customer_id,
        "remaining_tenure": tenure,
        "emi_per_month": emi,
        "remaining_amount": round(emi * tenure, 2),
        "total_paid": 0.0,
        "cibil_score_at_apply": int(kyc.get("cibil_score", 0)),
        "max_eligible_amount": float(payload.get("salary_income", 0)) * 60,  # simplistic
        "status": LoanStatus.APPLIED,
        "manager_id": None,
        "verification_id": None,
        "admin_id": None,
        "next_emi_date": next_month_date(),
        "applied_at": datetime.utcnow(),
        "approved_at": None,
        "disbursed_at": None,
    }
    res = await db[collection].insert_one(doc)
    out = {"_id": loan_seq, **doc}
    return normalize_doc(out)

async def list_manager_loans(manager_id: str):
    db = await get_db()
    loans = await db.personal_loans.find({}).to_list(length=200)
    loans += await db.vehicle_loans.find({}).to_list(length=200)
    loans = [normalize_doc(l) for l in loans]
    return loans

async def assign_verification(loan_collection: str, loan_id: str, verification_id: str):
    db = await get_db()
    filt = loan_id_filter(loan_id)
    loan = await db[loan_collection].find_one(filt)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    await db[loan_collection].update_one(filt, {"$set": {"verification_id": verification_id, "status": LoanStatus.ASSIGNED_TO_VERIFICATION}})
    return True

async def verification_complete(loan_collection: str, loan_id: str, approved: bool):
    db = await get_db()
    filt = loan_id_filter(loan_id)
    loan = await db[loan_collection].find_one(filt)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    await db[loan_collection].update_one(filt, {"$set": {"status": LoanStatus.VERIFICATION_DONE if approved else LoanStatus.REJECTED}})
    return True

async def manager_approve_or_reject(loan_collection: str, loan_id: str, manager_id: str, approve: bool):
    db = await get_db()
    filt = loan_id_filter(loan_id)
    loan = await db[loan_collection].find_one(filt)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    if not approve:
        await db[loan_collection].update_one(filt, {"$set": {"status": LoanStatus.REJECTED, "manager_id": manager_id}})
        return True
    amount = float(loan["loan_amount"]) 
    if amount <= 1500000:
        await db[loan_collection].update_one(filt, {"$set": {"status": LoanStatus.MANAGER_APPROVED, "manager_id": manager_id, "approved_at": datetime.utcnow()}})
    else:
        await db[loan_collection].update_one(filt, {"$set": {"status": LoanStatus.PENDING_ADMIN_APPROVAL, "manager_id": manager_id}})
    return True


async def admin_final_approve(loan_collection: str, loan_id: str, admin_id: str):
    db = await get_db()
    filt = loan_id_filter(loan_id)
    loan = await db[loan_collection].find_one(filt)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    amount = float(loan.get("loan_amount", 0))
    if amount <= 1500000:
        # Rule: manager is final approver for <= 15 lakh; admin cannot override
        raise HTTPException(status_code=403, detail="Admin approval not required for this loan amount")
    if loan.get("status") != LoanStatus.PENDING_ADMIN_APPROVAL:
        raise HTTPException(status_code=400, detail="Loan not pending admin approval")
    await db[loan_collection].update_one(filt, {"$set": {"status": LoanStatus.ADMIN_APPROVED, "admin_id": admin_id, "approved_at": datetime.utcnow()}})
    return True

async def send_sanction(loan_collection: str, loan_id: str):
    db = await get_db()
    filt = loan_id_filter(loan_id)
    await db[loan_collection].update_one(filt, {"$set": {"status": LoanStatus.SANCTION_SENT}})
    return True

async def mark_signed_received(loan_collection: str, loan_id: str):
    db = await get_db()
    filt = loan_id_filter(loan_id)
    await db[loan_collection].update_one(filt, {"$set": {"status": LoanStatus.SIGNED_RECEIVED}})
    return True

async def disburse(loan_collection: str, loan_id: str):
    db = await get_db()
    filt = loan_id_filter(loan_id)
    loan = await db[loan_collection].find_one(filt)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    # credit to customer's bank account
    acc = await db.bank_accounts.find_one({"customer_id": loan["customer_id"]})
    new_balance = float(acc.get("balance", 0)) + float(loan["loan_amount"]) 
    await db.bank_accounts.update_one({"_id": acc["_id"]}, {"$set": {"balance": new_balance}})
    txn = {
        "customer_id": loan["customer_id"],
        "loan_id": loan.get("loan_id") or (int(loan["_id"]) if isinstance(loan.get("_id"), int) else str(loan["_id"])),
        "loan_type": "personal" if loan_collection == "personal_loans" else "vehicle",
        "type": "disbursement",
        "amount": float(loan["loan_amount"]),
        "balance_after": new_balance,
        "created_at": datetime.utcnow(),
    }
    # use numeric transaction id
    tid = await next_transaction_id()
    txn["_id"] = tid
    txn["transaction_id"] = tid
    await db.transactions.insert_one(txn)
    await db[loan_collection].update_one(filt, {"$set": {"status": LoanStatus.ACTIVE, "disbursed_at": datetime.utcnow()}})
    return True

async def pay_emi(loan_collection: str, loan_id: str, customer_id: str):
    db = await get_db()
    filt = loan_id_filter(loan_id)
    # ensure customer match
    filt["customer_id"] = customer_id
    loan = await db[loan_collection].find_one(filt)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    if loan.get("status") != LoanStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Loan not active")
    acc = await db.bank_accounts.find_one({"customer_id": customer_id})
    emi = float(loan["emi_per_month"])
    if float(acc.get("balance", 0)) < emi:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    new_balance = float(acc.get("balance", 0)) - emi
    await db.bank_accounts.update_one({"_id": acc["_id"]}, {"$set": {"balance": new_balance}})
    # update loan
    remaining_tenure = int(loan["remaining_tenure"]) - 1
    remaining_amount = float(loan["remaining_amount"]) - emi
    await db[loan_collection].update_one(
        filt,
        {"$set": {
            "remaining_tenure": remaining_tenure,
            "remaining_amount": remaining_amount,
            "total_paid": float(loan.get("total_paid", 0)) + emi,
            "next_emi_date": next_month_date(),
            "status": LoanStatus.COMPLETED if remaining_tenure <= 0 else LoanStatus.ACTIVE
        }}
    )
    txn = {
        "customer_id": customer_id,
        "loan_id": loan.get("loan_id") or (int(loan.get("_id")) if isinstance(loan.get("_id"), int) else str(loan.get("_id"))),
        "loan_type": "personal" if loan_collection == "personal_loans" else "vehicle",
        "type": "emi",
        "amount": emi,
        "balance_after": new_balance,
        "created_at": datetime.utcnow(),
    }
    tid = await next_transaction_id()
    txn["_id"] = tid
    txn["transaction_id"] = tid
    await db.transactions.insert_one(txn)
    # KYC: increase cibil +1 max 850
    kyc = await db.kyc_details.find_one({"customer_id": customer_id})
    if kyc:
        new_cibil = min(850, int(kyc.get("cibil_score", 0)) + 1)
        await db.kyc_details.update_one({"_id": kyc["_id"]}, {"$set": {"cibil_score": new_cibil}})
    return True


async def pay_emi_any(loan_id: str, customer_id: str):
    # Try personal first
    try:
        await pay_emi('personal_loans', loan_id, customer_id)
        return {"collection": "personal_loans"}
    except Exception:
        # try vehicle
        await pay_emi('vehicle_loans', loan_id, customer_id)
        return {"collection": "vehicle_loans"}


async def list_customer_loans(customer_id: str):
    db = await get_db()
    loans = await db.personal_loans.find({"customer_id": customer_id}).to_list(length=200)
    loans += await db.vehicle_loans.find({"customer_id": customer_id}).to_list(length=200)
    from ..utils.serializers import normalize_doc
    return [normalize_doc(l) for l in loans]

from datetime import datetime
from fastapi import HTTPException
from bson import ObjectId
from ..database.mongo import get_db
from ..utils.serializers import normalize_doc, normalize_value


def _normalize_customer_id(cid):
    # convert numeric-looking strings to int so DB matches stored numeric customer_id
    try:
        if isinstance(cid, str) and cid.isdigit():
            return int(cid)
    except Exception:
        pass
    return cid

# Scoring weights: employment 25, income 25, emi 25, experience 25
def compute_scores(payload: dict) -> dict:
    employment_score = 25 if (payload.get("employment_status") == "employed") else 10
    income = float(payload.get("monthly_income") or 0)
    income_score = 25 if income >= 80000 else (20 if income >= 50000 else (15 if income >= 30000 else 10))
    emi_months = int(payload.get("existing_emi_months") or 0)
    emi_score = 25 if emi_months == 0 else (15 if emi_months <= 12 else 10)
    exp_years = int(payload.get("years_of_experience") or 0)
    experience_score = 25 if exp_years >= 5 else (15 if exp_years >= 2 else 10)

    total_score = employment_score + income_score + emi_score + experience_score

    # CIBIL mapping (per spec)
    if total_score > 80:
        cibil = 730
    elif 60 <= total_score <= 80:
        cibil = 600
    else:
        cibil = 400

    eligible = cibil > 650

    return {
        "employment_score": employment_score,
        "income_score": income_score,
        "emi_score": emi_score,
        "experience_score": experience_score,
        "total_score": total_score,
        "cibil_score": cibil,
        "loan_eligible": eligible,
    }


async def submit_kyc(customer_id: str, payload: dict) -> dict:
    db = await get_db()
    customer_id = _normalize_customer_id(customer_id)
    existing = await db.kyc_details.find_one({"customer_id": customer_id})
    if existing:
        raise HTTPException(status_code=400, detail="KYC already submitted")
    # Store submitted KYC details. Scores will be set by verification team.
    doc = {
        **payload,
        "customer_id": customer_id,
        "employment_score": None,
        "income_score": None,
        "emi_score": None,
        "experience_score": None,
        "total_score": None,
        "cibil_score": None,
        "loan_eligible": False,
        "kyc_status": "pending",
        "verified_by": None,
        "remarks": None,
        "submitted_at": datetime.utcnow(),
        "verified_at": None,
    }
    res = await db.kyc_details.insert_one(doc)
    out = {"_id": str(res.inserted_id), **doc}
    return normalize_doc(out)


async def verify_kyc(customer_id: str, verifier_id: str, approve: bool, scores: dict | None = None, remarks: str | None = None):
    db = await get_db()
    customer_id = _normalize_customer_id(customer_id)
    kyc = await db.kyc_details.find_one({"customer_id": customer_id})
    if not kyc:
        raise HTTPException(status_code=404, detail="KYC not found")

    status = "approved" if approve else "rejected"

    # If verifier provided manual scores, use them; otherwise use existing stored scores
    if scores:
        employment_score = int(scores.get("employment_score", 0))
        income_score = int(scores.get("income_score", 0))
        emi_score = int(scores.get("emi_score", 0))
        experience_score = int(scores.get("experience_score", 0))
    else:
        employment_score = int(kyc.get("employment_score") or 0)
        income_score = int(kyc.get("income_score") or 0)
        emi_score = int(kyc.get("emi_score") or 0)
        experience_score = int(kyc.get("experience_score") or 0)

    total_score = employment_score + income_score + emi_score + experience_score

    # CIBIL mapping
    if total_score > 80:
        cibil = 730
    elif 60 <= total_score <= 80:
        cibil = 600
    else:
        cibil = 400

    loan_eligible = cibil > 650

    # Update KYC record with manual scores and computed cibil
    await db.kyc_details.update_one(
        {"_id": kyc["_id"]},
        {
            "$set": {
                "employment_score": employment_score,
                "income_score": income_score,
                "emi_score": emi_score,
                "experience_score": experience_score,
                "total_score": total_score,
                "cibil_score": cibil,
                "loan_eligible": loan_eligible,
                "kyc_status": status,
                "verified_by": verifier_id,
                "remarks": remarks,
                "verified_at": datetime.utcnow(),
            }
        },
    )

    # Update user by customer_id (numeric or string), not by ObjectId _id
    await db.users.update_one({"customer_id": customer_id}, {"$set": {"is_kyc_verified": approve}})

    updated = await db.kyc_details.find_one({"customer_id": customer_id})
    return normalize_doc(updated)


async def get_verification_dashboard():
    db = await get_db()

    pending_kyc = await db.kyc_details.find({"kyc_status": "pending"}).to_list(length=100)
    pending_loans = await db.personal_loans.find({"status": "assigned_to_verification"}).to_list(length=100)
    pending_loans += await db.vehicle_loans.find({"status": "assigned_to_verification"}).to_list(length=100)

    # Stringify ids to avoid JSON issues
    pending_kyc = [normalize_doc(i) for i in pending_kyc]
    pending_loans = [normalize_doc(i) for i in pending_loans]

    return {"pending_kyc": pending_kyc, "pending_loan_verifications": pending_loans}


async def get_kyc_by_customer(customer_id: str):
    db = await get_db()
    customer_id = _normalize_customer_id(customer_id)
    kyc = await db.kyc_details.find_one({"customer_id": customer_id})
    if not kyc:
        raise HTTPException(status_code=404, detail="KYC not found")
    return normalize_doc(kyc)
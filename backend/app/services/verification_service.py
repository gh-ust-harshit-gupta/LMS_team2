def calculate_cibil(total_score: int) -> int:
    if total_score >= 90:
        return 780
    elif total_score >= 80:
        return 770
    elif total_score >= 70:
        return 750
    elif total_score >= 60:
        return 720
    elif total_score >= 50:
        return 680
    else:
        return 0


def calculate_loan_limits(score: int) -> dict:
    if score >= 90:
        return {"PERSONAL": 250000, "VEHICLE": 300000}
    elif score >= 80:
        return {"PERSONAL": 200000, "VEHICLE": 250000}
    elif score >= 70:
        return {"PERSONAL": 150000, "VEHICLE": 200000}
    elif score >= 60:
        return {"PERSONAL": 100000, "VEHICLE": 150000}
    else:
        return {"PERSONAL": 0, "VEHICLE": 0}


class VerificationService:
    def __init__(self, kyc_repo, customer_repo):
        self.kyc_repo = kyc_repo
        self.customer_repo = customer_repo

    def get_pending_kyc(self):
        docs = list(self.kyc_repo.collection.find({"status": "PENDING_VERIFICATION"}))
        # Convert Mongo types to JSON-serializable structures
        cleaned = []
        for d in docs:
            doc = dict(d)
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
            if "submitted_at" in doc and hasattr(doc["submitted_at"], "isoformat"):
                doc["submitted_at"] = doc["submitted_at"].isoformat()
            cleaned.append(doc)
        return cleaned

    def verify_kyc(self, kyc_id: int, scores: dict):
        total_score = sum(scores.values())
        cibil_score = calculate_cibil(total_score)
        loan_limits = calculate_loan_limits(total_score)

        self.kyc_repo.update(
            kyc_id,
            {
                "verification_scores": scores,
                "total_score": total_score,
                "cibil_score": cibil_score,
                "eligible_loan_limits": loan_limits,
                "status": "VERIFIED"
            }
        )

        kyc = self.kyc_repo.find_by_kyc_id(kyc_id)
        self.customer_repo.update_kyc_status(
            kyc["customer_id"],
            "VERIFIED"
        )

        return {
            "kyc_id": kyc_id,
            "total_score": total_score,
            "cibil_score": cibil_score,
            "eligible_loan_limits": loan_limits
        }

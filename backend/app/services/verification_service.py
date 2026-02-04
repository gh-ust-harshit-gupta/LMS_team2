class VerificationService:
    def __init__(self, kyc_repo, customer_repo):
        self.kyc_repo = kyc_repo
        self.customer_repo = customer_repo

    def verify_kyc(self, kyc_id: int, scores: dict):
        total_score = (
            scores["employment_type"]
            + scores["monthly_income"]
            + scores["existing_emi"]
            + scores["experience"]
        )

        self.kyc_repo.update_verification(
            kyc_id,
            {
                "verification_scores": scores,
                "total_score": total_score,
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
            "status": "VERIFIED",
            "total_score": total_score
        }

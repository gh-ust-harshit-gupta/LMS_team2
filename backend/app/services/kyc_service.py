from datetime import datetime

class KycService:
    def __init__(self, counter_repo, kyc_repo, customer_repo):
        self.counter_repo = counter_repo
        self.kyc_repo = kyc_repo
        self.customer_repo = customer_repo

    def submit_kyc(self, customer_id: int, data: dict, submitted_by: str):
        # Auto-increment kyc_id
        kyc_id = self.counter_repo.get_next_sequence("kyc_id")

        employment = data["employment_details"]

        # 🔐 EMI LOGIC
        if not employment["has_existing_emis"]:
            employment["emi_months_left"] = None

        kyc_doc = {
            "kyc_id": kyc_id,
            "customer_id": customer_id,

            "personal_details": data["personal_details"],
            "identity_details": data["identity_details"],
            "employment_details": employment,
            "address_details": data["address_details"],
            "documents": data["documents"],

            "status": "PENDING_VERIFICATION",
            "submitted_by": submitted_by,
            "submitted_at": datetime.utcnow()
        }

        # Update customer KYC status
        self.customer_repo.update_kyc_status(customer_id, "PENDING_VERIFICATION")

        return self.kyc_repo.create(kyc_doc)

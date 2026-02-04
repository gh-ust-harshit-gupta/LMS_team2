from datetime import datetime

class KycService:
    def __init__(self, counter_repo, kyc_repo, customer_repo):
        self.counter_repo = counter_repo
        self.kyc_repo = kyc_repo
        self.customer_repo = customer_repo

    def submit_kyc(self, customer_id: int, data: dict):
        kyc_id = self.counter_repo.get_next_sequence("kyc_id")

        kyc = {
            "kyc_id": kyc_id,
            "customer_id": customer_id,
            "personal_details": data["personal_details"],
            "identity_details": data["identity_details"],
            "employment_details": data["employment_details"],
            "address_details": data["address_details"],
            "documents": data["documents"],
            "status": "PENDING_VERIFICATION",
            "submitted_at": datetime.utcnow()
        }

        self.customer_repo.update_kyc_status(customer_id, "PENDING_VERIFICATION")
        return self.kyc_repo.create(kyc)

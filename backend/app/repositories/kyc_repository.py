class KycRepository:
    def __init__(self, db):
        self.collection = db["kyc"]

    def create(self, kyc: dict):
        self.collection.insert_one(kyc)
        return kyc

    def find_pending(self):
        return list(self.collection.find({"status": "PENDING_VERIFICATION"}))

    def find_by_kyc_id(self, kyc_id: int):
        return self.collection.find_one({"kyc_id": kyc_id})

    def update_verification(self, kyc_id: int, update: dict):
        self.collection.update_one(
            {"kyc_id": kyc_id},
            {"$set": update}
        )

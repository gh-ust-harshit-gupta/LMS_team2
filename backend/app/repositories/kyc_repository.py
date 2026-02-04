class KycRepository:
    def __init__(self, db):
        self.collection = db["kyc"]

    def create(self, kyc: dict):
        self.collection.insert_one(kyc)
        return kyc

    def find_by_customer_id(self, customer_id: int):
        return self.collection.find_one({"customer_id": customer_id})

    def find_by_kyc_id(self, kyc_id: int):
        return self.collection.find_one({"kyc_id": kyc_id})

    def update(self, kyc_id: int, update: dict):
        self.collection.update_one(
            {"kyc_id": kyc_id},
            {"$set": update}
        )

class CustomerRepository:
    def __init__(self, db):
        self.collection = db["customers"]

    def create(self, customer: dict):
        self.collection.insert_one(customer)
        return customer

    def find_by_user_id(self, user_id: str):
        return self.collection.find_one({"user_id": user_id})

    def update_kyc_status(self, customer_id: int, status: str):
        self.collection.update_one(
            {"customer_id": customer_id},
            {"$set": {"kyc_status": status}}
        )

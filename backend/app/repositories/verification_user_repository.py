class VerificationUserRepository:
    def __init__(self, db):
        self.collection = db["verification_users"]

    def create(self, user: dict):
        self.collection.insert_one(user)
        return user

    def find_by_email(self, email: str):
        return self.collection.find_one({"email": email})

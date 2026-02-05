class UserRepository:

    def __init__(self, db):
        self.db = db  
        self.collection = db["users"]

    def find_by_email(self, email: str):
        return self.collection.find_one({"email": email})

    def create(self, user: dict):
        result = self.collection.insert_one(user)
        user["_id"] = result.inserted_id
        return str(result.inserted_id)

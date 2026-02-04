from datetime import datetime
from app.core.security import hash_password

class AdminService:
    def __init__(self, counter_repo, verification_user_repo):
        self.counter_repo = counter_repo
        self.verification_user_repo = verification_user_repo

    def create_verification_user(self, data):
        verifier_id = self.counter_repo.get_next_sequence("verifier_id")

        user = {
            "verifier_id": verifier_id,
            "email": data["email"],
            "password_hash": hash_password(data["password"]),
            "full_name": data["full_name"],
            "role": "VERIFICATION_TEAM",
            "status": "ACTIVE",
            "created_at": datetime.utcnow()
        }

        return self.verification_user_repo.create(user)

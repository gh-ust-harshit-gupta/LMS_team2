from datetime import datetime
from app.database import db
from app.core.security import hash_password
from app.repositories.counter_repository import CounterRepository

def create_verification_user():
    counter_repo = CounterRepository(db)
    verifier_id = counter_repo.get_next_sequence("verifier_id")

    verification_user = {
        "verifier_id": verifier_id,
        "email": "veri@example.com",
        "password_hash": hash_password("Veri@123"),
        "full_name": "Verification Officer 1",
        "role": "VERIFICATION_TEAM",
        "status": "ACTIVE",
        "created_at": datetime.utcnow()
    }

    db.verification_users.insert_one(verification_user)
    print("✅ Verification user created:", verification_user["email"])


if __name__ == "__main__":
    create_verification_user()

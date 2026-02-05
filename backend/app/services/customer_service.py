from datetime import datetime
import random

class CustomerService:
    def __init__(self, counter_repo, customer_repo):
        self.counter_repo = counter_repo
        self.customer_repo = customer_repo

    def generate_account_number(self) -> str:
        """
        Generates a random 12-digit bank account number
        """
        return str(random.randint(10**11, 10**12 - 1))

    def create_customer_profile(self, user: dict):
        # Auto-increment customer_id
        customer_id = self.counter_repo.get_next_sequence("customer_id")

        customer = {
            "customer_id": customer_id,
            "user_id": str(user["_id"]),
            "pan_number": user["pan_number"],
            "dob": user["dob"],
            "gender": user["gender"],

            # 🔥 UPDATED PART
            "bank_account_no": self.generate_account_number(),  # 12-digit random
            "ifsc_code": "PCIN0001",                              # fixed IFSC

            "account_balance": 0,
            "kyc_status": "NOT_SUBMITTED",
            "created_at": datetime.utcnow()
        }

        return self.customer_repo.create(customer)

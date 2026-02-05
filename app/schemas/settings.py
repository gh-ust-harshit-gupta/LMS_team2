
from pydantic import BaseModel

class SystemSettingsUpdate(BaseModel):
    personal_loan_interest: float
    vehicle_loan_interest: float
    min_cibil_required: int

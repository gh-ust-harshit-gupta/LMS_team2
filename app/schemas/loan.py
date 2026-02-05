
from pydantic import BaseModel, Field
from typing import Optional

class ApplyPersonalLoan(BaseModel):
    bank_account_number: int
    full_name: str
    pan_number: str
    loan_amount: float
    loan_purpose: str
    salary_income: float
    monthly_avg_balance: float
    tenure_months: int
    pay_slip_url: Optional[str] = None  # PDF file path
    guarantor_name: Optional[str] = None
    guarantor_phone: Optional[str] = None
    guarantor_pan: Optional[str] = None

class ApplyVehicleLoan(ApplyPersonalLoan):
    vehicle_type: str
    vehicle_model: str
    vehicle_price_doc_url: Optional[str] = None  # PDF file path (vehicle showroom price doc)

class LoanOut(BaseModel):
    id: str = Field(alias="_id")
    loan_amount: float
    tenure_months: int
    remaining_tenure: int
    emi_per_month: float
    remaining_amount: float
    status: str
    pay_slip_url: Optional[str] = None
    vehicle_price_doc_url: Optional[str] = None

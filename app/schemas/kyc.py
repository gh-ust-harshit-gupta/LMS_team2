
from pydantic import BaseModel, Field
from typing import Optional, Dict

class KYCSubmit(BaseModel):
    full_name: str
    dob: str  # ISO date string (YYYY-MM-DD)
    nationality: str
    photo_url: Optional[str] = None
    gender: Optional[str] = None
    father_or_spouse_name: Optional[str] = None
    marital_status: Optional[str] = None
    phone_number: Optional[str] = None
    pan_number: Optional[str] = None
    aadhaar_number: Optional[str] = None
    employment_status: Optional[str] = None
    employment_type: Optional[str] = None
    company_name: Optional[str] = None
    monthly_income: Optional[float] = None
    existing_emi_months: Optional[int] = None
    years_of_experience: Optional[int] = None
    address: Optional[str] = None
    pan_card_url: Optional[str] = None  # PDF file path
    aadhar_card_url: Optional[str] = None  # PDF file path

class KYCOut(BaseModel):
    id: str = Field(alias="_id")
    kyc_status: str
    total_score: int | None
    cibil_score: int | None
    loan_eligible: bool | None
    dob: Optional[str] = None
    pan_card_url: Optional[str] = None
    aadhar_card_url: Optional[str] = None


class KYCVerify(BaseModel):
    approve: bool
    employment_score: int
    income_score: int
    emi_score: int
    experience_score: int
    remarks: Optional[str] = None

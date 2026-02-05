from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# ---------- SUB-SCHEMAS ----------

class PersonalDetails(BaseModel):
    full_name: str
    dob: str
    gender: str
    nationality: str
    father_or_spouse_name: str
    marital_status: str
    phone_number: str


class IdentityDetails(BaseModel):
    pan_number: str
    aadhaar_number: str


class EmploymentDetails(BaseModel):
    employment_type: str
    company_name: Optional[str] = None
    monthly_income: int
    has_existing_emis: bool
    emi_months_left: Optional[int] = None
    years_of_experience: int


class AddressDetails(BaseModel):
    address_line: str
    city: str
    state: str
    pincode: str


class Documents(BaseModel):
    photograph_url: str


# ---------- MAIN KYC SCHEMA ----------

class KycCreateSchema(BaseModel):
    personal_details: PersonalDetails
    identity_details: IdentityDetails
    employment_details: EmploymentDetails
    address_details: AddressDetails
    documents: Documents

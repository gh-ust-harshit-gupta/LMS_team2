from pydantic import BaseModel, conint

class VerificationScoreSchema(BaseModel):
    employment_type: conint(ge=0, le=25)
    monthly_income: conint(ge=0, le=25)
    existing_emi: conint(ge=0, le=25)
    experience: conint(ge=0, le=25)

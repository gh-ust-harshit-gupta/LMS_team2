from pydantic import BaseModel
from typing import Dict

class KycSchema(BaseModel):
    personal_details: Dict
    identity_details: Dict
    employment_details: Dict
    address_details: Dict
    documents: Dict

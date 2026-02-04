from fastapi import APIRouter, Depends
from app.core.permissions import require_role
from app.database import get_db
from app.repositories.counter_repository import CounterRepository
from app.repositories.kyc_repository import KycRepository
from app.repositories.customer_repository import CustomerRepository
from app.services.kyc_service import KycService
from app.views.schemas.kyc_schema import KycSchema

router = APIRouter(prefix="/kyc", tags=["KYC"])

def get_kyc_service(db=Depends(get_db)):
    return KycService(
        CounterRepository(db),
        KycRepository(db),
        CustomerRepository(db)
    )

@router.post("/submit")
def submit_kyc(
    data: KycSchema,
    user=Depends(require_role("CUSTOMER")),
    service: KycService = Depends(get_kyc_service)
):
    return service.submit_kyc(user["customer_id"], data.dict())

from fastapi import APIRouter, Depends
from app.database import get_db
from app.core.permissions import require_role
from app.views.schemas.kyc_schema import KycCreateSchema
from app.repositories.counter_repository import CounterRepository
from app.repositories.kyc_repository import KycRepository
from app.repositories.customer_repository import CustomerRepository
from app.services.kyc_service import KycService

router = APIRouter(prefix="/kyc", tags=["KYC"])

def get_kyc_service(db=Depends(get_db)):
    return KycService(
        CounterRepository(db),
        KycRepository(db),
        CustomerRepository(db)
    )

@router.post("/submit")
def submit_kyc(
    payload: KycCreateSchema,
    user=Depends(require_role("CUSTOMER")),
    service: KycService = Depends(get_kyc_service)
):
    return service.submit_kyc(
        customer_id=user["customer_id"],
        data=payload.dict(),
        submitted_by=user["sub"]
    )

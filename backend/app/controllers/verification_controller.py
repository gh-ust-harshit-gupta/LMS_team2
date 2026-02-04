from fastapi import APIRouter, Depends
from app.core.permissions import require_role
from app.database import get_db
from app.repositories.kyc_repository import KycRepository
from app.repositories.customer_repository import CustomerRepository
from app.services.verification_service import VerificationService

router = APIRouter(prefix="/verification", tags=["Verification"])

def get_verification_service(db=Depends(get_db)):
    return VerificationService(
        KycRepository(db),
        CustomerRepository(db)
    )

@router.post("/kyc/{kyc_id}/verify")
def verify_kyc(
    kyc_id: int,
    scores: dict,
    user=Depends(require_role("VERIFICATION_TEAM")),
    service: VerificationService = Depends(get_verification_service)
):
    return service.verify_kyc(kyc_id, scores)

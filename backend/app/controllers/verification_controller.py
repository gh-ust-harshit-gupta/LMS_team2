from fastapi import APIRouter, Depends
from app.database import get_db
from app.core.permissions import require_role
from app.repositories.kyc_repository import KycRepository
from app.repositories.customer_repository import CustomerRepository
from app.services.verification_service import VerificationService
from app.views.schemas.verification_schema import VerificationScoreSchema

router = APIRouter(prefix="/verification", tags=["Verification Team"])


def get_verification_service(db=Depends(get_db)):
    return VerificationService(
        KycRepository(db),
        CustomerRepository(db)
    )


@router.get("/kyc/pending")
def get_pending_kyc(
    user=Depends(require_role("VERIFICATION_TEAM")),
    service: VerificationService = Depends(get_verification_service)
):
    return service.get_pending_kyc()


@router.post("/kyc/{kyc_id}/verify")
def verify_kyc(
    kyc_id: int,
    scores: VerificationScoreSchema,
    user=Depends(require_role("VERIFICATION_TEAM")),
    service: VerificationService = Depends(get_verification_service)
):
    return service.verify_kyc(kyc_id, scores.dict())

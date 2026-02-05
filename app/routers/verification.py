
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from ..core.security import require_roles
from ..models.enums import Roles, LoanCollection, DocumentType
from ..services.kyc_service import get_verification_dashboard, verify_kyc, get_kyc_by_customer
from ..services.loan_service import verification_complete
from ..schemas.kyc import KYCOut, KYCVerify
from ..services.document_service import get_document_path
from ..database.mongo import get_db

router = APIRouter(prefix="/verification", tags=["verification"])

@router.get('/dashboard')
async def dashboard(user=Depends(require_roles(Roles.VERIFICATION))):
    return await get_verification_dashboard()

@router.put('/verify-kyc/{customer_id}', response_model=KYCOut)
async def verify_kyc_route(customer_id: str, payload: KYCVerify, user=Depends(require_roles(Roles.VERIFICATION))):
    scores = {
        "employment_score": int(payload.employment_score),
        "income_score": int(payload.income_score),
        "emi_score": int(payload.emi_score),
        "experience_score": int(payload.experience_score),
    }
    return await verify_kyc(customer_id, user['_id'], payload.approve, scores, payload.remarks)


@router.get('/kyc/{customer_id}', response_model=KYCOut)
async def get_kyc_route(customer_id: str, user=Depends(require_roles(Roles.VERIFICATION))):
    return await get_kyc_by_customer(customer_id)

@router.put('/verify-loan/{loan_collection}/{loan_id}')
async def verify_loan_route(loan_collection: LoanCollection, loan_id: str, approved: bool, user=Depends(require_roles(Roles.VERIFICATION))):
    return await verification_complete(loan_collection.value, loan_id, approved)


@router.get('/kyc-documents/{customer_id}')
async def get_kyc_documents(customer_id: str, user=Depends(require_roles(Roles.VERIFICATION))):
    """Get list of uploaded KYC documents for a customer."""
    db = await get_db()
    kyc = await db.kyc_details.find_one({"customer_id": int(customer_id)})
    if not kyc:
        return {"error": "KYC not found"}
    return {
        "customer_id": customer_id,
        "pan_card_url": kyc.get("pan_card_url"),
        "aadhar_card_url": kyc.get("aadhar_card_url"),
    }


@router.get('/download-kyc-document/{customer_id}/{doc_type}')
async def download_kyc_document(customer_id: str, doc_type: DocumentType, user=Depends(require_roles(Roles.VERIFICATION))):
    """Download a KYC document (pan_card or aadhar_card)."""
    db = await get_db()
    kyc = await db.kyc_details.find_one({"customer_id": int(customer_id)})
    if not kyc:
        return {"error": "KYC not found"}
    
    doc_field = f"{doc_type.value}_url" if doc_type in [DocumentType.PAN_CARD, DocumentType.AADHAR_CARD] else None
    if not doc_field or not kyc.get(doc_field):
        return {"error": f"Document {doc_type.value} not found"}
    
    file_path = get_document_path(kyc.get(doc_field))
    return FileResponse(file_path, media_type="application/pdf", filename=f"{customer_id}_{doc_type.value}.pdf")


@router.get('/loan-documents/{loan_id}')
async def get_loan_documents(loan_id: str, user=Depends(require_roles(Roles.VERIFICATION))):
    """Get list of uploaded loan documents."""
    db = await get_db()
    # Try both personal and vehicle loans
    loan = await db.personal_loans.find_one({"loan_id": int(loan_id)})
    if not loan:
        loan = await db.vehicle_loans.find_one({"loan_id": int(loan_id)})
    
    if not loan:
        return {"error": "Loan not found"}
    
    return {
        "loan_id": loan_id,
        "collection": "personal" if "personal_loans" in str(type(loan)) else "vehicle",
        "pay_slip_url": loan.get("pay_slip_url"),
        "vehicle_price_doc_url": loan.get("vehicle_price_doc_url"),
    }


@router.get('/download-loan-document/{loan_id}/{doc_type}')
async def download_loan_document(loan_id: str, doc_type: DocumentType, user=Depends(require_roles(Roles.VERIFICATION))):
    """Download a loan document (pay_slip or vehicle_price_doc)."""
    db = await get_db()
    loan = await db.personal_loans.find_one({"loan_id": int(loan_id)})
    if not loan:
        loan = await db.vehicle_loans.find_one({"loan_id": int(loan_id)})
    
    if not loan:
        return {"error": "Loan not found"}
    
    doc_field = f"{doc_type.value}_url" if doc_type in [DocumentType.PAY_SLIP, DocumentType.VEHICLE_PRICE_DOC] else None
    if not doc_field or not loan.get(doc_field):
        return {"error": f"Document {doc_type.value} not found"}
    
    file_path = get_document_path(loan.get(doc_field))
    return FileResponse(file_path, media_type="application/pdf", filename=f"loan_{loan_id}_{doc_type.value}.pdf")

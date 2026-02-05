
from fastapi import APIRouter, Depends, File, UploadFile
from ..core.security import require_roles
from ..models.enums import Roles, DocumentType
from ..services.account_service import add_money
from ..services.customer_service import profile_dashboard
from ..services.kyc_service import submit_kyc
from ..services.loan_service import apply_loan, pay_emi, list_customer_loans
from ..schemas.loan import ApplyPersonalLoan, ApplyVehicleLoan, LoanOut
from ..services.settings_service import get_settings
from ..schemas.kyc import KYCSubmit, KYCOut
from ..services.document_service import upload_document

router = APIRouter(prefix="/customer", tags=["customer"])

@router.post('/add-money')
async def add_money_route(amount: float, user=Depends(require_roles(Roles.CUSTOMER))):
    cid = user.get("customer_id") or user.get("_id")
    return await add_money(cid, amount)

@router.get('/get/profile')
async def profile(user=Depends(require_roles(Roles.CUSTOMER))):
    cid = user.get("customer_id") or user.get("_id")
    return await profile_dashboard(cid)

@router.post('/submit-kyc', response_model=KYCOut)
async def submit_kyc_route(payload: KYCSubmit, user=Depends(require_roles(Roles.CUSTOMER))):
    # use numeric customer_id if available
    cid = user.get("customer_id") or user.get("_id")
    return await submit_kyc(cid, payload.dict())

@router.post('/apply-personal-loan', response_model=LoanOut)
async def apply_personal(payload: ApplyPersonalLoan, user=Depends(require_roles(Roles.CUSTOMER))):
    settings = await get_settings()
    cid = user.get("customer_id") or user.get("_id")
    return await apply_loan('personal_loans', cid, payload.dict(), settings['personal_loan_interest'])

@router.post('/apply-vehicle-loan', response_model=LoanOut)
async def apply_vehicle(payload: ApplyVehicleLoan, user=Depends(require_roles(Roles.CUSTOMER))):
    settings = await get_settings()
    cid = user.get("customer_id") or user.get("_id")
    return await apply_loan('vehicle_loans', cid, payload.dict(), settings['vehicle_loan_interest'])

async def pay_emi_route(loan_collection: str, loan_id: str, user=Depends(require_roles(Roles.CUSTOMER))):
    cid = user.get("customer_id") or user.get("_id")
    return await pay_emi(loan_collection, loan_id, cid)


from ..services.loan_service import pay_emi_any

@router.post('/pay-emi/{loan_id}')
async def pay_emi_by_id(loan_id: str, user=Depends(require_roles(Roles.CUSTOMER))):
    cid = user.get("customer_id") or user.get("_id")
    return await pay_emi_any(loan_id, cid)


@router.get('/loans')
async def customer_loans(user=Depends(require_roles(Roles.CUSTOMER))):
    cid = user.get("customer_id") or user.get("_id")
    return await list_customer_loans(cid)


@router.post('/upload-kyc-document/{doc_type}')
async def upload_kyc_doc(doc_type: DocumentType, file: UploadFile = File(...), user=Depends(require_roles(Roles.CUSTOMER))):
    """Upload KYC documents (pan_card or aadhar_card) as PDF."""
    if doc_type not in [DocumentType.PAN_CARD, DocumentType.AADHAR_CARD]:
        raise ValueError("doc_type must be 'pan_card' or 'aadhar_card'")
    cid = user.get("customer_id") or user.get("_id")
    doc_path = await upload_document(file, f"kyc/{cid}", f"{doc_type.value}.pdf")
    return {"document_type": doc_type.value, "file_path": doc_path}


@router.post('/upload-loan-document/{loan_id}/{doc_type}')
async def upload_loan_doc(loan_id: str, doc_type: DocumentType, file: UploadFile = File(...), user=Depends(require_roles(Roles.CUSTOMER))):
    """Upload loan documents (pay_slip for personal or vehicle_price_doc for vehicle) as PDF."""
    if doc_type not in [DocumentType.PAY_SLIP, DocumentType.VEHICLE_PRICE_DOC]:
        raise ValueError("doc_type must be 'pay_slip' or 'vehicle_price_doc'")
    cid = user.get("customer_id") or user.get("_id")
    doc_path = await upload_document(file, f"loans/{cid}/{loan_id}", f"{doc_type.value}.pdf")
    return {"document_type": doc_type.value, "loan_id": loan_id, "file_path": doc_path}

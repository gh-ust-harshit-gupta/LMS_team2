
from fastapi import APIRouter, Depends
from ..core.security import require_roles
from ..models.enums import Roles, LoanCollection
from ..services.manager_service import get_loans_for_manager
from ..services.loan_service import assign_verification, manager_approve_or_reject

router = APIRouter(prefix="/manager", tags=["manager"])

@router.get('/loans')
async def list_loans(user=Depends(require_roles(Roles.MANAGER))):
    return await get_loans_for_manager()

@router.put('/assign-verification/{loan_collection}/{loan_id}/{verification_id}')
async def assign_verification_route(loan_collection: LoanCollection, loan_id: str, verification_id: str, user=Depends(require_roles(Roles.MANAGER))):
    return await assign_verification(loan_collection.value, loan_id, verification_id)

@router.put('/approve/{loan_collection}/{loan_id}')
async def approve_route(loan_collection: LoanCollection, loan_id: str, user=Depends(require_roles(Roles.MANAGER))):
    return await manager_approve_or_reject(loan_collection.value, loan_id, user['_id'], True)

@router.put('/reject/{loan_collection}/{loan_id}')
async def reject_route(loan_collection: LoanCollection, loan_id: str, user=Depends(require_roles(Roles.MANAGER))):
    return await manager_approve_or_reject(loan_collection.value, loan_id, user['_id'], False)


from fastapi import APIRouter, Depends
from ..core.security import require_roles
from ..models.enums import Roles, LoanCollection
from ..services.admin_service import list_pending_admin_approvals
from ..services.loan_service import admin_final_approve, send_sanction, mark_signed_received, disburse
from ..services.settings_service import update_settings
from ..schemas.settings import SystemSettingsUpdate

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get('/pending-approvals')
async def pending(user=Depends(require_roles(Roles.ADMIN))):
    return await list_pending_admin_approvals()

@router.put('/approve/{loan_collection}/{loan_id}')
async def approve_route(loan_collection: LoanCollection, loan_id: str, user=Depends(require_roles(Roles.ADMIN))):
    return await admin_final_approve(loan_collection.value, loan_id, user['_id'])

@router.put('/sanction/{loan_collection}/{loan_id}')
async def sanction_route(loan_collection: LoanCollection, loan_id: str, user=Depends(require_roles(Roles.ADMIN))):
    return await send_sanction(loan_collection.value, loan_id)

@router.put('/signed/{loan_collection}/{loan_id}')
async def signed_route(loan_collection: LoanCollection, loan_id: str, user=Depends(require_roles(Roles.ADMIN))):
    return await mark_signed_received(loan_collection.value, loan_id)

@router.put('/disburse/{loan_collection}/{loan_id}')
async def disburse_route(loan_collection: LoanCollection, loan_id: str, user=Depends(require_roles(Roles.ADMIN))):
    return await disburse(loan_collection.value, loan_id)

@router.put('/settings')
async def settings_update(payload: SystemSettingsUpdate, user=Depends(require_roles(Roles.ADMIN))):
    return await update_settings(user['_id'], payload.dict())


from pydantic import BaseModel, EmailStr
from ..services.admin_service import create_staff_user

class StaffCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: str  # manager or verification

@router.post('/create-staff')
async def create_staff(payload: StaffCreate, user=Depends(require_roles(Roles.ADMIN))):
    return await create_staff_user(payload.email, payload.full_name, payload.password, payload.role)

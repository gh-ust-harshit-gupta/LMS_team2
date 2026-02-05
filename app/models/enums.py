
from enum import Enum

class Roles:
    CUSTOMER = "customer"
    ADMIN = "admin"
    MANAGER = "manager"
    VERIFICATION = "verification"

class LoanCollection(str, Enum):
    PERSONAL = "personal_loans"
    VEHICLE = "vehicle_loans"

class DocumentType(str, Enum):
    PAN_CARD = "pan_card"
    AADHAR_CARD = "aadhar_card"
    PAY_SLIP = "pay_slip"
    VEHICLE_PRICE_DOC = "vehicle_price_doc"

class LoanStatus:
    APPLIED = "applied"
    ASSIGNED_TO_VERIFICATION = "assigned_to_verification"
    VERIFICATION_DONE = "verification_done"
    MANAGER_APPROVED = "manager_approved"
    PENDING_ADMIN_APPROVAL = "pending_admin_approval"
    ADMIN_APPROVED = "admin_approved"
    REJECTED = "rejected"
    SANCTION_SENT = "sanction_sent"
    SIGNED_RECEIVED = "signed_received"
    ACTIVE = "active"
    COMPLETED = "completed"
    DISBURSED = "disbursed"

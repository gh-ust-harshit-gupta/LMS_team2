
from ..database.mongo import get_db
from ..models.enums import LoanStatus
from ..utils.serializers import normalize_doc


async def get_loans_for_manager():
    db = await get_db()
    loans = await db.personal_loans.find({"status": {"$in": [LoanStatus.APPLIED, LoanStatus.VERIFICATION_DONE, LoanStatus.PENDING_ADMIN_APPROVAL]}}).to_list(length=200)
    loans += await db.vehicle_loans.find({"status": {"$in": [LoanStatus.APPLIED, LoanStatus.VERIFICATION_DONE, LoanStatus.PENDING_ADMIN_APPROVAL]}}).to_list(length=200)
    return [normalize_doc(l) for l in loans]

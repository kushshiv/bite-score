from fastapi import APIRouter

from app.schemas import BillingStatus

router = APIRouter(prefix="/billing", tags=["billing"])


@router.get("/status", response_model=BillingStatus)
def billing_status():
    return BillingStatus()

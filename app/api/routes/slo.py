from fastapi import APIRouter

from app.observability.slo import (
    slo_monitor,
)


router = APIRouter(
    prefix="/slo",
    tags=["SLO"],
)


@router.get("")
def get_slo_status():

    return slo_monitor.evaluate()
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.core.dependencies import get_auditory_service
from app.services.auditory_service import AuditoryService
from app.schemas.auditory import FreeAuditoryItem

router = APIRouter(prefix="/auditories")

@router.get("/free", response_model=list[FreeAuditoryItem])
async def get_free_auditories(
    day_of_week: str,
    week_number: int = Query(..., ge=1, le=4),
    time: str = Query(..., pattern=r"^\d{2}:\d{2}$"),
    building_number: int | None = Query(None, ge=1),
    service: AuditoryService = Depends(get_auditory_service),
) -> list[FreeAuditoryItem]:
    try:
        return await service.get_free_auditories(day_of_week, week_number, time, building_number)
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc
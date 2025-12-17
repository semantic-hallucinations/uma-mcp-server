from fastapi import APIRouter, Depends, HTTPException
from app.core.dependencies import get_system_service
from app.services.system_service import SystemService
from app.schemas.system import CurrentWeekResponse

router = APIRouter(prefix="/system")

@router.get("/current-week", response_model=CurrentWeekResponse)
async def get_current_week(
    service: SystemService = Depends(get_system_service),
) -> CurrentWeekResponse:
    try:
        week = await service.get_current_week()
        return CurrentWeekResponse(week_number=week)
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Service unavailable") from exc
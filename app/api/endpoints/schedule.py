import json
from typing import Any, Literal
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.core.dependencies import get_schedule_service
from app.services.schedule_service import ScheduleService

router = APIRouter(prefix="/schedule")
EntityType = Literal["group", "employee"]

@router.get("/{entity_type}/{entity_identifier}")
async def get_schedule(
    entity_type: EntityType,
    entity_identifier: str,
    service: ScheduleService = Depends(get_schedule_service),
):
    try:
        data = await service.get_schedule(entity_type, entity_identifier)
        return JSONResponse(content=data)
    except ValueError as exc:
        # Пытаемся понять, ошибка это 404, 409 или 503 по тексту ошибки (не идеально, но для совместимости)
        # В идеале нужно использовать кастомные Exception классы в сервисах.
        msg = str(exc)
        if "Ambiguous" in msg:
            try:
                detail = json.loads(msg)
            except:
                detail = msg
            raise HTTPException(status_code=409, detail=detail)
        if "not found" in msg:
             raise HTTPException(status_code=404, detail=msg)
        if "unavailable" in msg:
             raise HTTPException(status_code=503, detail=msg)
        
        raise HTTPException(status_code=400, detail=msg)
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc
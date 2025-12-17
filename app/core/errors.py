import logging
import json

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError


logger = logging.getLogger(__name__)


async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    """
    Обработчик ошибок базы данных.
    Ловит SQLAlchemyError и всё, что от него наследуется.
    """
    logger.error(f"Database error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=503,
        content={"detail": "Database unavailable"},
    )

async def value_error_handler(request: Request, exc: ValueError):
    """
    Обработчик ошибок валидации и бизнес-логики.
    """
    msg = str(exc)
    
    # 1. Проверяем, не JSON ли это (случай Ambiguous identifier)
    try:
        if msg.startswith("{") and "matches" in msg:
            data = json.loads(msg)
            return JSONResponse(status_code=409, content=data)
    except json.JSONDecodeError:
        pass

    msg_lower = msg.lower()
    
    if "not found" in msg_lower:
        return JSONResponse(status_code=404, content={"detail": msg})
    
    if "unavailable" in msg_lower:
        return JSONResponse(status_code=503, content={"detail": msg})

    return JSONResponse(status_code=400, content={"detail": msg})


def setup_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(SQLAlchemyError, database_exception_handler) # type: ignore
    app.add_exception_handler(ValueError, value_error_handler)             # type: ignore
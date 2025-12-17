from fastapi import HTTPException, Request, Depends
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncConnection

from app.services.auditory_service import AuditoryService
from app.services.structure_service import StructureService
from app.services.employee_service import EmployeeService
from app.services.schedule_service import ScheduleService
from app.services.system_service import SystemService


def get_settings(request: Request):
    return request.app.state.settings

def get_db_engine(request: Request):
    return request.app.state.db_engine

async def get_db_conn(request: Request):
    engine = request.app.state.db_engine
    try:
        async with engine.connect() as conn:
            yield conn
    except (OperationalError, OSError) as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc

def get_redis(request: Request):
    return request.app.state.redis

# --- Service Dependencies ---

def get_auditory_service(conn: AsyncConnection = Depends(get_db_conn)) -> AuditoryService:
    return AuditoryService(conn)

def get_structure_service(conn: AsyncConnection = Depends(get_db_conn)) -> StructureService:
    return StructureService(conn)

def get_employee_service(conn: AsyncConnection = Depends(get_db_conn)) -> EmployeeService:
    return EmployeeService(conn)

def get_system_service(
    conn: AsyncConnection = Depends(get_db_conn),
    redis = Depends(get_redis),
    settings = Depends(get_settings)
) -> SystemService:
    return SystemService(conn, redis, settings)

def get_schedule_service(
    conn: AsyncConnection = Depends(get_db_conn),
    redis = Depends(get_redis),
    settings = Depends(get_settings)
) -> ScheduleService:
    return ScheduleService(conn, redis, settings)
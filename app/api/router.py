from fastapi import APIRouter
 
from app.api.endpoints.auditories import router as auditories_router
from app.api.endpoints.structure import router as structure_router
from app.api.endpoints.employees import router as employees_router
from app.api.endpoints.schedule import router as schedule_router
from app.api.endpoints.system import router as system_router
 
api_router = APIRouter()
api_router.include_router(schedule_router, tags=["schedule"])
api_router.include_router(structure_router, tags=["structure"])
api_router.include_router(employees_router, tags=["employees"])
api_router.include_router(auditories_router, tags=["auditories"])
api_router.include_router(system_router, tags=["system"])

from fastapi import APIRouter, Depends, Query
from app.core.dependencies import get_employee_service
from app.services.employee_service import EmployeeService
from app.schemas.structure import Employee


router = APIRouter(prefix="/employees")


@router.get("/search", response_model=list[Employee])
async def employees_search(
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100),
    service: EmployeeService = Depends(get_employee_service),
) -> list[Employee]:
    return await service.search(q, limit=limit)
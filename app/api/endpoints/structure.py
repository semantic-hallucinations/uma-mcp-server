from fastapi import APIRouter, Depends, Query
from app.core.dependencies import get_structure_service
from app.services.structure_service import StructureService
from app.schemas.structure import Faculty, Department, Specialty, Group, Employee


router = APIRouter(prefix="/structure")


@router.get("/faculties", response_model=list[Faculty])
async def get_faculties(
    service: StructureService = Depends(get_structure_service),
) -> list[Faculty]:
    return await service.get_faculties()


@router.get("/departments", response_model=list[Department])
async def get_departments(
    service: StructureService = Depends(get_structure_service),
) -> list[Department]:
    return await service.get_departments()


@router.get("/specialities", response_model=list[Specialty])
async def get_specialities(
    faculty_id: int | None = Query(None),
    service: StructureService = Depends(get_structure_service),
) -> list[Specialty]:
    return await service.get_specialities(faculty_id=faculty_id)


@router.get("/groups", response_model=list[Group])
async def get_groups(
    specialty_id: int | None = Query(None),
    service: StructureService = Depends(get_structure_service),
) -> list[Group]:
    return await service.get_groups(specialty_id=specialty_id)


@router.get("/employees", response_model=list[Employee])
async def get_employees_structure(
    department_id: int | None = Query(None),
    service: StructureService = Depends(get_structure_service),
) -> list[Employee]:
    return await service.get_employees_by_department(department_id=department_id)
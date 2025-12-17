from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncConnection

from app.db.tables import faculties, departments, specialities, student_groups, employees, departments_employees
from app.schemas.structure import Faculty, Department, Specialty, Group, Employee


class StructureService:
    def __init__(self, conn: AsyncConnection):
        self.conn = conn

    async def get_faculties(self) -> list[Faculty]:
        query = select(faculties).order_by(faculties.c.id)
        result = await self.conn.execute(query)
        return [Faculty.model_validate(r) for r in result.mappings().all()]

    async def get_departments(self) -> list[Department]:
        query = select(departments).order_by(departments.c.id)
        result = await self.conn.execute(query)
        return [Department.model_validate(r) for r in result.mappings().all()]

    async def get_specialities(self, faculty_id: int | None = None) -> list[Specialty]:
        query = select(specialities).order_by(specialities.c.id)
        if faculty_id is not None:
            query = query.where(specialities.c.faculty_id == faculty_id)
        
        result = await self.conn.execute(query)
        return [Specialty.model_validate(r) for r in result.mappings().all()]

    async def get_groups(self, specialty_id: int | None = None) -> list[Group]:
        query = select(student_groups).where(student_groups.c.valid_to.is_(None))
        query = query.order_by(student_groups.c.id)
        
        if specialty_id is not None:
            query = query.where(student_groups.c.specialty_id == specialty_id)
        
        result = await self.conn.execute(query)
        return [Group.model_validate(r) for r in result.mappings().all()]

    async def get_employees_by_department(self, department_id: int | None = None) -> list[Employee]:
        if department_id is None:
            query = select(employees).order_by(employees.c.id)
        else:
            query = (
                select(employees)
                .join(departments_employees, departments_employees.c.employee_id == employees.c.id)
                .where(departments_employees.c.department_id == department_id)
                .order_by(employees.c.id)
            )

        result = await self.conn.execute(query)
        return [Employee.model_validate(r) for r in result.mappings().all()]
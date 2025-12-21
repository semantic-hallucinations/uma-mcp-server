from typing import Any

from sqlalchemy import select, or_, func, and_
from sqlalchemy.ext.asyncio import AsyncConnection

from app.db.tables import employees, departments_employees


class EmployeeService:
    def __init__(self, conn: AsyncConnection):
        self.conn = conn

    async def search(
        self, 
        q: str | None = None, 
        department_id: int | None = None, 
        limit: int = 20
    ) -> list[dict[str, Any]]:
        query = select(employees)
        
        if department_id:
            query = query.join(
                departments_employees, 
                departments_employees.c.employee_id == employees.c.id
            ).where(departments_employees.c.department_id == department_id)

        if q:
            clean_query = q.strip()
            full_name_concat = func.concat_ws(' ', employees.c.last_name, employees.c.first_name, employees.c.middle_name)
            
            fts_condition = func.to_tsvector('simple', full_name_concat).op('@@')(func.plainto_tsquery('simple', clean_query))
            ilike_condition = full_name_concat.ilike(f"%{clean_query}%")
            
            query = query.where(or_(fts_condition, ilike_condition))

        query = query.limit(limit)
        
        result = await self.conn.execute(query)
        return [dict(r) for r in result.mappings().all()]
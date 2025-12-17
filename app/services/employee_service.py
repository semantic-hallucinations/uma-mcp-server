from sqlalchemy.ext.asyncio import AsyncConnection
from app.db.employee_search import search_employees as db_search_employees
from app.schemas.structure import Employee


class EmployeeService:
    def __init__(self, conn: AsyncConnection):
        self.conn = conn

    async def search(self, query: str, limit: int = 20) -> list[Employee]:
        raw_data = await db_search_employees(self.conn, query, limit=limit)
        return [Employee.model_validate(row) for row in raw_data]
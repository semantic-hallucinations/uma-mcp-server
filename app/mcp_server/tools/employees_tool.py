from pydantic import BaseModel, Field

from app.mcp_server.sdk import registry, ToolContext
from app.services.employee_service import EmployeeService


class EmployeesSearchArgs(BaseModel):
    q: str = Field(..., min_length=1, description="Часть ФИО преподавателя (например, 'Иванов' или 'Иванов И.И.')")
    limit: int = Field(10, ge=1, le=50, description="Максимальное количество результатов")


@registry.tool(
    name="employees_search",
    description=(
        "Поиск преподавателей (сотрудников) по ФИО. "
        "Используйте этот инструмент, когда пользователь спрашивает о преподавателе, "
        "чтобы узнать его точный `url_id` или `id` для дальнейших запросов расписания."
    ),
    args_model=EmployeesSearchArgs
)
async def handle_employees_search(ctx: ToolContext, args: EmployeesSearchArgs):
    async with ctx.db_engine.connect() as conn:
        service = EmployeeService(conn)
        return await service.search(args.q, limit=args.limit)
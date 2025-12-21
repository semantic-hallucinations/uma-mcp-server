from pydantic import BaseModel, Field, model_validator

from app.mcp_server.sdk import registry, ToolContext
from app.services.employee_service import EmployeeService


class EmployeesFindArgs(BaseModel):
    q: str | None = Field(None, description=(
        "Часть ФИО (например, 'Иванов'). "
        "Если не указано, вернет всех сотрудников кафедры (требуется department_id)."
    ))
    department_id: int | None = Field(None, description=(
        "ID кафедры для фильтрации. Если указано, ищет только внутри этой кафедры." \
        "Можно узнать из инструмента directories_get, который вернёт все кафедры"
    ))
    limit: int | None = Field(None, description=(
        "Количество сотрудников, которое нужно найти. Оставляй пустым, если не указано иначе."
    ))

    @model_validator(mode='after')
    def check_args(self):
        if not self.q and not self.department_id:
            raise ValueError("Нужно указать хотя бы один параметр: 'q' (ФИО) или 'department_id'.")
        return self


@registry.tool(
    name="employees_find",
    description=(
        "Поиск преподавателей и сотрудников. "
        "Позволяет найти человека по ФИО, получить список всех сотрудников определенной кафедры "
        "или найти конкретного человека внутри кафедры."
    ),
    args_model=EmployeesFindArgs
)
async def handle_employees_find(ctx: ToolContext, args: EmployeesFindArgs):
    async with ctx.db_engine.connect() as conn:
        service = EmployeeService(conn)
        return await service.search(
            q=args.q, 
            department_id=args.department_id, 
            limit=500 if args.limit is None else int(args.limit)
        )
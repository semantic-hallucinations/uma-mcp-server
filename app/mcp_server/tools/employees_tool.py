from pydantic import BaseModel, Field

from app.mcp_server.sdk import registry, ToolContext
from app.services.employee_service import EmployeeService


class EmployeesSearchArgs(BaseModel):
    q: str = Field(..., min_length=1)
    limit: int = Field(20, ge=1, le=100)


@registry.tool(
    name="employees_search",
    description="Searches employees (teachers) by name.",
    args_model=EmployeesSearchArgs
)
async def handle_employees_search(ctx: ToolContext, args: EmployeesSearchArgs):
    async with ctx.db_engine.connect() as conn:
        service = EmployeeService(conn)
        return await service.search(args.q, limit=args.limit)
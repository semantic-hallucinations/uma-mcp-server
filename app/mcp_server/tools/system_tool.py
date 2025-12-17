from pydantic import BaseModel

from app.mcp_server.sdk import registry, ToolContext
from app.services.system_service import SystemService


class SystemCurrentWeekArgs(BaseModel):
    pass


@registry.tool(
    name="system_current_week",
    description="Returns current academic week number.",
    args_model=SystemCurrentWeekArgs
)
async def handle_current_week(ctx: ToolContext, args: SystemCurrentWeekArgs):
    async with ctx.db_engine.connect() as conn:
        service = SystemService(conn, ctx.redis, ctx.settings)
        week = await service.get_current_week()
        return {"week_number": week}
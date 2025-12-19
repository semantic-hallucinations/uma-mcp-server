from pydantic import BaseModel

from app.mcp_server.sdk import registry, ToolContext
from app.services.system_service import SystemService


class SystemCurrentWeekArgs(BaseModel):
    pass


@registry.tool(
    name="system_current_week",
    description=(
        "Возвращает номер текущей учебной недели (1-4). "
        "Используйте этот инструмент ПЕРВЫМ при любых вопросах, связанных с датами, "
        "расписанием на 'сегодня', 'завтра' или 'эту неделю', чтобы правильно фильтровать занятия."
    ),
    args_model=SystemCurrentWeekArgs
)
async def handle_current_week(ctx: ToolContext, args: SystemCurrentWeekArgs):
    async with ctx.db_engine.connect() as conn:
        service = SystemService(conn, ctx.redis, ctx.settings)
        week = await service.get_current_week()
        return {"week_number": week}
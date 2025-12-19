from typing import Literal
from pydantic import BaseModel, Field

from app.mcp_server.sdk import registry, ToolContext
from app.services.schedule_service import ScheduleService


class ScheduleGetArgs(BaseModel):
    entity_type: Literal["group", "employee"]
    entity_identifier: str = Field(..., description="Номер группы (например '221703') или ФИО/url_id преподавателя")


@registry.tool(
    name="schedule_get",
    description=(
        "ВНИМАНИЕ: ВОЗВРАЩАЕТ ОГРОМНЫЙ JSON СО ВСЕМ РАСПИСАНИЕМ НА ВЕСЬ СЕМЕСТР. "
        "Вызывать ТОЛЬКО в крайнем случае, если пользователь явно просит 'Покажи всё расписание целиком' "
        "и подтвердил это действие. ВСЕГДА спрашивай подтверждение пользователя"
        "Для конкретных вопросов ('какие пары во вторник?', 'когда математика?') используйте инструменты "
        "`schedule_get_day` или `schedule_search_event`."
    ),
    args_model=ScheduleGetArgs
)
async def handle_schedule_get(ctx: ToolContext, args: ScheduleGetArgs):
    async with ctx.db_engine.connect() as conn:
        service = ScheduleService(conn, ctx.redis, ctx.settings)
        return await service.get_schedule(args.entity_type, args.entity_identifier)
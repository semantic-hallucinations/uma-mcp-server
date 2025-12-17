from typing import Literal
from pydantic import BaseModel, Field

from app.mcp_server.sdk import registry, ToolContext
from app.services.schedule_service import ScheduleService


class ScheduleGetArgs(BaseModel):
    entity_type: Literal["group", "employee"]
    entity_identifier: str = Field(..., description="Group name (e.g. 221703) or Employee FIO/url_id")


@registry.tool(
    name="schedule_get",
    description="Returns full schedule JSON for a group or employee.",
    args_model=ScheduleGetArgs
)
async def handle_schedule_get(ctx: ToolContext, args: ScheduleGetArgs):
    async with ctx.db_engine.connect() as conn:
        service = ScheduleService(conn, ctx.redis, ctx.settings)
        return await service.get_schedule(args.entity_type, args.entity_identifier)
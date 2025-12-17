from pydantic import BaseModel, Field

from app.mcp_server.sdk import registry, ToolContext
from app.services.auditory_service import AuditoryService


class AuditoriesFreeArgs(BaseModel):
    day_of_week: str
    week_number: int = Field(..., ge=1, le=4)
    time: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    building_number: int | None = None


@registry.tool(
    name="auditories_free",
    description="Returns free auditories at a specific moment.",
    args_model=AuditoriesFreeArgs
)
async def handle_auditories_free(ctx: ToolContext, args: AuditoriesFreeArgs):
    async with ctx.db_engine.connect() as conn:
        service = AuditoryService(conn)
        return await service.get_free_auditories(
            day_of_week=args.day_of_week,
            week_number=args.week_number,
            time_str=args.time,
            building_number=args.building_number
        )
from pydantic import BaseModel, Field

from app.mcp_server.sdk import registry, ToolContext
from app.services.event_service import EventService


class ScheduleSearchEventArgs(BaseModel):
    q: str = Field(..., description="Subject name part (e.g. 'math', 'database')")
    entity_name: str = Field(..., description="Group name (221703) or Employee url_id (ivanov-i-i)")
    week_number: int | None = Field(None, description="Filter by week number")

@registry.tool(
    name="schedule_search_event",
    description="Finds specific lessons by subject name for a group or employee.",
    args_model=ScheduleSearchEventArgs
)
async def handle_search_event(ctx: ToolContext, args: ScheduleSearchEventArgs):
    async with ctx.db_engine.connect() as conn:
        service = EventService(conn)
        return await service.search_events(args.q, args.entity_name, args.week_number)


class AuditoryOccupancyArgs(BaseModel):
    auditory_name: str = Field(..., description="Auditory number (e.g. '305-2 к.', '501-2 к.')")
    week_number: int = Field(..., description="Academic week number")
    day_of_week: int = Field(..., description="Day number (1=Monday, 7=Sunday)")
    time: str | None = Field(None, description="Specific time to check (HH:MM), e.g. '10:30'. If empty, returns all events for the day.")

@registry.tool(
    name="auditories_occupancy_check",
    description="Checks who is currently in a specific auditory or lists events for the day.",
    args_model=AuditoryOccupancyArgs
)
async def handle_auditory_occupancy(ctx: ToolContext, args: AuditoryOccupancyArgs):
    async with ctx.db_engine.connect() as conn:
        service = EventService(conn)
        return await service.get_auditory_events(
            auditory_name=args.auditory_name,
            week_number=args.week_number,
            day_of_week=args.day_of_week,
            time_check=args.time
        )


class GlobalSubjectSearchArgs(BaseModel):
    q: str = Field(..., description="Subject name to search globally")
    limit: int = Field(10, le=50)

@registry.tool(
    name="global_subject_search",
    description="Searches for a subject globally to find which groups or employees have it. Useful for 'Who teaches X?'.",
    args_model=GlobalSubjectSearchArgs
)
async def handle_global_search(ctx: ToolContext, args: GlobalSubjectSearchArgs):
    async with ctx.db_engine.connect() as conn:
        service = EventService(conn)
        return await service.global_subject_search(args.q, args.limit)
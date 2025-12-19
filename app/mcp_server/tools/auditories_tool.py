from pydantic import BaseModel, Field

from app.mcp_server.sdk import registry, ToolContext
from app.services.auditory_service import AuditoryService


class AuditoriesFreeArgs(BaseModel):
    day_of_week: str = Field(..., description="День недели полное название (например: 'Понедельник', 'Вторник')")
    week_number: int = Field(..., ge=1, le=4, description="Номер учебной недели (1-4). Получите через system_current_week.")
    time: str = Field(..., pattern=r"^\d{2}:\d{2}$", description="Время в формате ЧЧ:ММ (например, '10:30')")
    building_number: int | None = Field(None, description="Номер учебного корпуса (опционально, например 4 или 5)")


@registry.tool(
    name="auditories_free",
    description=(
        "Поиск списка СВОБОДНЫХ аудиторий в заданный момент времени. "
        "Используйте, когда студент ищет пустое место для самостоятельной работы. "
        "Обязательно уточните номер корпуса, если пользователь не указал."
    ),
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
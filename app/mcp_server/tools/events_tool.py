from pydantic import BaseModel, Field

from app.mcp_server.sdk import registry, ToolContext
from app.services.event_service import EventService


class ScheduleSearchEventArgs(BaseModel):
    q: str = Field(..., description="Название предмета или его часть (например, 'математика', 'базы данных', 'физика')")
    entity_name: str = Field(..., description="Номер группы (например, '221703') или url_id преподавателя (например, 'ivanov-i-i')")
    week_number: int | None = Field(None, description="Номер учебной недели для фильтрации")

@registry.tool(
    name="schedule_search_event",
    description=(
        "Поиск конкретных занятий (лекций, лабораторных) по названию предмета в расписании группы или преподавателя. "
        "Используйте это вместо получения полного расписания, если пользователь спрашивает: "
        "'Когда у меня математика?', 'Во сколько лекция по БД?', 'В какой аудитории физика?'."
    ),
    args_model=ScheduleSearchEventArgs
)
async def handle_search_event(ctx: ToolContext, args: ScheduleSearchEventArgs):
    async with ctx.db_engine.connect() as conn:
        service = EventService(conn)
        return await service.search_events(args.q, args.entity_name, args.week_number)


class AuditoryOccupancyArgs(BaseModel):
    auditory_name: str = Field(..., description="Номер аудитории (например, '305-2', '501-2')")
    week_number: int = Field(..., description="Номер учебной недели (1-4)")
    day_of_week: int = Field(..., description="Порядковый номер дня недели (1=Понедельник, 7=Воскресенье)")
    time: str | None = Field(None, description="Время проверки (ЧЧ:ММ). Если не указано, вернет все занятия в этой аудитории за день.")

@registry.tool(
    name="auditories_occupancy_check",
    description=(
        "Проверка занятости КОНКРЕТНОЙ аудитории. "
        "Позволяет узнать, кто сейчас занимается в аудитории ('Какая группа сейчас в 305-2?') "
        "или получить список всех пар в этой аудитории на день."
        "Имя аудитории должно быть в формате {214-4 к.}, где 214 это номер аудитории, 4 к. это 4 корпус"
    ),
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

class ScheduleDayArgs(BaseModel):
    entity_name: str = Field(..., description="Номер группы (например '221703') или url_id преподавателя")
    day_of_week: int = Field(..., description="Порядковый номер дня недели (1=Понедельник, 7=Воскресенье)")
    week_number: int = Field(..., description="Номер учебной недели (1-4)")

@registry.tool(
    name="schedule_get_day",
    description=(
        "Получение расписания на ОДИН конкретный день. "
        "Используйте это ВМЕСТО `schedule_get` для вопросов вида: 'Какие пары завтра?', 'Что у меня в среду?', 'Расписание на понедельник'. "
        "Возвращает список занятий только на указанный день."
    ),
    args_model=ScheduleDayArgs
)
async def handle_schedule_day(ctx: ToolContext, args: ScheduleDayArgs):
    async with ctx.db_engine.connect() as conn:
        service = EventService(conn)
        return await service.get_day_events(
            entity_name=args.entity_name,
            week_number=args.week_number,
            day_of_week=args.day_of_week
        )

class GlobalSubjectSearchArgs(BaseModel):
    q: str = Field(..., description="Название предмета")
    limit: int = Field(10, le=50)

@registry.tool(
    name="global_subject_search",
    description=(
        "Глобальный поиск по всем расписаниям. "
        "Используйте ТОЛЬКО для вопросов вида: 'Кто ведет Нейронные сети?', 'У каких групп есть Философия?'. "
        "Позволяет найти преподавателей или группы, связанные с предметом."
    ),
    args_model=GlobalSubjectSearchArgs
)
async def handle_global_search(ctx: ToolContext, args: GlobalSubjectSearchArgs):
    async with ctx.db_engine.connect() as conn:
        service = EventService(conn)
        return await service.global_subject_search(args.q, args.limit)
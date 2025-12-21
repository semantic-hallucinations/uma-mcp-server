from datetime import time, datetime
from typing import Literal, Any

from sqlalchemy import select, and_, or_, func, cast, Time, distinct
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncConnection

from app.db.tables import schedule_events, employees
from app.schemas.events import ScheduleEventItem, EmployeeFromEvent


class EventService:
    def __init__(self, conn: AsyncConnection):
        self.conn = conn

    def _build_base_query(self):
        """
        Строит базовый запрос с JOIN к таблице сотрудников,
        чтобы сразу получать ФИО, если entity_name == url_id.
        """
        return select(
            schedule_events,
            employees.c.last_name,
            employees.c.first_name,
            employees.c.middle_name
        ).outerjoin(
            employees,
            and_(
                schedule_events.c.entity_type == 'employee',
                schedule_events.c.entity_name == employees.c.url_id
            )
        )

    def _process_row(self, row: Any) -> ScheduleEventItem:
        """
        Преобразует строку БД в Pydantic-модель с красивыми именами.
        """
        # Преобразуем RowMapping в dict
        row_dict = dict(row)
        
        if row_dict.get("last_name"):
            parts = [
                row_dict["last_name"], 
                row_dict.get("first_name"), 
                row_dict.get("middle_name")
            ]
            display_name = " ".join(filter(None, parts))
        else:
            display_name = row_dict["entity_name"]

        teachers_display = []
        raw_related = row_dict.get("related_employees")
        
        if isinstance(raw_related, list):
            for t in raw_related:
                if isinstance(t, dict):
                    t_parts = [
                        t.get("lastName"), 
                        t.get("firstName"), 
                        t.get("middleName")
                    ]
                    if any(t_parts):
                        teachers_display.append(" ".join(filter(None, t_parts)))
                    elif t.get("urlId"):
                        teachers_display.append(t["urlId"])
        
        return ScheduleEventItem(
            **row_dict,
            entity_display_name=display_name,
            teachers_display_names=teachers_display
        )

    async def search_events(
        self, 
        q: str, 
        entity_name: str, 
        week_number: int | None = None
    ) -> list[ScheduleEventItem]:
        
        query = self._build_base_query().where(
            and_(
                schedule_events.c.entity_name == entity_name,
                or_(
                    schedule_events.c.subject.ilike(f"%{q}%"),
                    schedule_events.c.subject_full.ilike(f"%{q}%")
                )
            )
        )

        if week_number:
            query = query.where(schedule_events.c.week_numbers.any(week_number))

        query = query.order_by(schedule_events.c.day_of_week, schedule_events.c.start_time)

        result = await self.conn.execute(query)
        return [self._process_row(r) for r in result.mappings().all()]

    async def get_auditory_events(
        self,
        auditory_name: str,
        week_number: int,
        day_of_week: int,
        time_check: str | None = None
    ) -> list[ScheduleEventItem]:
        
        query = select(schedule_events).where(
            schedule_events.c.auditories.any(auditory_name)
        )

        query = query.where(schedule_events.c.week_numbers.any(week_number))
        query = query.where(schedule_events.c.day_of_week == day_of_week)

        if time_check:
            try:
                time_obj = datetime.strptime(time_check, "%H:%M").time()
            except ValueError:
                raise ValueError(f"Invalid time format: {time_check}. Expected HH:MM")

            query = query.where(and_(
                schedule_events.c.start_time <= time_obj,
                schedule_events.c.end_time > time_obj
            ))

        query = query.order_by(schedule_events.c.start_time)

        result = await self.conn.execute(query)
        return [ScheduleEventItem.model_validate(r) for r in result.mappings().all()]
    
    async def get_day_events(
        self,
        entity_name: str,
        week_number: int,
        day_of_week: int
    ) -> list[ScheduleEventItem]:
        """
        Возвращает расписание сущности на конкретный день недели.
        """
        query = select(schedule_events).where(
            and_(
                schedule_events.c.entity_name == entity_name,
                schedule_events.c.day_of_week == day_of_week,
                schedule_events.c.week_numbers.any(week_number)
            )
        )
        
        query = query.order_by(schedule_events.c.start_time)

        result = await self.conn.execute(query)
        return [ScheduleEventItem.model_validate(r) for r in result.mappings().all()]

    async def global_subject_search(
        self,
        q: str,
        limit: int = 10
    ) -> list[ScheduleEventItem]:
        
        query = self._build_base_query().where(
             or_(
                schedule_events.c.subject.ilike(f"%{q}%"),
                schedule_events.c.subject_full.ilike(f"%{q}%")
            )
        )
        
        query = query.limit(limit)
        
        result = await self.conn.execute(query)
        return [self._process_row(r) for r in result.mappings().all()]


    async def get_employees_by_group(self, group_name: str) -> list[EmployeeFromEvent]:
        elem = func.jsonb_array_elements(
            cast(schedule_events.c.related_employees, JSONB)
        ).column_valued("elem")
        
        query = (
            select(
                distinct(elem.op("->>")("urlId")).label("url_id"),
                elem.op("->>")("lastName").label("last_name"),
                elem.op("->>")("firstName").label("first_name"),
                elem.op("->>")("middleName").label("middle_name")
            )
            .select_from(schedule_events)
            .where(schedule_events.c.entity_name == group_name)
            .where(schedule_events.c.related_employees.is_not(None))
        )
        
        result = await self.conn.execute(query)
        return [EmployeeFromEvent(**dict(r)) for r in result.mappings().all()]
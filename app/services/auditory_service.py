from datetime import datetime # <--- Добавляем импорт
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncConnection

from app.db.tables import auditories, occupancy_index
from app.schemas.auditory import FreeAuditoryItem

class AuditoryService:
    def __init__(self, conn: AsyncConnection):
        self.conn = conn

    async def get_free_auditories(
        self,
        day_of_week: str,
        week_number: int,
        time_str: str,
        building_number: int | None = None
    ) -> list[FreeAuditoryItem]:
        
        try:
            check_time = datetime.strptime(time_str, "%H:%M").time()
        except ValueError:
            raise ValueError("Invalid time format. Use HH:MM")

        occupancy_subquery = (
            select(1)
            .where(
                and_(
                    occupancy_index.c.auditory_id == auditories.c.id,
                    occupancy_index.c.day_of_week == day_of_week,
                    occupancy_index.c.week_number == week_number,
                    occupancy_index.c.start_time <= check_time,
                    occupancy_index.c.end_time > check_time
                )
            )
            .exists()
        )

        query = (
            select(auditories.c.name, auditories.c.capacity, auditories.c.auditory_type)
            .where(~occupancy_subquery)
            .order_by(auditories.c.name)
        )

        if building_number is not None:
            query = query.where(auditories.c.building_number == str(building_number))

        result = await self.conn.execute(query)
        rows = result.mappings().all()
        return [FreeAuditoryItem(**dict(r)) for r in rows]
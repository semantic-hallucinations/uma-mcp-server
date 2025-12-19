import json
from typing import Any, Literal
from redis.asyncio import Redis
from redis.exceptions import RedisError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncConnection

from app.core.config import Settings
from app.core.redis_keys import RedisKeys
from app.db.tables import student_groups, employees, schedule_storage
from app.db.employee_search import resolve_employee_identifier


EntityType = Literal["group", "employee"]


class ScheduleService:
    def __init__(
        self, 
        conn: AsyncConnection, 
        redis: Redis, 
        settings: Settings
    ):
        self.conn = conn
        self.redis = redis
        self.settings = settings

    async def get_schedule(self, entity_type: EntityType, entity_identifier: str) -> Any:

        redis_key, db_lookup_val = await self._resolve_identifier(entity_type, entity_identifier)

        try:
            cached = await self.redis.get(redis_key)
            if cached:
                return json.loads(cached)
        except (RedisError, json.JSONDecodeError):
            pass 

        if db_lookup_val is not None:
            schedule_data = await self._fetch_from_db_scd2(entity_type, db_lookup_val)
            if schedule_data:
                try:
                    await self.redis.setex(
                        redis_key, 
                        self.settings.redis_schedule_cache_ttl, 
                        json.dumps(schedule_data, ensure_ascii=False)
                    )
                except RedisError:
                    pass
                
                return schedule_data

        raise ValueError("Schedule not found")

    async def _resolve_identifier(self, entity_type: str, identifier: str) -> tuple[str, str | int | None]:
        """
        Возвращает (Redis Key, Database Lookup Value)
        Database Lookup Value: 
           - для групп: строка имени ("221703")
           - для сотрудников: int ID (5050)
        """
        if entity_type == "group":
            
            key = RedisKeys.schedule(entity_type, identifier)
            return key, identifier

        if entity_type == "employee":
            _, resolved_url_id, matches = await resolve_employee_identifier(self.conn, identifier)
            
            if not resolved_url_id:
                if matches:
                     raise ValueError(json.dumps({"message": "Ambiguous identifier", "matches": matches}))
                return RedisKeys.schedule(entity_type, identifier), None

            query = select(employees.c.id).where(employees.c.url_id == resolved_url_id)
            res = await self.conn.execute(query)
            row = res.mappings().first()
            
            return RedisKeys.schedule(entity_type, resolved_url_id), row["id"] if row else None

        raise ValueError("Unknown entity type")

    async def _fetch_from_db_scd2(self, entity_type: str, lookup_val: str | int) -> Any | None:
        """
        Ищет актуальное расписание (valid_to IS NULL).
        """
        query = select(schedule_storage.c.data).where(
            schedule_storage.c.valid_to.is_(None)
        )

        if entity_type == "group":
            query = query.where(schedule_storage.c.group_name == str(lookup_val))
        else:
            query = query.where(schedule_storage.c.employee_id == int(lookup_val))

        query = query.order_by(schedule_storage.c.api_last_update_ts.desc().nulls_last()).limit(1)

        result = await self.conn.execute(query)
        row = result.mappings().first()
        return row["data"] if row else None
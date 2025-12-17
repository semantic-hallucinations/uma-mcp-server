from redis.asyncio import Redis
from redis.exceptions import RedisError

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncConnection

from app.core.config import Settings
from app.db.tables import system_state
from app.core.redis_keys import RedisKeys


class SystemService:
    def __init__(self, conn: AsyncConnection, redis: Redis, settings: Settings):
        self.conn = conn
        self.redis = redis
        self.settings = settings

    async def get_current_week(self) -> int:
        cache_key = RedisKeys.SYSTEM_CURRENT_WEEK

        try:
            cached = await self.redis.get(cache_key)
            if cached:
                return int(cached)
        except (RedisError, ValueError):
            pass

        query = select(system_state.c.value).where(system_state.c.key == "current_week")
        result = await self.conn.execute(query)
        val = result.scalar()

        if val is None:
            raise ValueError("Current week not found in System State")

        week_number = int(val)

        try:
            await self.redis.setex(
                cache_key, 
                self.settings.redis_curr_week_cache_ttl, 
                str(week_number)
            )
        except RedisError:
            pass

        return week_number
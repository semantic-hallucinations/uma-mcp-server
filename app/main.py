from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import Settings
from app.core.errors import setup_exception_handlers
from app.db.session import create_engine
from app.services.cache_service import create_redis_client

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = Settings()

    app.state.settings = settings
    app.state.db_engine = create_engine(str(settings.database_url))
    app.state.redis = create_redis_client(settings.redis_host, settings.redis_port)

    try:
        try:
            from app.mcp_server.mount import mount_mcp

            mount_mcp(app)
        except ModuleNotFoundError as exc:
            missing = exc.name or ""
            if missing == "mcp" or missing.startswith("mcp.") or missing == "sse_starlette":
                logger.warning("MCP dependencies are missing; /mcp endpoints will be disabled")
            else:
                raise
        yield
    finally:
        aclose = getattr(app.state.redis, "aclose", None)
        if callable(aclose):
            aclose()
        else:
            await app.state.redis.close()
            
        await app.state.db_engine.dispose()


app = FastAPI(title="bsuir-mcp-api", lifespan=lifespan)

setup_exception_handlers(app)

app.include_router(api_router)
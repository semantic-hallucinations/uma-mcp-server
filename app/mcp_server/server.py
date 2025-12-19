from __future__ import annotations
from typing import Any
import mcp.types as types
from mcp.server.lowlevel import Server

from app.mcp_server.sdk import registry, ToolContext
import app.mcp_server.tools.auditories_tool
import app.mcp_server.tools.employees_tool
import app.mcp_server.tools.schedule_tool
import app.mcp_server.tools.structure_tool
import app.mcp_server.tools.system_tool
import app.mcp_server.tools.events_tool


def create_mcp_server(runtime) -> Server:
    server = Server("bsuir-mcp-api")

    @server.list_tools()
    async def list_tools() -> list[types.Tool]:
        return registry.tools

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[types.ContentBlock]:
        context = ToolContext(
            db_engine=runtime.db_engine,
            redis=runtime.redis,
            settings=runtime.settings
        )
        
        return await registry.call(name, arguments, context)

    return server
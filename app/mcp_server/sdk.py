from __future__ import annotations
import json
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Type

from pydantic import BaseModel
import mcp.types as types
from sqlalchemy.ext.asyncio import AsyncEngine
from redis.asyncio import Redis

from app.core.config import Settings


@dataclass
class ToolContext:
    db_engine: AsyncEngine
    redis: Redis
    settings: Settings


class ToolRegistry:
    def __init__(self):
        self._tools_metadata: list[types.Tool] = []
        self._handlers: dict[str, Callable[..., Awaitable[Any]]] = {}
        self._arg_models: dict[str, Type[BaseModel]] = {}

    def tool(self, name: str, description: str, args_model: Type[BaseModel]):
        def decorator(func):
            schema = args_model.model_json_schema()
            
            if "title" in schema:
                del schema["title"]

            self._tools_metadata.append(
                types.Tool(
                    name=name,
                    description=description,
                    inputSchema=schema
                )
            )

            self._handlers[name] = func
            self._arg_models[name] = args_model
            return func
        return decorator

    @property
    def tools(self) -> list[types.Tool]:
        return self._tools_metadata

    async def call(self, name: str, arguments: dict[str, Any], context: ToolContext) -> list[types.ContentBlock]:
        handler = self._handlers.get(name)
        model = self._arg_models.get(name)

        if not handler or not model:
            raise ValueError(f"Unknown tool: {name}")

        try:
            validated_args = model.model_validate(arguments)
        except Exception as e:
            raise ValueError(f"Invalid arguments for tool {name}: {e}")

        try:
            result = await handler(context, validated_args)
            
            return [self._format_result(result)]
        except Exception as e:
            return [types.TextContent(type="text", text=json.dumps({"error": str(e)}, ensure_ascii=False))]

    def _format_result(self, value: Any) -> types.TextContent:
        if isinstance(value, list) and value and hasattr(value[0], "model_dump"):
            data = [item.model_dump(mode="json") for item in value]
        elif hasattr(value, "model_dump"):
            data = value.model_dump(mode="json")
        else:
            data = value
        
        return types.TextContent(type="text", text=json.dumps(data, ensure_ascii=False))


registry = ToolRegistry()
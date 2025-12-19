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
    """Контекст, доступный внутри функции инструмента"""
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
            # 1. Генерируем JSON Schema из Pydantic модели
            schema = args_model.model_json_schema()
            
            # 2. Очищаем схему для совместимости с LLM (Gemini/OpenAI)
            schema = self._sanitize_schema(schema)

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

    def _sanitize_schema(self, schema: dict) -> dict:
        """
        Удаляет конструкции Pydantic (anyOf, type: [t, null]), которые ломают Gemini/n8n.
        Превращает Optional[T] просто в T.
        """
        new_schema = schema.copy()
        
        if "title" in new_schema:
            del new_schema["title"]
            
        if "properties" in new_schema:
            for prop_name, prop_def in new_schema["properties"].items():
                # Исправляем type: ["string", "null"] -> type: "string"
                if isinstance(prop_def.get("type"), list):
                    valid_types = [t for t in prop_def["type"] if t != "null"]
                    if valid_types:
                        prop_def["type"] = valid_types[0]
                
                # Исправляем anyOf: [{type: string}, {type: null}] -> type: "string"
                if "anyOf" in prop_def:
                    for option in prop_def["anyOf"]:
                        if option.get("type") and option.get("type") != "null":
                            # Копируем свойства из варианта (type, format и т.д.)
                            prop_def.update(option)
                            break
                    del prop_def["anyOf"]
                    
                # Чистим title внутри свойств (мусор для LLM)
                if "title" in prop_def:
                    del prop_def["title"]

        # Если есть определения ($defs), их тоже надо почистить (обычно Pydantic инлайнит, но на всякий случай)
        if "$defs" in new_schema:
            del new_schema["$defs"]

        return new_schema

    @property
    def tools(self) -> list[types.Tool]:
        return self._tools_metadata

    async def call(self, name: str, arguments: dict[str, Any], context: ToolContext) -> list[types.ContentBlock]:
        handler = self._handlers.get(name)
        model = self._arg_models.get(name)

        if not handler or not model:
            raise ValueError(f"Unknown tool: {name}")

        try:
            # Pydantic сам разберется с типами при валидации
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
from __future__ import annotations
from typing import Iterable

from fastapi import FastAPI
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response
from starlette.routing import Mount, Route

from app.mcp_server.server import create_mcp_server


class McpSecurityMiddleware:
    def __init__(self, app, *, auth_token: str | None, allowed_origins: Iterable[str] | None):
        self._app = app
        self._auth_token = auth_token
        self._allowed_origins = set(allowed_origins or [])

    async def __call__(self, scope, receive, send):
        if scope.get("type") == "http":
            headers = {k.decode("latin-1"): v.decode("latin-1") for k, v in scope.get("headers", [])}

            origin = headers.get("origin")
            if origin and self._allowed_origins and origin not in self._allowed_origins:
                return await PlainTextResponse("Forbidden", status_code=403)(scope, receive, send)

            if self._auth_token:
                expected = f"Bearer {self._auth_token}"
                if headers.get("authorization") != expected:
                    return await PlainTextResponse("Unauthorized", status_code=401)(scope, receive, send)

        return await self._app(scope, receive, send)


def mount_mcp(app: FastAPI) -> None:
    from mcp.server.sse import SseServerTransport

    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request):
        runtime = request.app.state.parent_fastapi.state
        mcp_server = create_mcp_server(runtime)
        async with sse.connect_sse(request.scope, request.receive, request._send) as streams:  # type: ignore[attr-defined]
            await mcp_server.run(streams[0], streams[1], mcp_server.create_initialization_options())
        return Response()

    starlette_app = Starlette(
        routes=[
            Route("/sse", endpoint=handle_sse, methods=["GET"]),
            Mount("/messages/", app=sse.handle_post_message),
        ]
    )

    starlette_app.state.parent_fastapi = app
    settings = app.state.settings

    token_value = settings.mcp_auth_token.get_secret_value() if settings.mcp_auth_token else None
    
    origins_list = settings.mcp_allowed_origins

    secured = McpSecurityMiddleware(
        starlette_app,
        auth_token=token_value,
        allowed_origins=origins_list,
    )

    app.mount("/mcp", secured)


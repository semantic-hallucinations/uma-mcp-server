from __future__ import annotations
from typing import Any

from sqlalchemy import select, text, func, or_
from sqlalchemy.ext.asyncio import AsyncConnection

from app.db.tables import employees


async def search_employees(conn: AsyncConnection, query: str, *, limit: int = 20) -> list[dict[str, Any]]:
    clean_query = query.strip()
    if not clean_query:
        return []

    limit_value = max(1, min(int(limit), 100))

    full_name_concat = func.concat_ws(' ', employees.c.last_name, employees.c.first_name, employees.c.middle_name)

    fts_condition = func.to_tsvector('simple', full_name_concat).op('@@')(func.plainto_tsquery('simple', clean_query))

    ilike_condition = full_name_concat.ilike(f"%{clean_query}%")

    stmt = (
        select(employees)
        .where(or_(fts_condition, ilike_condition))
        .limit(limit_value)
    )

    result = await conn.execute(stmt)
    return [dict(r) for r in result.mappings().all()]


async def resolve_employee_identifier(
    conn: AsyncConnection,
    identifier: str,
    *,
    limit: int = 5,
) -> tuple[int, str, list[dict[str, Any]]]:
    """
    Пытается найти сотрудника по:
    1. ID (число)
    2. url_id (строка)
    3. Поиск по ФИО
    """
    normalized = identifier.strip()

    if normalized.isdigit():
        return int(normalized), normalized, []

    stmt_url = select(employees.c.id).where(employees.c.url_id == normalized).limit(1)
    result_url = await conn.execute(stmt_url)
    row_url = result_url.mappings().first()
    
    if row_url:
        return int(row_url["id"]), normalized, []

    matches = await search_employees(conn, normalized, limit=limit)
    
    if len(matches) == 1:
        match = matches[0]
        resolved_id = int(match["id"])
        resolved_url_id = match.get("url_id") or str(resolved_id)
        return resolved_id, resolved_url_id, []

    return -1, normalized, matches
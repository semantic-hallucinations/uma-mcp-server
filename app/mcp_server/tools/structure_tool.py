from typing import Literal
from pydantic import BaseModel, Field

from app.mcp_server.sdk import registry, ToolContext
from app.services.structure_service import StructureService


class DirectoriesGetArgs(BaseModel):
    directory_name: Literal["faculties", "departments", "specialities", "groups"]
    faculty_id: int | None = Field(None, description="ID факультета (обязательно для directory_name='specialities')")
    specialty_id: int | None = Field(None, description="ID специальности (обязательно для directory_name='groups')")


@registry.tool(
    name="directories_get",
    description=(
        "Получение списков структурных подразделений университета. "
        "Используйте для навигации по иерархии: Факультеты -> Специальности -> Группы. "
        "Не используйте для поиска людей."
    ),
    args_model=DirectoriesGetArgs
)
async def handle_directories(ctx: ToolContext, args: DirectoriesGetArgs):
    async with ctx.db_engine.connect() as conn:
        service = StructureService(conn)
        
        if args.directory_name == "faculties":
            return await service.get_faculties()
        elif args.directory_name == "departments":
            return await service.get_departments()
        elif args.directory_name == "specialities":
            return await service.get_specialities(faculty_id=args.faculty_id)
        elif args.directory_name == "groups":
            return await service.get_groups(specialty_id=args.specialty_id)
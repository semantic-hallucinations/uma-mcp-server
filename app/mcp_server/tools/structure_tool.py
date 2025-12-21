from typing import Literal
from pydantic import BaseModel, Field

from app.mcp_server.sdk import registry, ToolContext
from app.services.structure_service import StructureService


class DirectoriesGetArgs(BaseModel):
    directory_name: Literal["faculties", "departments", "specialities", "groups", "auditories"]
    faculty_id: int | None = Field(None, description="ID факультета (обязательно для directory_name='specialities')")
    specialty_id: int | None = Field(None, description="ID специальности (обязательно для directory_name='groups')")


@registry.tool(
    name="directories_get",
    description=(
        "Получение списков структурных подразделений университета. "
        "Получение списков: факультеты, кафедры, аудитории, специальности, группы"
        "ВАЖНО для списков:"
        "Факультеты: используйте всегда когда необходимо узнать полную информацию о факультетах;"
        "Кафедры: используйте всегда когда необходимо узнать полную информацию о кафедрах;"
        "Аудитории: используйте для получени списка всех аудиторий, и когда нужно узнать,"
        "относятся ли аудитории к какому-либо корпусу и т.д.;"
        "Специальности: используйте всегда когда необходим доступ к специальностям конкретной кафедры;"
        "Группы: используйте всегда когда необходим доступ к группам конкретной специальности;"
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
        elif args.directory_name == "auditories":
            return await service.get_auditories()
        elif args.directory_name == "specialities":
            return await service.get_specialities(faculty_id=args.faculty_id)
        elif args.directory_name == "groups":
            return await service.get_groups(specialty_id=args.specialty_id)

class GroupInfoArgs(BaseModel):
    group_name: str = Field(..., description="Номер группы (например, '221703')")


@registry.tool(
    name="structure_group_info",
    description="Получение детальной информации о группе: специальность, курс, факультет.",
    args_model=GroupInfoArgs
)
async def handle_group_info(ctx: ToolContext, args: GroupInfoArgs):
    async with ctx.db_engine.connect() as conn:
        service = StructureService(conn)
        info = await service.get_group_info(args.group_name)
        if not info:
            return {"error": f"Группа {args.group_name} не найдена."}
        return info
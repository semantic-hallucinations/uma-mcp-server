from pydantic import BaseModel, ConfigDict, Field

class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class Faculty(BaseSchema):
    id: int
    name: str
    abbr: str

class Department(BaseSchema):
    id: int
    name: str
    abbr: str
    url_id: str

class Specialty(BaseSchema):
    id: int
    name: str
    faculty_id: int

class Group(BaseSchema):
    id: int
    name: str
    specialty_id: int

class Employee(BaseSchema):
    id: int
    first_name: str
    last_name: str
    middle_name: str
    url_id: str
    photo_link: str | None = None
    degree: str | None = None
    rank: str | None = None
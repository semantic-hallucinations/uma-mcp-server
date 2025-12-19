from pydantic import BaseModel, ConfigDict

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
    course: int | None = None
    education_degree: int
    number_of_students: int | None = None

class Employee(BaseSchema):
    id: int
    first_name: str
    last_name: str
    url_id: str
    middle_name: str | None = None
    photo_link: str | None = None
    degree: str | None = None
    rank: str | None = None
    calendar_id: str | None = None
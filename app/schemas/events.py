from datetime import date, time
from pydantic import BaseModel, ConfigDict, Field


class ScheduleEventItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    subject: str
    subject_full: str | None = None
    week_numbers: list[int]
    day_of_week: int | None = None
    start_time: time
    end_time: time
    auditories: list[str]
    
    entity_name: str 
    entity_type: str 
    
    entity_display_name: str | None = Field(None, description="Human readable name (FIO or Group Name)")
    
    teachers_display_names: list[str] = Field(default_factory=list, description="List of teachers names (FIO)")
    
    lesson_type: str | None = None
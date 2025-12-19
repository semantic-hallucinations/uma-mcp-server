from pydantic import BaseModel, ConfigDict

class FreeAuditoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    name: str
    capacity: int | None = None
    auditory_type: str | None = None
    building_number: str | None = None
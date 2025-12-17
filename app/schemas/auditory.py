from pydantic import BaseModel


class FreeAuditoryItem(BaseModel):
    name: str
    capacity: int
    auditory_type: str

from pydantic import BaseModel


class CurrentWeekResponse(BaseModel):
    week_number: int

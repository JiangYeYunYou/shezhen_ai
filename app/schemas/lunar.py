from datetime import date
from pydantic import BaseModel


class LunarCalendarResponse(BaseModel):
    date: str
    lunar_date: str
    ganzhi: str
    weekday: str
    season: str
    festival: str
    yi: list[str]
    ji: list[str]

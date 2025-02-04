from datetime import datetime
from pydantic import BaseModel, Field

from src.models.modes import Mode

class Listing(BaseModel):
    id: int|None = Field(init = False, default = None)
    link: str
    mode: Mode
    startdate: datetime|None = Field(init = False, default = None)
    enddate: datetime|None = Field(init = False, default = None)
    successful: bool = Field(default = False)
    attempts: int = Field(init = False, default = 0)
    
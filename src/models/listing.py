from datetime import datetime
from pydantic import BaseModel, Field

from models.modes import Mode

class Listing(BaseModel):
    id: int|None = Field(init = False, default = None)
    link: str
    mode: Mode
    startdate: datetime|None = Field(init = False, default = None)
    enddate: datetime|None = Field(init = False, default = None)
    successful: bool = Field(default = False)
    attemps: int = Field(init = False, default = 0)
    


    #   - link
    #   - startdate
    #   - enddate
    #   - successful
    #   - primary key
    #   - unique key
    #   - id
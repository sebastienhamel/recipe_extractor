from datetime import datetime
from pydantic import BaseModel

class Listing(BaseModel):
    id: int
    link: str
    startdate: datetime
    enddate: datetime
    successful: bool
    


    #   - link
    #   - startdate
    #   - enddate
    #   - successful
    #   - primary key
    #   - unique key
    #   - id
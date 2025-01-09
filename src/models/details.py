import datetime
from types import List
from pydantic import BaseModel

class Ingredient(BaseModel):
    quantity: float
    ingredient_name: str

class Method(BaseModel):
    step_number: int
    instruction: str

class Recipe(BaseModel):
    ingredients: List[Ingredient]
    method: List[Method]

class Details(BaseModel):
    id: int
    link: str
    startdate: datetime
    enddate: datetime
    successful: bool
    data: Recipe
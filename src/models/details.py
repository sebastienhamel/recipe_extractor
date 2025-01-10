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
    name: str
    portions: int
    preperation_time: int
    cooking_time: int
    total_time: int
    category: str
    key_works: str
    ingredients: List[Ingredient]
    method: List[Method]

class Details(BaseModel):
    id: int
    link: str
    startdate: datetime
    enddate: datetime
    successful: bool
    data: Recipe
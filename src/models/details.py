from datetime import datetime
from typing import List
from pydantic import BaseModel

class Ingredient(BaseModel):
    quantity_unit: str
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
    categories: List[str]
    key_works: List[str]
    ingredients: List[Ingredient]
    method: List[Method]

class Details(BaseModel):
    id: int
    link: str
    startdate: datetime
    enddate: datetime
    successful: bool
    data: Recipe
    attempts: int
    #NOTE - might be better to add some recipe informations here like name, category, etc.
from datetime import datetime
from typing import List
from pydantic import BaseModel, Field

class Ingredient(BaseModel):
    quantity_unit: str = ""
    ingredient_name: str = ""

class Method(BaseModel):
    step_number: int = 0
    instruction: str = ""

class Recipe(BaseModel):
    name: str = ""
    portions: str = 0
    preparation_time: str = ""
    cooking_time: str = ""
    total_time: str = ""
    categories: List[str] = []
    keywords: List[str] = []
    ingredients: List[Ingredient] = []
    method: List[Method] = []

class Details(BaseModel):
    id: int
    link: str
    startdate: datetime
    enddate: datetime
    successful: bool
    data: Recipe
    attempts: int
    #NOTE - might be better to add some recipe informations here like name, category, etc.
from enum import Enum

class Mode(str, Enum):
    CATEGORIES_LISTING = "categories_listing"
    RECIPE_LINKS = "recipe_links"
    RECIPE_DETAILS = "recipe_details"


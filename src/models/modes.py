from enum import Enum

class Mode(str, Enum):
    CATEGORIES_LISTING = "categories_listing"
    CATEGORIES_LISTING_PAGE = "categories_listing_page"
    RECIPE_LINKS = "recipe_links"
    RECIPE_DETAILS = "recipe_details"


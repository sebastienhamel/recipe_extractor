import re

from typing import List
from datetime import datetime

from requests_html import HTML
from sqlalchemy.exc import IntegrityError

from utils.logger_service import get_logger
from utils.scraper_service import load_page
from utils.database.database_tables import Detail, Listing
from utils.database.database_connection import get_listing_to_process
from utils.database.database_connection import get_database

from models.details import Recipe, Ingredient, Method


class RecipeScraper():

    def __init__(self, page_content:HTML, logger):
        self.page_content = page_content
        self.logger = logger
        self.details = Detail()
        self.details.data = Recipe()

    def run(self):
        self.get_recipe_name()
        self.get_recipe_info_section()
        self.get_category()
        self.get_keywords()
        self.get_ingredients()
        self.get_method()

    def get_recipe_name(self):
        name_element = self.page_content.xpath("//h1")[0]
        recipe_name = name_element.text
        self.details.data.name = recipe_name


    def get_recipe_info_section(self):
        """ Gets all value from the recipe-infos section on the page """

        info_search_terms = {
            "Préparation": "preparation_time",
            "Cuisson": "cooking_time",
            "Total": "total_time",
            "Portion": "portions"
        }

        for search_term, field_name in info_search_terms.items():
            x_path = f"//section[contains(@class, 'recipe-infos')]//li//span[contains(text(), '{search_term}')]/following-sibling::span"
            field_value = self.page_content.xpath(x_path)[0].text
            setattr(self.details.data, field_name, field_value)

    
    def get_ingredients(self):
        ingredients:List[Ingredient] = []

        ingredient_elements = self.page_content.xpath("//h4[text()='Ingrédients']/following::ul//li[@class='itemListe']") 

        for ingredient_element in ingredient_elements:
            try:
                full_ingredient = ingredient_element.text
                ingredient_quantity = ingredient_element.xpath("//span[@class='qty']")[0].text
                ingredient_name = full_ingredient.removeprefix(ingredient_quantity)

            except Exception as e:
                self.logger.error(f"Error: {e}")
            
            ingredient = Ingredient(
                quantity_unit=ingredient_quantity,
                ingredient_name=ingredient_name.strip()
            )

            ingredients.append(ingredient)

        self.details.data.ingredients = ingredients


    def get_method(self):
        #TODO - finish method
        method:List[Method] = []

        method_elements = self.page_content.xpath("//section[contains(@class, 'method')]")[0]
        number_of_steps = len(re.findall(r"Étape ", method_elements.text))
        all_one_digit_steps_descriptions = re.findall(r'(?<=Étape \d\n).*', method_elements.text) # Can only do a look behind with a fixed range.

        for index, value in enumerate(all_one_digit_steps_descriptions):
            step = Method(
                step_number=index + 1, 
                instruction=value
            )

            method.append(step)

        # Number of steps > 9
        all_two_digit_steps_descriptions = re.findall(r'(?<=Étape \d{2}\n).*', method_elements.text) # Can only do a look behind with a fixed range(!\d{1,2})

        for index, value in enumerate(all_two_digit_steps_descriptions):
            step = Method(
                step_number = index + 9,
                instruction = value
            )

            method.append(step)

        # Final check to make sure we have all steps for method
        if number_of_steps == len(method):
            self.details.data.method = method
        else:
            raise ValueError(f"The code did not return all the method steps for {self.details.link}. Returned only the following steps {method}")


    def get_category(self):
        categories = []
        categories_element = self.page_content.xpath("//div[contains(@class, 'categories')]//li/a")

        for category in categories_element:
            categories.append(category.text)

        self.details.data.categories = categories 


    def get_keywords(self):
        keywords = []
        keywords_element = self.page_content.xpath("//div[contains(@class, 'categories')]//li/a")

        for keyword in keywords_element:
            keywords.append(keyword.text)

        self.details.data.keywords = keywords 


if __name__ == "__main__":
    logger = get_logger(name = RecipeScraper.__name__)
    listing_to_process = get_listing_to_process(limit=5)
    

    for listing in listing_to_process:
        listing.attempts += 1
        listing.startdate = datetime.now()
        page_content = load_page(listing.link)

        app = RecipeScraper(logger = logger, page_content= page_content)

        with(next(get_database())) as database:
            try:
                app.run()
                listing.enddate = datetime.now()
                listing.successful = True

                detail_item = Detail(
                    link = listing.link,
                    timestamp = datetime.now(),
                    data = app.details.data
                )

                try:
                    database.add(detail_item)
                    app.logger.info("Link processing successful")
                
                except IntegrityError as e:
                    app.logger.warning("Detail item is a duplicate. Rollback.")
                    database.rollback()
                
            except:
                listing.enddate = datetime.now()
                listing.successful = False

            #update listing
            database.query(Listing).where(Listing.id == listing.id).update({
                "attempts": listing.attempts, 
                "enddate": listing.enddate,
                "successful": listing.successful,
                "startdate": listing.startdate
            })
            database.commit()
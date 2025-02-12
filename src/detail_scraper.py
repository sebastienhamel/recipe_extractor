import re

from typing import List
from datetime import datetime

from requests_html import HTML
from sqlalchemy.exc import IntegrityError

from src.utils.logger_service import get_logger
from src.utils.scraper_service import load_page
from src.utils.database.database_tables import Detail
from src.utils.database.database_connection import get_details_to_process, update_listing, is_detail_complete
from src.utils.database.database_connection import get_database

from src.models.details import Recipe, Ingredient, Method


class RecipeScraper():

    def __init__(self, logger, page_content:HTML = None):
        self.page_content = page_content
        self.logger = logger
        self.details = Detail()
        self.details.data = Recipe()

    def run(self):
        listing_to_process = get_details_to_process(limit=5)

        if listing_to_process and not is_detail_complete():
            for listing in listing_to_process:
                
                # check if max attempts achieved
                # if listing.attempts <= 5: 
                self.logger.info(f"Processing details for {listing.link}")
                listing.attempts += 1
                listing.startdate = datetime.now()
                self.page_content = load_page(listing.link)

                with(next(get_database())) as database:
                    try:
                        self.get_details()
                        listing.enddate = datetime.now()
                        listing.successful = True

                        detail_item = Detail(
                            link = listing.link,
                            timestamp = datetime.now(),
                            data = self.details.data
                        )

                        try:
                            database.add(detail_item)
                            self.logger.info("Link processing successful")
                            database.commit()
                        
                        except IntegrityError as e:
                            self.logger.warning("Detail item is a duplicate. Rollback.")
                            database.rollback()
                        
                    except:
                        listing.enddate = datetime.now()
                        listing.successful = False

                    #update listing
                    update_listing(listing=listing)
                
                # else:
                #     self.logger.info("Max attempts already too high for this record. Skipping.")

        elif not listing_to_process and not is_detail_complete():
            self.logger.info("There are no details to process because the listing hasn't found details yet.")

        elif not listing_to_process and is_detail_complete():
            self.logger.info("Details is complete, there are no links to process.")
        
    def get_details(self):  
        self.logger.info("Working on details...")      
        self.get_recipe_name()
        self.get_recipe_info_section()
        self.get_category()
        self.get_keywords()
        self.get_ingredients()
        self.get_method()
        self.logger.info("Recipe details acquired!")

    def get_recipe_name(self):
        self.logger.info("Working on recipe name...")
        name_element = self.page_content.xpath("//h1")[0]
        recipe_name = name_element.text
        self.details.data.name = recipe_name


    def get_recipe_info_section(self):
        self.logger.info("Working on info section...")
        """ Gets all value from the recipe-infos section on the page """

        info_search_terms = {
            "Préparation": "preparation_time",
            "Cuisson": "cooking_time",
            "Total": "total_time",
            "Portion": "portions"
        }

        for search_term, field_name in info_search_terms.items():
            x_path = f"//section[contains(@class, 'recipe-infos')]//li//span[contains(text(), '{search_term}')]/following-sibling::span"
            
            try:
                field_value = self.page_content.xpath(x_path)[0].text
                setattr(self.details.data, field_name, field_value)
            except IndexError:
                self.logger.error(f"{field_name} unavailable for this link. Setting empty string as value.")
                setattr(self.details.data, field_name, "")

    
    def get_ingredients(self):
        self.logger.info("Working on ingredients...")
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
        self.logger.info("Working on recipe method...")
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
        if number_of_steps == len(method) and len(method) != 0:
            self.details.data.method = method
        elif len(method) == 0:
            self.logger.error(f"Could not get method for link {self.details.link}.")
            self.details.data.method = method # Will assess if this has impact on data quality in a later step.
        else:
            raise ValueError(f"The code did not return all the method steps for {self.details.link}. Returned only the following steps {method}")


    def get_category(self):
        self.logger.info("Working on category...")
        categories = []
        categories_element = self.page_content.xpath("//div[contains(@class, 'categories')]//li/a")

        for category in categories_element:
            categories.append(category.text)

        self.details.data.categories = categories 


    def get_keywords(self):
        self.logger.info("Working on keyworkds...")
        keywords = []
        keywords_element = self.page_content.xpath("//div[contains(@class, 'categories')]//li/a")

        for keyword in keywords_element:
            keywords.append(keyword.text)

        self.details.data.keywords = keywords 


if __name__ == "__main__":
    logger = get_logger(name = RecipeScraper.__name__)
    app = RecipeScraper(logger = logger)
    app.run()

from typing import List

from requests_html import HTML

from utils.logger_service import get_logger
from utils.scraper_service import load_page
from utils.database.database_tables import Detail

from models.details import Recipe, Ingredient, Method

class RecipeScraper():

    def __init__(self, page_content:HTML, logger):
        self.page_content = page_content
        self.logger = logger
        self.details = Detail

    def get_recipe_name(self):
        name_element = self.page_content.xpath("//h1")[0]
        recipe_name = name_element.text
        self.details.data.name = recipe_name

    def get_recipe_info_section(self):
        """ Gets all value from the recipe-infos section on the page """

        recipe_info_section = self.page.content.xpath("//section[contains(@class, 'recipe-infos')]//li")

        info_search_terms = {
            self.details.data.preparation_time: "Preparation", 
            self.details.data.cooking_time: "Cuisson", 
            self.details.data.total_time: "Total", 
            self.details.data.portions: "Portion"
        }

        for field, search_term in info_search_terms:
            x_path = f"//section[contains(@class, 'recipe-infos')]//li//span[contains(text(), '{search_term}')]/following-sibling::span"
            field = self.page_content.xpath(x_path)[0].text


    # def get_recipe_prep_time():
    #     pass
    
    def get_ingredients(self):
        ingredients:List[Ingredient] = []

        ingredient_elements = self.page_content.xpath("//h4[text()='Ingrédients']/following::ul//li[@class='itemListe']") 

        for ingredient_element in ingredient_elements:

        pass

    def get_ingredient_quantity():
        pass 

    def get_ingredient_name():
        pass

    def get_method(self):
        method:List[Method] = []

        method_elements = self.page_content.xpath("//section[contains(@class, 'method')]")
        pass

    # def get_portions():
    #     pass

    # def get_cooking_time():
    #     pass

    # def get_total_time():
    #     pass

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
    app = RecipeScraper(logger = logger)
    app.run()
import pandas
import matplotlib
import re

from enum import Enum
from typing import List

from src.utils.database.database_connection import get_database
from src.utils.database.database_tables import Detail as DetailTable
from src.models.details import Details

class Category(Enum):
    GATEAU = "gateau"
    GALETTE = "galette"
    BISCUIT = "biscuit"

class DataAnalyzer():
    EXCLUDED_KEYWORDS = ["Viande", "Volaille", "Pizza", "Sandwich", "Poisson et fruits de mer", "Verrines, bouchées et tapas", "Salade", "Légumes", "Sauce et condiments", "Pâté", "Oeufs", "Confitures, gelées et marmelades"]

    EXCLUDED_NAMES = ["tarte", "truffes", "tcones", "biscotti", "biscoti", "sablés", "boules", ]

    def __init__(self):
        self.all_details = []

    
    def run(self):
        self.get_data_from_database()
        self.exclude_data()
        self.categorize_recipe()

        converted_details = []

        for detail in self.all_details:
            if detail.category:
                detail_dict = {
                    "id": detail.id, 
                    "link": detail.link,
                    "timestamp": detail.timestamp,
                    "data": detail.data.model_dump()
                }

                converted_details.append(detail_dict)

        df = pandas.DataFrame(converted_details)
        #Nope, not how it should be done
        exploded_data_df = pandas.json_normalize(df['data'])
        exploded_ingredients_df = pandas.json_normalize(exploded_data_df['ingredients'])
        exploded_method_df = pandas.json_normalize(exploded_data_df['method'])


    def categorize_recipe(self):
        regex_gateau = r"g*teau"

        for detail in self.all_details:
            detail.is_right_category = False
            if re.search(regex_gateau, detail.data.name):
                detail.is_right_category = True
                detail.category = Category.GATEAU

            elif "galette" in detail.data.name:
                detail.is_right_category = True
                detail.category = Category.GALETTE

            elif "biscuit" in detail.data.name:
                detail.is_right_category = True
                detail.category = Category.BISCUIT

        self.all_details = [detail for detail in self.all_details if detail.is_right_category]



    def get_data_from_database(self):

        all_details:List[Details] = []

        with(next(get_database())) as database:
            rows = database.query(DetailTable).all()

            for row in rows:
                all_details.append(row)

        self.all_details = all_details
    

    def exclude_data(self):

        for detail in self.all_details:
            detail.should_be_excluded = False

            for keyword in detail.data.keywords:
                if keyword in self.EXCLUDED_KEYWORDS:
                    detail.should_be_excluded = True


            for category in detail.data.categories:
                if category in self.EXCLUDED_KEYWORDS:
                    detail.should_be_excluded = True


            for word in detail.data.name.lower():
                if word in self.EXCLUDED_NAMES:
                    detail.should_be_excluded = True

        self.all_details = [detail for detail in self.all_details if not detail.should_be_excluded]



if __name__ == "__main__": 
    app = DataAnalyzer()
    app.run()


#TODO - Get data from database
#TODO - Categorize data (gateau, cookies, galettes)
#TODO - exclude non dessert data
#TODO - Check number of steps for recipes
#TODO - Check cooking time
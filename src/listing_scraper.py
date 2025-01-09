import argparse
import math
import requests
import re

from requests_html import HTML

from models.listing import Listing
from models.modes import Mode

class RecipeLister():
    START_URL = "https://www.recettes.qc.ca/recettes/recherche?"
    RESULTS_PER_PAGE = 10

    def run(self, mode:Mode):
        #TODO - document

        if mode == Mode.CATEGORIES_LISTING:
            query_links = self.generate_query_links()
            all_recipe_links = []

        #TODO - do not have loop, just a different scraping mode.
        for link in query_links:
            page_content:HTML = self.load_page(link=link)
            number_of_pages = self.get_total_page_quantity(page_content=page_content)
            listing_links_per_category = self.generate_listing_links(query_link=link, number_of_pages=number_of_pages)
            all_recipe_links.append(listing_links_per_category)

        #TODO - add different mode
        for link in all_recipe_links[0]:
            self.get_detail_links(link)

        pass

    def get_total_page_quantity(self, page_content:HTML):
        #TODO - document
        total_span = page_content.xpath("//span[@class='total']")[0]
        total_span_text = total_span.text 
        total_results = re.match(r'\d+', total_span_text)[0]

        number_of_pages = math.ceil(int(total_results) / RecipeLister.RESULTS_PER_PAGE)

        return number_of_pages
    
    def get_detail_links(self, link:str):
        page_content = self.load_page(link=link)
        search_result = page_content.xpath("//section[@id='search-results']//h4/a")
        all_detail_links = []

        for web_element in search_result:
            href = web_element.attrs.get("href")
            full_link = "https://www.recettes.qc.ca" + href
            all_detail_links.append(full_link)

        
        return all_detail_links




    def generate_listing_links(self, query_link:str, number_of_pages:int):
        #TODO - document
        page_number_filter = "&search[page]="
        listing_links = []
        
        for page_number in range(1,number_of_pages + 1):
            listing_links.append(query_link + page_number_filter + str(page_number))

        return listing_links
    
    def generate_query_links(self):
        #TODO - document
        query_term_filter = "search[query]="
        query_terms = ["galette", "biscuit", "gateau"]
        query = []

        for term in query_terms:
            query.append(RecipeLister.START_URL + query_term_filter + term)
        
        return query
        

    def load_page(self, link:str):
        #TODO - document
        #TODO - error management
        response = requests.get(link)
        page_content = HTML(html=response.text)

        return page_content


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="The mode you would like to run the RecipeLister with.")
    mode_choices = ["categories_listing", "recipe_links"]
    parser.add_argument(
        "--mode",
        type=Mode, 
        choices=list(Mode), 
        help=f"Modes {", ".join(list(Mode))} can be used."
    )

    args = parser.parse_args()



    app = RecipeLister()
    app.run(mode=args.mode)

    #TODO - listing modes
    # - generic listing mode
    #TODO - details mode
    # - recipes
    #TODO - all modes
    # - document
    # - error management
    # - write to database
    # - add modes
    #   - listing
    #   - detail links
    #   - details
    #TODO - database work
    # - listing
    #   - link
    #   - startdate
    #   - enddate
    #   - successful
    #   - primary key
    #   - unique key
    #   - id
    # - details
    # - migrations
    #   - using Alembic, sql-alchemy and pydantic
    #   - make OOP models
    #TODO - run scripts
    # - find of other solutions than NiFi would be easier
    #TODO - add queue
    # - using from queue import Queue
    
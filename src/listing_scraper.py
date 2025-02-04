import math
import re

from datetime import datetime
from requests_html import HTML
from sqlalchemy.exc import IntegrityError
from typing import List

from src.models.modes import Mode

from src.utils.logger_service import get_logger
from src.utils.database.database_connection import engine, get_database, get_listing_to_process, update_listing, is_listing_complete
from src.utils.database.database_tables import Base, Listing
from src.utils.scraper_service import load_page

Base.metadata.create_all(bind = engine)

class RecipeLister():
    START_URL = "https://www.recettes.qc.ca/recettes/recherche?"
    MAX_RETRIES = 5
    RESULTS_PER_PAGE = 10

    def __init__(self, logger):
        self.logger = logger

    def run(self):
        """ Processes the listing for the recipe scraper. """

        self.logger.info("Starting listing modes.")

        listings_to_process = get_listing_to_process(limit=5)
        
        if listings_to_process and not is_listing_complete():
            self.logger.info("There are listing elements to process.")
            
            #check for max retries
            for listing in listings_to_process:
                self.logger.info(f"Processing link {listing.link} for {listing.mode}")
                listing.startdate = datetime.now()
                listing.attempts += 1
                new_listing_items: List[Listing] = []

                try:

                    if listing.mode == Mode.CATEGORIES_LISTING:
                        new_listing_items = self.process_categories_listing(listing_to_process=listing)

                    if listing.mode == Mode.CATEGORIES_LISTING_PAGE:
                        new_listing_items = self.process_categories_listing_page(listing_to_process=listing)

                    listing.enddate = datetime.now()
                    listing.successful = True
                    
                except Exception:
                    self.logger.info(f"Error while processing link {listing.link} for {listing.mode} ")
                    listing.enddate = datetime.now()
                    listing.successful = False
                    
                self.insert_new_listing_items(new_listing_items=new_listing_items)
                update_listing(listing=listing)


        # No listing item exists in database
        elif not listings_to_process and not is_listing_complete():
            self.logger.info("Listing has not ran before, proceeding to seeding.")
            categories_listing_items = self.seed_listing_with_categories()
            self.insert_new_listing_items(new_listing_items=categories_listing_items)

        else:
            self.logger.info("Listing is complete. Nothing to process.")


    def insert_new_listing_items(self, new_listing_items:List[Listing]):
        """ Inserts a list of new listing item in database """
        
        with next(get_database()) as database:
            for listing_item in new_listing_items:
                self.logger.info(f"Processing {listing_item.link}")
                try:
                    database.add(listing_item)
                    database.commit()
                    self.logger.info("Link processing successful")

                        
                except IntegrityError as e:
                    self.logger.warning("Listing item is a duplicate. Rollback.")
                    database.rollback()


    def seed_listing_with_categories(self):
        """ Creates the seeds for the listing from the original categories to scrape """
        
        query_links = self.generate_query_links()
        listing_items: List[Listing] = []

        for link in query_links:
            listing_item = Listing(
                link = link,
                mode = Mode.CATEGORIES_LISTING,
                successful = False,
                attempts = 0,
            )

            listing_items.append(listing_item)
        
        return listing_items
    
    
    def process_categories_listing(self, listing_to_process:Listing) -> List[Listing]:
        """ Process the categories listing and generates the categories listing pages listing items. """
        
        page_content:HTML = load_page(link=listing_to_process.link)
        number_of_pages = self.get_total_page_quantity(page_content=page_content)
        listing_links_per_category = self.generate_listing_links(query_link=listing_to_process.link, number_of_pages=number_of_pages)
        categories_listing_page_items: List[Listing] = []
        
        for link in listing_links_per_category:
            listing_item = Listing(
                link = link,
                mode = Mode.CATEGORIES_LISTING_PAGE, 
                attempts = 0
            )
            
            self.logger.info(f"Adding link {listing_item.link} to queue.")
            categories_listing_page_items.append(listing_item)
        
        self.logger.info(f"Link processing successful for {listing_to_process.link}")
        return categories_listing_page_items
    

    def process_categories_listing_page(self, listing_to_process:Listing) -> List[Listing]:
        """ Process the categories listing pages items and generates recipe detail links. """
        
        all_detail_links = self.get_detail_links(link = listing_to_process.link)
        detail_links_items: List[Listing] = []

        for link in all_detail_links:
            listing_item = Listing(
                link = link,
                mode = Mode.RECIPE_LINKS,
                attempts = 0
            )

            detail_links_items.append(listing_item)

        return detail_links_items

    def get_total_page_quantity(self, page_content:HTML) -> int:
        """ Calculates the maximum number of pages based on the number of search results. """
        
        self.logger.info("Calculating maximum page number.")
        total_span = page_content.xpath("//span[@class='total']")[0]
        total_span_text = total_span.text 
        total_results = re.match(r'\d+', total_span_text)[0]

        number_of_pages = math.ceil(int(total_results) / RecipeLister.RESULTS_PER_PAGE)

        return number_of_pages
    
    def get_detail_links(self, link:str) -> List[str]:
        """ Finds detail links from search results. """

        self.logger.info("Retreiving detail links.")
        page_content = load_page(link = link)
        search_result = page_content.xpath("//section[@id='search-results']//h4/a")
        all_detail_links = []

        for web_element in search_result:
            href = web_element.attrs.get("href")
            full_link = "https://www.recettes.qc.ca" + href
            all_detail_links.append(full_link)

        
        return all_detail_links

    def generate_listing_links(self, query_link:str, number_of_pages:int) -> List[str]:
        """ Generates the listing links by page number """

        self.logger.info(f"Generating listing links by page number.")
        page_number_filter = "&search[page]="
        listing_links = []
        
        for page_number in range(1,number_of_pages + 1):
            listing_links.append(query_link + page_number_filter + str(page_number))

        return listing_links
    
    def generate_query_links(self) -> List[str]:
        """ Generates the first query links for the scraper. """

        self.logger.info("Generating query links.")
        query_term_filter = "search[query]="
        #query_terms = ["galette"]
        query_terms = ["galette", "biscuit", "gateau"]
        query = []

        for term in query_terms:
            query.append(RecipeLister.START_URL + query_term_filter + term)
        
        return query


if __name__ == "__main__":
    logger = get_logger(name = RecipeLister.__name__)
    app = RecipeLister(logger = logger)
    app.run()

    #TODO - get stacktrace in logger

    
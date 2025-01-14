import math
import requests
import re
import time

from datetime import datetime
from queue import Queue
from requests_html import HTML
from typing import List

from models.listing import Listing
from models.modes import Mode

from utils.logger_service import get_logger

class RecipeLister():
    START_URL = "https://www.recettes.qc.ca/recettes/recherche?"
    MAX_RETRIES = 5
    RESULTS_PER_PAGE = 10

    def __init__(self, logger):
        self.logger = logger

    def run(self):
        """ Processes the listing for the recipe scraper. """

        self.logger.info("Starting listing modes.")
        queue = Queue()

        if queue.empty():
            self.logger.info("Queue is empty.")
            query_links = self.generate_query_links()

            for link in query_links:
                listing_item = Listing(
                    link = link,
                    mode = Mode.CATEGORIES_LISTING,
                    successful = True,
                    attemps = 0
                )

                queue.put(listing_item)

        while not queue.empty():
            queued_item:Listing = queue.get()
            self.logger.info(f"Processing link {queued_item.link} for {queued_item.mode}")

            if queued_item.attemps <= RecipeLister.MAX_RETRIES:
                if queued_item.mode == Mode.CATEGORIES_LISTING:
                    queued_item.startdate = datetime.now()
                    queued_item.attemps += 1
                    
                    try:
                        page_content:HTML = self.load_page(link=queued_item.link)
                        number_of_pages = self.get_total_page_quantity(page_content=page_content)
                        listing_links_per_category = self.generate_listing_links(query_link=link, number_of_pages=number_of_pages)
                        for link in listing_links_per_category:
                            listing_item = Listing(
                                link = link,
                                mode = Mode.CATEGORIES_LISTING_PAGE
                            )
                            
                            self.logger.info(f"Adding link {listing_item.link} to queue.")
                            queue.put(listing_item)
                        
                        self.logger.info("Link processing successful")

                    except Exception:
                        self.logger.info(f"Error while processing link {queued_item.link} for {queued_item.mode} ")
                        queued_item.enddate = datetime.now()
                        queued_item.sucessful = False
                        queue.put(queued_item)

                elif queued_item.mode == Mode.CATEGORIES_LISTING_PAGE:
                    queued_item.startdate = datetime.now()
                    queued_item.attemps += 1
                    
                    #TODO - check if processing of listing link only. Seems like it's not. 
                    #NOTE - needs to stop if Mode == Mode.RECIPE_LINKS
                    try:
                        all_detail_links = self.get_detail_links(link=queued_item.link)
                        
                        for link in all_detail_links:
                            listing_item = Listing(
                                link = link,
                                mode = Mode.RECIPE_LINKS
                            )

                            self.logger.info(f"Adding link {listing_item.link} to queue.")
                            queue.put(listing_item)

                        self.logger.info("Link processing successful")
                    
                    except Exception:
                        self.logger.info(f"Error while processing link {queued_item.link} for {queued_item.mode} ")
                        queued_item.enddate = datetime.now()
                        queued_item.sucessful = False
                        queue.put(queued_item)

                else:
                    self.logger.info(f"Unmanaged mode for link {queued_item.link}: {queued_item.mode}")

            else:
                self.logger.info(f"Item has {queued_item.attemps} retries. Skipping.")

            pass

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
        page_content = self.load_page(link=link)
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

        logger.info("Generating query links.")
        query_term_filter = "search[query]="
        query_terms = ["galette"]
        #query_terms = ["galette", "biscuit", "gateau"]
        query = []

        for term in query_terms:
            query.append(RecipeLister.START_URL + query_term_filter + term)
        
        return query
        

    def load_page(self, link:str) -> HTML:
        """ Load a page using requests, transtyping the page into an HTML object. 
        
            params
            link(str): the link to load the page with.

            return
            page_content(html): the page content loaded
        """

        #TODO - error management
        time.sleep(60)
        response = requests.get(link)
        page_content = HTML(html=response.text)

        return page_content


if __name__ == "__main__":
    logger = get_logger(name = RecipeLister.__name__)
    app = RecipeLister(logger = logger)
    app.run()

    #TODO - listing modes
    # - generic listing mode
    #TODO - details mode
    # - recipes
    # - logging
    #TODO - all modes
    # - document
    # - error management
    # - write to database
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
    #   - we might be getting more links from details
    # - migrations
    #   - using Alembic, sql-alchemy and pydantic
    #   - make OOP models
    #TODO - run scripts
    # - find of other solutions than NiFi would be easier
    #TODO - logging
    # - add logging

    
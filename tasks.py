from celery import Celery
from time import sleep

from src.listing_scraper import RecipeLister
from src.detail_scraper import RecipeScraper
from src.utils.logger_service import get_logger

app = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')
app.conf.beat_schedule = {}
# app.conf.beat_schedule_filename = '/app/celerybeat-schedule'

listing_logger = get_logger(name = RecipeLister.__name__)
detail_logger = get_logger(name = RecipeLister.__name__)

@app.task
def run_scraper():
    listing_scraper = RecipeLister(logger = listing_logger)
    listing_scraper.run()

    detail_scraper = RecipeScraper(logger = detail_logger)
    detail_scraper.run()

app.conf.beat_schedule = {
    'run-every-5-minutes': {
        'task': 'tasks.run_scraper',
        'schedule': 300.0,  # every 5 minutes
    },
}

app.conf.timezone = 'UTC'

if __name__=="__main__":
    run_scraper.apply_async()
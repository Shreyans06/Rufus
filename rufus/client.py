from .scraper import WebScraper
from .document_synthesizer import DocumentSynthesizer
from .config import MAX_PAGES , TIMEOUT

class RufusClient:
    def __init__(self, api_key):
        if api_key is None:
            raise 'API Key not found'
        
        # Initialize the API Key
        self.api_key = api_key

        # Initialize the WebScraper
        self.scraper = WebScraper()

        # Initialize the Document Synthesizer
        self.synthesizer = DocumentSynthesizer()

    def scrape(self, url, prompt):
        # Call the scraper method to get the scraped data
        scraped_data = self.scraper.scrape_site(url , prompt , max_pages = MAX_PAGES , time_out = TIMEOUT)

        # Call the document synthesizer to get the structured data
        structured_data = self.synthesizer.synthesize(scraped_data, prompt)

        # Close the driver 
        self.scraper.close_driver()

        return structured_data

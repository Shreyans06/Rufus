from selenium import webdriver
from bs4 import BeautifulSoup
import heapq
from urllib.parse import urlparse, parse_qs
import re
from sentence_transformers import SentenceTransformer, util
from selenium.common.exceptions import TimeoutException


class WebScraper:
    def __init__(self) -> None:
        # Using selenium driver to set options for the browser
        chrome_options = webdriver.ChromeOptions()
        # Run Chrome in headless mode
        chrome_options.add_argument("--headless")  
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--remote-debugging-port=9222")
        self.driver = webdriver.Chrome(options=chrome_options)
        # Initialize the heap to store the pages similar to the prompt
        self.heap = []

    def bert_sentence_similarity(self , sent1, sent2):
        """
        Check the cosine similarity between two sentences
        """
        model = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight BERT variant
        embeddings = model.encode([sent1, sent2])
        cosine_sim = util.cos_sim(embeddings[0], embeddings[1])
        return cosine_sim.item()

    def parse_url_words(self, url):
        """
        Parse the URL to get words
        """
        # Parse the URL into components
        parsed_url = urlparse(url)
        
        # Tokenize each component into words
        def tokenize(text):
            # Using regex to find words (alphanumeric sequences) and return as a list
            return re.findall(r'\w+', text)

        # Parse the scheme, netloc (domain), and path
        scheme_words = tokenize(parsed_url.scheme)
        netloc_words = tokenize(parsed_url.netloc)
        path_words = tokenize(parsed_url.path)
        
        # Parse query parameters and fragment, if any
        query_words = []
        if parsed_url.query:
            query_params = parse_qs(parsed_url.query)
            for key, values in query_params.items():
                query_words.extend(tokenize(key))
                for value in values:
                    query_words.extend(tokenize(value))
        
        fragment_words = tokenize(parsed_url.fragment)
        
        # Combine all words into a single list
        all_words = scheme_words + netloc_words + path_words + query_words + fragment_words
        
        return all_words

    def scrape_site(self, url, prompt, max_pages = 5 , time_out = 10):
        """
        Used to scrape the website to get the relevant information 
        """
        scraped_data = []
        links_to_visit = [url]
        visited_links = set()

        # Visit relevant links to the prompt
        while links_to_visit:
            current_url = links_to_visit.pop(0)
            if current_url in visited_links:
                continue
            
            visited_links.add(current_url)
            try:
                self.driver.get(current_url)
                self.driver.implicitly_wait(time_out)  # Allow the page to load
            except TimeoutException:
                print(f"Error: Timeout while loading {current_url}")

            # Get the HTML content
            html_content = self.driver.page_source

            # Store the content from each page
            content = []

            # Parse the page content using BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']):
                if element.name.startswith('h'):
                    # Append heading elements as a dictionary with their type and text
                    content.append({
                        'type': element.name,  # h1, h2, h3, etc.
                        'text': element.get_text(strip=True)  # Clean the text
                    })
                elif element.name == 'p':
                    # Append paragraph elements similarly
                    content.append({
                        'type': 'p',
                        'text': element.get_text(strip=True)
                    })
            scraped_data.append({"url": current_url.strip() , "page_text": content})

            # Find all internal links for further crawling
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.startswith('http') and href not in visited_links:
                    url_words = self.parse_url_words(href)
                    url_string = " ".join(url_words[4:])
                    similarity = self.bert_sentence_similarity(url_string , prompt)
                    if similarity >= 0.5:
                        heapq.heappush(self.heap , (similarity , href))

            # Storing only the top_k links to extract more information
            top_k_links = heapq.nlargest(3 , self.heap)
            for links in top_k_links:
                links_to_visit.append(links[1])
            
            self.heap = []
        return scraped_data
    
    def close_driver(self):
        """
        Close the selenium driver 
        """
        self.driver.quit()

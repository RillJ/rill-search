import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

class Crawler:
    def __init__(self, start_url):
        self.start_url = start_url # Start crawling from this URL
        self.visited_urls = set() # Easier than a list (prevents duplicates)
        self.index = {} # Dictionary for the in-memory index

    def start_crawling(self):
        """
        Start crawling from the initial URL input when creating the class.
        """
        print_prefix = f"{self.start_crawling.__name__} >"
        print(f"{print_prefix} Starting to crawl now!")
        self.crawl_page(self.start_url)
    
    def crawl_page(self, url):
        """
        Crawl a single page, index the page content and parse the links on the page.
        Var 'url': The URL that will be crawled.
        Appends: The 'visited_urls' set.
        """
        print_prefix = f"{self.crawl_page.__name__} >"
        if url in self.visited_urls: # Skip already visited URLs
            print(f"{print_prefix} The URL {url} has already been visited. Ignoring.")
        else:
            print(f"{print_prefix} Currently crawling the URL: {url}")
            response = requests.get(url) # Fetch URL
            if response.headers["Content-Type"].startswith("text/html"): # Only process HTML responses
                self.visited_urls.add(url) # Add the visited URL to the set
                print(f"{print_prefix} Successfully added {url} to the set.")
                self.index_page(url, response.text) # Index the page content
                self.parse_links(url, response.text) # Parse the links on the page
            else:
                print(f"{print_prefix} The URL {url} is not a HTML document. Ignoring.")

    def parse_links(self, base_url, html):
        """
        Parse links in the URL's HTML content and crawl these links.
        This makes the link crawling recursive until it has crawled all pages.
        Var 'base_url': The URL that was crawled.
        Var 'html': Scraped plaintext HTML content of the crawled URL in question.
        """
        print_prefix = f"{self.parse_links.__name__} >"
        soupie = BeautifulSoup(html, "html.parser")
        for a in soupie.find_all("a", href=True):
            print(f"{print_prefix} Parsing the URL: {a['href']}")
            full_url = urljoin(base_url, a['href'])
            if self.is_same_server(full_url):
                self.crawl_page(full_url)

    def is_same_server(self, url):
        """
        Verify if the input URL belongs to the same server/network location as the start URL.
        Var 'url': The URL that needs to be compared to the start URL.
        Returns: True if it is on the same server and False if not.
        """
        print_prefix = f"{self.is_same_server.__name__} >"
        start_netloc = urlparse(self.start_url).netloc
        url_netloc = urlparse(url).netloc
        if start_netloc == url_netloc:
            print(f"{print_prefix} The URL {url} is on the same server as {start_netloc}.")
            return True
        else:
            print(f"{print_prefix} The URL {url} is not on the same server as {start_netloc}. Ignoring.")
            return False

    def index_page(self, url, html):
        """
        Build an in-memory index from the HTML text content found on the given page.
        Var 'url': The URL of the HTML page that contains text content.
        Var 'html': Scraped plaintext HTML content of the crawled URL in question.
        Appends: The found words on the HTML page to the 'index' dictionary.
        """
        print_prefix = f"{self.index_page.__name__} >"
        soupie = BeautifulSoup(html, 'html.parser')
        text = soupie.get_text() # Extract the visible text from the HTML
        words = text.split() # Split text into list of words
        for word in words:
            word = re.sub('\W+','', word.lower().strip()) # Normalize and remove special characters
            if word not in self.index:
                self.index[word] = []
            if url not in self.index[word]:
                self.index[word].append(url)
        print(f"{print_prefix} Indexed content from the URL: {url}")

    def search(self, words, all_words = True):
            """
            Search the index for pages containing all the given words.
            Var 'words': A list of words to search for.
            Var 'all_words': If True, will only search for URLs that contain all words from the list.
            Returns: A list of URLs containing all the words.
            """
            print_prefix = f"{self.search.__name__} >"
            print(f"{print_prefix} Searching for words: {words}")
            normalized_words = [word.lower() for word in words] # Normalize words to lowercase
            found_urls = []
            # For all words in the list, check if they appear in the index
            for word in normalized_words:
                if word in self.index:
                    for url in self.index[word]:
                        if url not in found_urls: # Avoid duplicate URLs
                            found_urls.append(url)
            # Filter for URLs that contain all words instead of only some
            if all_words:
                filtered_urls = []
                for url in found_urls:
                    contains_all_words = True
                    for word in normalized_words:
                        if word not in self.index or url not in self.index[word]:
                            contains_all_words = False
                            break
                    if contains_all_words:
                        filtered_urls.append(url)
                found_urls = filtered_urls
            print(f"{print_prefix} For the search {words}, found URLs: {found_urls}")
            return found_urls

if __name__ == "__main__":
    crawler = Crawler("https://vm009.rz.uos.de/crawl/index.html")
    crawler.start_crawling()
    search_results = crawler.search(["Australia", "Biology"])
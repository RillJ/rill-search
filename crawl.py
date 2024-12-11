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
        This is recursive until all pages within the starting URL have been crawled.
        """
        print_prefix = f"{self.start_crawling.__name__} >"
        print(f"{print_prefix} Starting to crawl now!")
        self.crawl_page(self.start_url)
    
    def crawl_page(self, url):
        """
        Crawl a single page and parse the links on the page.
        """
        print_prefix = f"{self.crawl_page.__name__} >"
        if url in self.visited_urls: # Skip already visited URLs
            print(f"{print_prefix} The URL {url} has already been visited. Ignoring.")
        else:
            print(f"{print_prefix} Currently crawling the URL: {url}")
            response = requests.get(url) # Fetch URL
            if response.headers["Content-Type"].startswith("text/html"): # Only process HTML responses
                self.visited_urls.add(url)
                self.index_page(url, response.text) # Index the page content
                self.parse_links(url, response.text)
            else:
                print(f"{print_prefix} The URL {url} is not a HTML document. Ignoring.")

    def parse_links(self, base_url, html):
        """
        Parse links in the URL's HTML content and crawl these links.
        This makes the link crawling recursive until it has crawled all pages.
        """
        print_prefix = f"{self.parse_links.__name__} >"
        soupie = BeautifulSoup(html, "html.parser")
        for a in soupie.find_all("a", href=True):
            print(f"{print_prefix} Parsing the URL: {a['href']}")
            full_url = urljoin(base_url, a['href'])
            if self.is_same_server(full_url):
                self.crawl_page(full_url)
                print(f"{print_prefix} Successfully added {full_url} to the set.")

    def is_same_server(self, url):
        """
        Verify if the input URL belongs to the same server/network location as the start URL.
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
        """
        print_prefix = f"{self.index_page.__name__} >"
        soupie = BeautifulSoup(html, 'html.parser')
        text = soupie.get_text() # Extract the visible text from the HTML
        words = text.split() # Split text into list of words
        for word in words:
            word = word.lower().strip() # Normalize words to lowercase and remove whitespace
            if word not in self.index:
                self.index[word] = []
            if url not in self.index[word]:
                self.index[word].append(url)
        print(f"{print_prefix} Indexed content from the URL {url}.")

if __name__ == "__main__":
    crawler = Crawler("https://vm009.rz.uos.de/crawl/index.html")
    crawler.start_crawling()
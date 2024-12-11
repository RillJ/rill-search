import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser

class Crawler:
    def __init__(self, start_url):
        self.start_url = start_url # Start crawling from this URL
        self.visited_urls = set() # Easier than a list (prevents duplicates)
        if not os.path.exists("indexdir"):
            os.mkdir("indexdir") # Create Whoosh indexdir folder if it doesn't exist
        schema = Schema(url=ID(stored=True, unique=True), content=TEXT) # Setting up Whoosh index
        self.index = create_in("indexdir", schema)
        self.writer = self.index.writer()

    def start_crawling(self):
        """
        Start crawling from the initial URL input when creating the class.
        """
        print_prefix = f"{self.start_crawling.__name__} >"
        print(f"{print_prefix} Starting to crawl now!")
        self.crawl_page(self.start_url)
        self.writer.commit() # Once all pages have been crawled, commit to Whoosh
        print(f"{print_prefix} Finished crawling!")

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
            full_url = urljoin(base_url, a['href'])
            print(f"{print_prefix} Parsing the URL: {full_url}")
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
        Use the Whoosh library to index the HTML text content found on the given page.
        Var 'url': The URL of the HTML page that contains text content.
        Var 'html': Scraped plaintext HTML content of the crawled URL in question.
        """
        print_prefix = f"{self.index_page.__name__} >"
        soupie = BeautifulSoup(html, "html.parser")
        text = soupie.get_text() # Extract the visible text from the HTML
        self.writer.add_document(url=url, content=text) # Add the crawled URL to the Whoosh index
        print(f"{print_prefix} Indexed content from the URL: {url}")

    def search(self, query):
        """
        Search the Whoosh index for pages containing the query string.
        Var 'query_str': The search query as a string.
        Returns: A list of URLs containing the query string.
        """
        print_prefix = f"{self.search.__name__} >"
        print(f"{print_prefix} Searching for: {query}")
        whoosh_query = QueryParser("content", self.index.schema).parse(query) # Parse query to a Whoosh query
        results = self.index.searcher().search(whoosh_query) # Search on this query
        found_urls = []
        for result in results:
            found_urls.append(result["url"]) # Append only the URLs to the list
        print(f"{print_prefix} For the search '{query}', found URLs: {found_urls}")
        return found_urls

# if __name__ == "__main__":
#     crawler = Crawler("https://vm009.rz.uos.de/crawl/index.html")
#     crawler.start_crawling()
#     search_results = crawler.search("Australia and Biology")
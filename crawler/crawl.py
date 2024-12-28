# Copyright 2024 Julian Calvin Rill

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import bleach
import requests
import argparse
from openai import OpenAI
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from urllib.parse import urljoin, urlparse
from whoosh.index import create_in, exists_in
from whoosh.fields import Schema, TEXT, ID
# from whoosh.qparser import QueryParser

load_dotenv() # Load OpenAI API key

class Crawler:
    def __init__(self, start_url, index_dir):
        self.start_url = start_url # Start crawling from this URL
        self.visited_urls = set() # Easier than a list (prevents duplicates)
        if not os.path.exists(index_dir):
            os.mkdir(index_dir) # Create Whoosh index folder if it doesn't exist
        # Setting up Whoosh index
        schema = Schema(
            url=ID(stored=True, unique=True),
            title=TEXT(stored=True, field_boost=2.0),
            teaser=TEXT(stored=True),
            content=TEXT
        )
        self.index = create_in(index_dir, schema)
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

    def extract_title(self, soupie, url):
        """
        Attempts to extract the HTML title of a webpage.
        Var 'soupie': The BeautifulSoup instance of the HTML webpage the title will be extracted from.
        Var 'url': The URL of the same HTML webpage.
        Returns: The title of the HTML, or if not found, the URL as a fallback.
        """
        print_prefix = f"{self.extract_title.__name__} >"
        if soupie.title:
            title = soupie.title.string.strip()
            print(f"{print_prefix} Found the title '{title}' in the URL: {url}")
            return title
        else:
            print(f"{print_prefix} Didn't find a page title in the URL {url}. Defaulting to URL.")
            return url

    def extract_body_content(self, soupie):
        """
        Attempts to extract the HTML body content of a webpage.
        Var 'soupie': The BeautifulSoup instance of the HTML webpage the body will be extracted from.
        Returns: The body content form the HTML, or if not found, an error message as a fallback.
        """
        print_prefix = f"{self.extract_body_content.__name__} >"
        body = soupie.find("body")
        if body:
            print(f"{print_prefix} Found body content.")
            return body.get_text(strip=True)
        else:
            print(f"{print_prefix} Didn't find body content. Defaulting to error message.")
            return "No body found on this web page."

    def generate_teaser(self, content, title):
        """
        Generates a teaser summary using ChatGPT.
        Var 'content': Serves as the input text for summarization.
        Var 'title': The title of the web page to be summarized.
        Returns: The LLM-summarized teaser, or if this process failed, truncated content as a fallback.
        """
        print_prefix = f"{self.generate_teaser.__name__} >"
        sanitized_content = bleach.clean(content) # Prevent XSS attacks
        try:
            client = OpenAI(
                api_key=os.environ.get("OPENAI_API_KEY"),
            )
            system_prompt = """
            You are an assistant that creates concise teaser summaries from webpage content for a search engine.
            Highlight important text using HTML, not markdown, by surrounding it with <b> tags, like this: <b>important text</b>.
            """
            user_prompt = f"Summarize the content for the page called {title}: {sanitized_content[:4000]}" # Don't send the whole webpage to the website to prevent token limits
            response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model="gpt-4o-mini"
            )
            teaser = response.choices[0].message.content.strip()
            print(f"{print_prefix} Succesfully generated a teaser summary with ChatGPT: {teaser}")
            return teaser
        except Exception as e: # Fall back to truncating content if ChatGPT fails
            print(f"{print_prefix} Failed to generate teaser using OpenAI API: {e}")
            if len(sanitized_content) > 300:
                return sanitized_content[:300] + "..."
            else:
                return sanitized_content

    def index_page(self, url, html):
        """
        Use the Whoosh library to index the HTML title and content found on the given page.
        Var 'url': The URL of the HTML page that contains text content.
        Var 'html': Scraped plaintext HTML content of the crawled URL in question.
        """
        soupie = BeautifulSoup(html, "html.parser")
        # Extract indexing components
        title = self.extract_title(soupie, url)
        body_content = self.extract_body_content(soupie)
        teaser = self.generate_teaser(body_content, title)
        # Add the crawled URL to the Whoosh index
        self.writer.add_document(url=url, content=body_content, title=title, teaser=teaser)
        print(f"{self.index_page.__name__} > Indexed content from the URL {url} with the title '{title}'.")

    # def search(self, query):
    #     """
    #     Search the Whoosh index for pages containing the query string.
    #     Var 'query_str': The search query as a string.
    #     Returns: A list of URLs containing the query string.
    #     """
    #     print_prefix = f"{self.search.__name__} >"
    #     print(f"{print_prefix} Searching for: {query}")
    #     whoosh_query = QueryParser("content", self.index.schema).parse(query) # Parse query to a Whoosh query
    #     results = self.index.searcher().search(whoosh_query) # Search on this query
    #     found_urls = []
    #     for result in results:
    #         found_urls.append(result["url"]) # Append only the URLs to the list
    #     print(f"{print_prefix} For the search '{query}', found URLs: {found_urls}")
    #     return found_urls

# if __name__ == "__main__":
#     crawler = Crawler("https://vm009.rz.uos.de/crawl/index.html")
#     crawler.start_crawling()
#     search_results = crawler.search("Australia and Biology")

# Command-line interface
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rill Search CLI - Indexing and Scraping")
    parser.add_argument("--start-url", default="https://vm009.rz.uos.de/crawl/index.html", help="Starting URL for the crawler.")
    parser.add_argument("--index-dir", default="indexdir", help="Directory to store the Whoosh index into.")
    parser.add_argument("--force", action=argparse.BooleanOptionalAction, help="Forces crawling even if an index already exists.")
    args = parser.parse_args() # Get the user entered arguments into a variable
    # Start crawling unless an index already exists 
    if exists_in(args.index_dir) and not args.force:
        print(f"An index has already been built in '{args.index_dir}'.")
    else:
        crawler = Crawler(start_url=args.start_url, index_dir=args.index_dir)
        crawler.start_crawling()
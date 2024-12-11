from crawler.crawl import Crawler
from flask import Flask, request, render_template
from whoosh.index import open_dir
from whoosh.qparser import QueryParser

app = Flask(__name__)

def initialize_crawler():
    """
    Initialize the crawler by building the index.
    """
    start_url = "https://vm009.rz.uos.de/crawl/index.html"
    crawler = Crawler(start_url)
    crawler.start_crawling()
    print(f"{initialize_crawler.__name__} > The crawler has finished initialising.")

@app.before_request
def setup_index():
    """
    Initialises the crawler once on startup of the Flask app.
    """
    app.before_request_funcs[None].remove(setup_index) # Remove this handler after execution
    print(f"{setup_index.__name__} > Starting to setup the index.")
    initialize_crawler()

@app.route("/")
def home():
    """
    Home route, shows the home page.
    """
    print(f"{home.__name__} > Drawing the home page.")
    return render_template("home.html")

@app.route("/search")
def search():
    """
    Search route, searches the crawled index with Whoosh and shows the results.
    """
    query = request.args.get("q") # Get the input query from the form
    if query:
        index = open_dir("indexdir") # Open the crawled Whoosh index
        print_prefix = f"{search.__name__} >"
        print(f"{search.__name__} > Searching for: '{query}'")
        whoosh_query = QueryParser("content", index.schema).parse(query) # Parse query to a Whoosh query
        results = index.searcher().search(whoosh_query) # Search on this query
        found_urls = []
        for result in results:
            found_urls.append(result["url"]) # Append only the URLs to the list
        print(f"{print_prefix} For the search '{query}', found URLs: {found_urls}. Drawing the search results page.")
        return render_template("search.html", results=found_urls, query=query)
    print(f"{print_prefix} Input search query is empty. Drawing the search results page.")
    return render_template("search.html", results=[], query=query) # If the user somehow input nothing, return empty results

if __name__ == "__main__":
    app.run(debug=True)
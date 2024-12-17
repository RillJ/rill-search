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
            found_urls.append({ # Append only the URLs, title and teaser to the list
                "url": result["url"],
                "title": result["title"],
                "teaser": result["teaser"],
                })
        print(f"{print_prefix} For the search '{query}', found URLs: {found_urls}. Drawing the search results page.")
        return render_template("search.html", results=found_urls, query=query)
    print(f"{print_prefix} Input search query is empty. Drawing the search results page.")
    return render_template("search.html", results=[], query=query) # If the user somehow input nothing, return empty results

if __name__ == "__main__":
    app.run(debug=True)
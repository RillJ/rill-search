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

# from crawler.crawl import Crawler
from flask import Flask, request, render_template, redirect
from whoosh.index import open_dir
from whoosh.qparser import QueryParser

app = Flask(__name__)

# def initialize_crawler():
#     """
#     Initialize the crawler by building the index.
#     """
#     start_url = "https://vm009.rz.uos.de/crawl/index.html"
#     crawler = Crawler(start_url)
#     crawler.start_crawling()
#     print(f"{initialize_crawler.__name__} > The crawler has finished initialising.")

# @app.before_request
# def setup_index():
#     """
#     Initialises the crawler once on startup of the Flask app.
#     """
#     app.before_request_funcs[None].remove(setup_index) # Remove this handler after execution
#     print(f"{setup_index.__name__} > Starting to setup the index.")
#     initialize_crawler()

#region Helper Functions
def get_spelling_suggestion(query, ix):
    """
    Helper function to handle spelling correction suggestions.
    Var 'query': The query used for searching.
    Var 'ix': The Whoosh indexer to use for determining spelling suggestions.
    Returns: The suggested word if a typo is detected, and if not, returns None.
    """
    print_prefix = f"{get_spelling_suggestion.__name__} >"
    with ix.searcher() as searcher: # Use the searcher context
        corrector = searcher.corrector("content") # Create the corrector for the 'content' field
        suggested_word = corrector.suggest(query, limit=1) # Get one suggestion
    if suggested_word and suggested_word[0] != query:
        print(f"{print_prefix} Found word suggestion '{suggested_word[0]}' for query: {query}'")
        return suggested_word[0] # Return the suggested word
    else:
        print(f"{print_prefix} No word suggestions found for query: {query}'")
        return None

def execute_search(query, ix):
    """
    Helper function to execute the search on the Whoosh index.
    Var 'query': The query used for searching.
    Var 'ix': The Whoosh indexer to use for searching.
    Returns: The Whoosh search results as a list.
    """
    whoosh_query = QueryParser("content", ix.schema).parse(query) # Parse query to a Whoosh query
    results = ix.searcher().search(whoosh_query) # Search on this query
    return results

def prepare_search_results(results):
    """
    Helper function to prepare the search result data.
    Var 'results': The Whoosh search results as a list. 
    Returns: A list of search result data to send to a render template.
    """
    found_urls = []
    for result in results:
        found_urls.append({ # Append only the URLs, title and teaser to the list
            "url": result["url"],
            "title": result["title"],
            "teaser": result["teaser"],
        })
    return found_urls
#endregion

#region App Routes
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
    frisky = request.args.get("frisky") # If the user pressed the "I'm Feeling Frisky..." button
    if query:
        print_prefix = f"{search.__name__} >"
        print(f"{print_prefix} Searching for: '{query}'")
        ix = open_dir("crawler/indexdir") # Open the crawled Whoosh index
        # Call helper functions for search logic
        corrected_query = get_spelling_suggestion(query, ix)
        results = execute_search(query, ix)
        found_urls = prepare_search_results(results)
        # Check if the "I'm Feeling Frisky..." button was clicked
        if frisky and results: 
            return redirect(results[0]["url"]) # Redirect to the first result's URL
        else: # Log results and render template
            print(f"{print_prefix} For the search '{query}', found URLs: {found_urls}. Drawing the search results page.")
            return render_template("search.html", results=found_urls, query=query, corrected_query=corrected_query)
    else: # If the user somehow input nothing, return empty results
        print(f"{print_prefix} Input search query is empty. Drawing empty search results page.")
        return render_template("search.html", results=[], query=query)
#endregion

if __name__ == "__main__":
    app.run(debug=True)
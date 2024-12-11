from crawler.crawl import Crawler
from flask import Flask, request, render_template

app = Flask(__name__)

def initialize_crawler():
    """
    Initialize the crawler by building the index.
    """
    start_url = "https://vm009.rz.uos.de/crawl/index.html"
    crawler = Crawler(start_url)
    crawler.start_crawling()

@app.before_request
def setup_index():
    """
    Initialises the crawler once on startup of the Flassk app.
    """
    app.before_request_funcs[None].remove(setup_index) # Remove this handler after execution
    initialize_crawler()

# Home route
@app.route("/")
def home():
    return render_template("home.html")

if __name__ == "__main__":
    app.run(debug=True)
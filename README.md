# Rill Search - A Simple AI Powered Search Engine

Rill Search is a simple search engine combining classical search engine elements and modern technologies like Large Language Models. It boasts both code for crawling pages and a web front end for searching the crawled web pages. Built using Flask, BeautifulSoup, Whoosh, and OpenAI's ChatGPT, Rill Search offers a fast and presentable search experience.

## Features

- **Web Crawling & Indexing**: Crawls a given website with BeautifulSoup starting from an entry point and indexes HTML content using the Whoosh library.
- **Spelling Suggestions**: Provides spelling suggestions for mis-typed queries using Whoosh’s spelling correction mechanism.
- **Search Results**: Displays the results of queries with clickable links, page teasers, and titles.
- **LLM Generated Teasers**: Generates concise teaser summaries for page content using OpenAI's chatgpt-4o-mini model.
- **I'm Feeling Frisky**: Click this button next to the search bar to get redirected to the first search result immediately.

## Background
I developed this search engine as part of a course in my Master's program in Cognitive Science. This course focuses on the application of AI technologies within web applications.

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/RillJ/rill-search.git
cd rill-search
```

### 2. Set up the Virtual Environment

Create a virtual environment and activate it:

```bash
python -m venv venv
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

Install all the required packages:

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables (optional)

Create a `.env` file in the root directory with your OpenAI API key:

```
OPENAI_API_KEY="your_openai_api_key"
```

Make sure to replace `your_openai_api_key` with your actual OpenAI API key.

If this step is skipped, the crawler will not use OpenAI to generate summaries and fall back to generating teasers by simply trimming contents of the web pages.

### 5. Crawl Web Pages

To begin crawling and indexing a website, use the CLI proveded in `crawl.py`. By default, it starts crawling from the URL `https://vm009.rz.uos.de/crawl/index.html`.

```bash
cd crawler
python crawl.py --start-url your_start_url --index-dir desired_index_dir [--force]
```
- The `--start-url` flag specifies the initial URL where the crawler will commence, continuing to index all links beginning from this URL.
- The `--index-dir` flag denotes the desired storage location of the Whoosh index.
- The `--force` flag will force crawling even if the `indexdir` folder already exists.

You may also use the pre-built index by unzipping `crawler/sample_indexdir.zip`. This index is built from the default demo values.

### 6. Run the Application

```bash
python app.py
```

This will start the Flask server. You can visit the app at `http://localhost:5000` in your browser.

## Project Structure

```
.
├── app.py                       # Flask web server
├── crawler/                     # Web crawler for indexing pages
│   ├── indexdir/                # Directory containing Whoosh index files
│   ├── __init__.py              # Crawler module initialization
│   ├── crawl.py                 # Crawler script
│   └── sample_indexdir.zip      # Sample indexed data
├── static/                      # Static assets (e.g., logos, images)
│   └── rill-search-logo.png     # Logo for the search engine
├── templates/                   # HTML templates for Flask
│   ├── home.html                # Landing page template
│   └── search.html              # Search results page template
│   └── includes/                # Shared templates
│       └── search_form.html     # Search form template
├── requirements.txt             # Python dependencies
├── README.md                    # Project documentation
├── LICENSE                      # Apache license
├── .env                         # Environment variables (for the OpenAI API key)
├── .gitignore                   # Files to ignore in Git
```

## License

This project is licensed under the APACHE Version 2.0 License - see the [LICENSE](LICENSE) file for details.
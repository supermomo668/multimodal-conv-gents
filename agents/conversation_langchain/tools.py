import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from langchain.tools import tool

@tool("process_search_tool", return_direct=False)
def process_search_tool(url: str) -> str:
    """Used to process content found on the internet."""
    response = requests.get(url=url)
    soup = BeautifulSoup(response.content, "html.parser")
    return soup.get_text()

@tool("internet_search_tool", return_direct=False)
def internet_search_tool(query: str) -> str:
    """Search provided query on the internet using DuckDuckGo."""
    with DDGS() as ddgs:
        results = [r for r in ddgs.text(query, max_results=5)]
        return results if results else "No results found"

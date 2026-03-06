import requests
from langchain_community.tools.tavily_search import TavilySearchResults
import os

class WebTools:
    def __init__(self, tavily_api_key=None):
        self.tavily_api_key = tavily_api_key or os.environ.get("TAVILY_API_KEY")
        if self.tavily_api_key:
            self.search_tool = TavilySearchResults(api_key=self.tavily_api_key)
        else:
            self.search_tool = None

    def search(self, query):
        """Searches the web for the given query."""
        if self.search_tool:
            return self.search_tool.run(query)
        else:
            # Simple fallback using requests to a public search API or DDG (DuckDuckGo)
            # For brevity, let's just return a placeholder message
            return f"Search for '{query}' (Tavily API key not provided)"

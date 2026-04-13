from tavily import TavilyClient
from arya.core.config import Config

class SearchModule:
    def __init__(self):
        self.api_key = Config.TAVILY_API_KEY
        if self.api_key:
            self.client = TavilyClient(api_key=self.api_key)
        else:
            self.client = None

    def search_web(self, query: str) -> str:
        """Searches the internet for real-time information, news, or latest trends."""
        if not self.client:
            return "Tavily API key is missing. I cannot execute the web search."
        
        try:
            # We use basic search to be fast, but advanced can be used for deep research
            response = self.client.search(query=query, search_depth="basic")
            
            if "results" in response and response["results"]:
                summary_lines = []
                for idx, res in enumerate(response["results"][:3]):
                    summary_lines.append(f"Result {idx+1}: {res.get('content')} (Source: {res.get('url')})")
                return "\n\n".join(summary_lines)
            return "I searched the web but found no relevant results."
        except Exception as e:
            return f"An error occurred during web search: {str(e)}"

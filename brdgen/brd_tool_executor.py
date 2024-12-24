# Sample tool to interact with Tavily API
# TODO - Implement an actual tool as needed

import json
import os

from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()


class BRDExternalTool:
    def __init__(self):
        self.client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

    def search(self, query="What is the Background of SAP in 50 words?") -> str:
        result = self.client.search(query, limit=1)
        return result["results"][0]["content"]

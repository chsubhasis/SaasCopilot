# Sample tool to interact with Tavily API
# TODO - Implement an actual tool as needed

from tavily import TavilyClient
import os
import json
from dotenv import load_dotenv

load_dotenv()


class BRDExternalTool:
    def __init__(self):
        self.client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

    def search(self, query="What is the Background of SAP in 50 words?") -> str:
        result = self.client.search(query, limit=1)
        return result["results"][0]["content"]


# Below code is for testing only
if __name__ == "__main__":
    brdtool = BRDExternalTool()
    print(brdtool.search())

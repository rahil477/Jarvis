import trafilatura
from duckduckgo_search import DDGS
from Jarvis.utils.logger import logger

class WebEngine:
    def __init__(self):
        self.ddgs = DDGS()

    def search(self, query, max_results=5):
        """Tier 3: External World - Web Search"""
        try:
            results = self.ddgs.text(query, max_results=max_results)
            return results
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def scrape(self, url):
        """Tier 3: External World - Deep Research Scraping"""
        try:
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                result = trafilatura.extract(downloaded)
                return result
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
        return ""

    def deep_research(self, topic):
        """Tier 3: Deep Research Mode Implementation"""
        logger.info(f"Starting Deep Research on: {topic}")
        search_results = self.search(topic, max_results=3)
        
        research_data = []
        for res in search_results:
            url = res.get('href')
            title = res.get('title')
            content = self.scrape(url)
            if content:
                research_data.append(f"SOURCE: {title}\nURL: {url}\nCONTENT: {content[:1000]}...")
        
        return "\n\n".join(research_data) if research_data else "No data found."

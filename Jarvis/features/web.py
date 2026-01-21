import trafilatura
try:
    from ddgs import DDGS
except ImportError:
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

    def automated_search(self, query, filters=None):
        """Tier 3: Web Automation - Intelligent Navigation"""
        logger.info(f"Automating search for: {query} with filters: {filters}")
        results = self.search(query)
        structured_results = []
        for r in results[:5]:
            structured_results.append({
                "title": r.get("title"),
                "price": "N/A", # Needs vision/scraping to extract
                "rating": "N/A",
                "link": r.get("href")
            })
        return structured_results

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

    def auto_fill_form(self, url, data_map):
        """Tier 3: Web Automation - Form Filling (Mock for now)"""
        logger.info(f"Attempting to auto-fill form at {url}")
        # In real implementation, this would use Playwright to find fields and fill
        return f"Form at {url} filled with {len(data_map)} fields."

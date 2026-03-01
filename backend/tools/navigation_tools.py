# navigation_tools.py - CORREGIDO
import asyncio
import sys  # ¡IMPORTANTE!
import json
import re
import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from core.scraper import LLMFriendlyScraper
import yfinance as yf
from utils.tool_decorator import tool

try:
    import arxiv
except ImportError:
    import sys as _sys
    _sys.stderr.write("Warning: arxiv library not found. pip install arxiv\n")
    arxiv = None

class NavigationTools:
    @tool()
    async def web_search_general(self, query: str) -> str:
        """
        DEFAULT SEARCH TOOL. Use this for ANY question about the real world:
        news, weather, prices, companies, people, events, technology, internships, jobs, etc.
        This is the MAIN tool for answering user questions that need internet data.
        :param query: The search query (e.g. "weather in Tokyo", "Yandex internships 2024")
        """
        url = "https://lite.duckduckgo.com/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {"q": query, "kl": "us-en"}
        
        try:
            resp = requests.post(url, headers=headers, data=data, timeout=15)
            
            if resp.status_code != 200:
                return f"Search Error: HTTP {resp.status_code}"
            
            soup = BeautifulSoup(resp.text, "html.parser")
            links = soup.select("a.result-link")[:5]
            snippets = soup.select("td.result-snippet")[:5]
            
            if not links:
                return f"No results found for: {query}"
            
            # Construir respuesta
            summary = f"## 🔍 SEARCH RESULTS: {query}\n\n"
            urls_to_scrape = []
            
            for i, (link, snippet) in enumerate(zip(links, snippets), 1):
                title = link.get_text(strip=True)
                href = link.get("href", "")
                desc = snippet.get_text(strip=True) if snippet else "No description"
                
                summary += f"### {i}. {title}\n"
                summary += f"**URL:** {href}\n"
                summary += f"**Preview:** {desc}\n\n"
                
                if href.startswith(("http://", "https://")):
                    urls_to_scrape.append(href)
            
            # Scraping profundo
            if urls_to_scrape:
                try:
                    scraper = LLMFriendlyScraper()
                    scraped_pages = await scraper.scrape_multiple(urls_to_scrape, max_urls=3,max_concurrent=3)
                    
                    if scraped_pages:
                        summary += "\n## 📖 DETAILED CONTENT:\n\n"
                        for page in scraped_pages:
                            summary += f"### 📰 {page.get('title', 'Untitled')}\n"
                            summary += f"**Source:** {page.get('url', 'N/A')}\n\n"
                            
                            content = page.get('markdown', '')
                            if len(content) > 1500:
                                content = content[:1500] + "...\n*(truncated)*"
                            
                            summary += f"{content}\n\n---\n\n"
                except Exception as e:
                    # Error silencioso, no agregamos nada al resultado
                    pass
            
            return summary
            
        except Exception as e:
            return f"Search Error: {str(e)[:100]}"
    
    @tool()
    async def scrape_url(self, url: str) -> str:
        """
        Reads and extracts text content from a specific URL.
        Use AFTER web_search_general to get full page content from a result URL.
        Returns clean text (no HTML). Use this to get REAL DATA from web pages.
        :param url: The full URL to scrape (e.g. "https://finance.yahoo.com/quote/GOOG/history/")
        """
        try:
            def fetch():
                return requests.get(url, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }, timeout=10)
            
            resp = await asyncio.to_thread(fetch)
            
            if resp.status_code != 200:
                return f"HTTP Error {resp.status_code}"
            
            soup = BeautifulSoup(resp.text, "html.parser")
            
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.extract()
            
            text = soup.get_text(separator="\n")
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            return '\n'.join(chunk for chunk in chunks if chunk)[:5000]
            
        except Exception as e:
            return f"HTTP Fallback Error: {str(e)}"

    @tool()
    def arxiv_research(self, query: str, max_results: int = 5) -> str:
        """
        Searches arXiv for academic papers. ONLY use when user explicitly says 'arxiv', 'avix', 'papers', or 'scientific papers'.
        Do NOT use for general questions, news, weather, or company info.
        :param query: Academic search query
        :param max_results: Number of papers to return (default: 5)
        """
        if not arxiv:
            return "Error: The 'arxiv' library is not installed. Please run 'pip install arxiv'."
        try:
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.Relevance
            )
            results = list(search.results())
            
            if not results:
                return "No results found on arXiv."
            
            formatted = "PAPERS FOUND ON ARXIV:\n\n"
            for i, r in enumerate(results, 1):
                formatted += f"## Paper {i}: {r.title}\n"
                formatted += f"Summary: {r.summary[:300]}...\n"
                formatted += f"Web Link: {r.entry_id}\n"
                formatted += f"PDF Link: {r.pdf_url}\n"
                formatted += "---\n\n"
            return formatted
        except Exception as e:
            return f"Error searching arXiv: {str(e)}"

    @tool()
    def stock_data(self, ticker: str, period: str = "1y") -> str:
        """
        Gets REAL stock market data (prices, volume) for any company.
        Returns CSV-formatted data with Date, Open, High, Low, Close, Volume.
        Use this for stock prices, market data, financial history.
        :param ticker: Stock ticker symbol (e.g. "GOOG", "AAPL", "MSFT", "TSLA", "KO")
        :param period: Time period - "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "max"
        """
        try:
            ticker = ticker.strip().upper()
            stock = yf.Ticker(ticker)
            df = stock.history(period=period)
            
            if df.empty:
                return f"No data found for ticker '{ticker}'. Verify the symbol is correct (e.g., 'KO' for Coca-Cola, 'AAPL' for Apple)."
            
            # Format as CSV text
            csv_text = "Date,Open,High,Low,Close,Volume\n"
            # Limit rows if too many for the LLM context (e.g., last 30 days of data if > 30)
            rows_to_show = df.tail(60) if len(df) > 60 else df
            
            for date, row in rows_to_show.iterrows():
                csv_text += f"{date.strftime('%Y-%m-%d')},{row['Open']:.2f},{row['High']:.2f},{row['Low']:.2f},{row['Close']:.2f},{int(row['Volume'])}\n"
            
            try:
                name = stock.info.get('longName', ticker)
            except:
                name = ticker
            
            result = f"## Stock Data: {name} ({ticker})\n"
            result += f"Period: {period} | Records shown: {len(rows_to_show)} (out of {len(df)})\n"
            result += f"Current Price: ${df['Close'].iloc[-1]:.2f}\n"
            result += f"Period High: ${df['High'].max():.2f} | Period Low: ${df['Low'].min():.2f}\n\n"
            result += f"### CSV DATA (Tail):\n{csv_text}"
            
            return result
        except Exception as e:
            return f"Error fetching stock data: {str(e)}"
    
    @tool()
    def voice_to_query(self, transcript: str) -> str:
        """
        INTERNAL ONLY. Converts raw audio transcription text into a clean query.
        Only use when processing actual voice/audio input, NOT for normal text queries.
        :param transcript: Raw voice transcription text from audio input
        """
        # This is a placeholder. A real implementation would use an LLM to clean up the transcript.
        return transcript.strip()
# navigation_tools.py - CORREGIDO
import asyncio
import sys  # ¡IMPORTANTE!
import json
import re
import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from core.scraper import LLMFriendlyScraper

class NavigationTools:
    async def autonomous_research(self, topic: str) -> str:
        """Solo devuelve texto, sin prints a stdout"""
        url = "https://lite.duckduckgo.com/lite/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {"q": topic, "kl": "us-en"}
        
        try:
            resp = requests.post(url, headers=headers, data=data, timeout=15)
            
            if resp.status_code != 200:
                return f"Search Error: HTTP {resp.status_code}"
            
            soup = BeautifulSoup(resp.text, "html.parser")
            links = soup.select("a.result-link")[:5]
            snippets = soup.select("td.result-snippet")[:5]
            
            if not links:
                return f"No results found for: {topic}"
            
            # Construir respuesta
            summary = f"## 🔍 SEARCH RESULTS: {topic}\n\n"
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
                    scraped_pages = await scraper.scrape_multiple(urls_to_scrape, max_urls=3)
                    
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
    
    async def read_page_http(self, url: str) -> str:
        """Sin prints a stdout"""
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
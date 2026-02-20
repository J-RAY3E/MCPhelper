import os
import asyncio
import sys
from typing import List, Dict, Optional

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode, LLMConfig, BrowserConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

os.environ["CRAWL4AI_LOG_LEVEL"] = "ERROR"


class LLMFriendlyScraper:
    """
    Scraper optimizado para extracción con LLM:
    - Usa servidores OpenAI-compatibles (llama.cpp, vLLM, etc.)
    - Extracción inteligente por bloques con filtro
    - Fallback seguro a markdown básico
    """
    def __init__(self):
        self.instruction = (
                "You are a content filter. Process each text block independently:\n"
                "\n"
                "EXAMPLES:\n"
                "Query: 'What anime are in the list?'\n"
                "Block: 'Popular anime: Naruto, One Piece, Attack on Titan'\n"
                "Response: [Naruto, One Piece, Attack on Titan]\n"
                "\n"
                "Block: 'Copyright information and site navigation links'\n"
                "Response: [EMPTY]\n"
                "\n"
                "RULES:\n"
                "- Extract only direct answers (max 3 items)\n"
                "- No relevant data = [EMPTY]\n"
                "- No explanations\n\n"
                "Your response: [items...] or [EMPTY]"
            )
        self.llm_config = LLMConfig(
            provider="openai/local", 
            api_token="sk-no-key",
            base_url="http://localhost:8080/v1"
        )

    def getInstruction(self,query):
        return f"Query: '{query}'\n\n" + self.instruction

    async def scrape_multiple(
        self,
        urls: List[str],
        max_urls: int = 5,
        query: Optional[str] = None,
        max_concurrent: int = 3
    ) -> List[Dict[str, str]]:

        urls = urls[:max_urls]
        print(f"[SCRAPER] Scraping {len(urls)} URLs",
              file=sys.stderr, flush=True)

        # ---------- LLM STRATEGY ----------
        strategy = None
        if query:
            print(f"[SCRAPER] LLM extraction enabled for: {query}",
                  file=sys.stderr, flush=True)
            
            llm_config = self.llm_config
            instruction = self.getInstruction(query)
            

            strategy = LLMExtractionStrategy(
                llm_config=llm_config,
                extraction_type="block",
                instruction=instruction,
                chunk_token_threshold=800,
                overlap_rate=0.2,
                extra_args={
                    "temperature": 0.1,
                    "max_tokens": 50,
                    "top_p": 0.97,
                    "presence_penalty": 0.1
                }
            )
        
        # ---------- CONTENT FILTER & MARKDOWN ----------
        pruning_filter = PruningContentFilter(threshold=0.48)
        md_generator = DefaultMarkdownGenerator(
            content_filter=pruning_filter,
            options={"ignore_links": True}
        )

        # ---------- CRAWL CONFIG ----------
        crawl_config = CrawlerRunConfig(
            markdown_generator=md_generator,
            extraction_strategy=strategy,
            cache_mode=CacheMode.ENABLED, 
            verbose = False
        )

        
        async with AsyncWebCrawler(verbose=False) as crawler:
            # Opcional: limitar concurrencia con semáforo
            semaphore = asyncio.Semaphore(max_concurrent)

            async def crawl_one(url):
                async with semaphore:
                    return await crawler.arun(url=url, config=crawl_config)

            tasks = [crawl_one(url) for url in urls]
            results = await asyncio.gather(*tasks, return_exceptions=True) 

        scraped: List[Dict[str, str]] = []
        for url, result in zip(urls, results):
            if isinstance(result, Exception):
                print(f"[SCRAPER] ❌ Failed {url}: {result}", file=sys.stderr, flush=True)
                continue

            # Verificar éxito del crawl
            if not result.success:
                print(f"[SCRAPER] ❌ Crawl not successful for {url}", file=sys.stderr, flush=True)
                continue

            content_to_use = ""

            # 1. Contenido extraído por LLM (si se usó)
            if strategy and hasattr(result, 'extracted_content') and result.extracted_content:
                llm_output = result.extracted_content.strip()
                if llm_output and len(llm_output) >= 5:
                    content_to_use = llm_output
                    print(f"[SCRAPER] ✓ LLM extracted from {url}", file=sys.stderr, flush=True)

            # 2. Fallback a markdown filtrado
            if not content_to_use and hasattr(result, 'markdown'):
                md_obj = result.markdown
                if hasattr(md_obj, 'fit_markdown') and md_obj.fit_markdown:
                    markdown = md_obj.fit_markdown.strip()
                    if len(markdown) >= 50:
                        content_to_use = markdown
                        print(f"[SCRAPER] ↳ Using filtered markdown from {url}", file=sys.stderr, flush=True)

            if content_to_use:
                scraped.append({
                    "url": url,
                    "title": result.metadata.get("title", "Untitled") if hasattr(result, 'metadata') else "Untitled",
                    "markdown": content_to_use,
                    "success": True
                })
            else:
                print(f"[SCRAPER] ✗ No valid content from {url}", file=sys.stderr, flush=True)

        print(f"[SCRAPER] Done: {len(scraped)}/{len(urls)} pages OK", file=sys.stderr, flush=True)
        return scraped
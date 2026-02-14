import asyncio
from crawl4ai import AsyncWebCrawler,CrawlerRunConfig,CacheMode,LLMConfig,BrowserConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
import litellm
from litellm import completion
import os


litellm.drop_params = True
litellm.suppress_debug_info = True

litellm._turn_on_debug() 

async def main():
    os.environ["CRAWL4AI_CACHE_DIR"] = "./cache"
    links = [
        "https://myanimelist.net/stacks/23722",
    ]
    query = "what anime is in this list?"

    llm_config = LLMConfig(
            provider="openai/local", 
            api_token="sk-no-key",
            base_url="http://localhost:8080/v1"
        )
        # 2. Creamos la estrategia usando el config
    instruction = (
        f"Query: '{query}'\n\n"
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
    strategy = LLMExtractionStrategy(
        llm_config=llm_config,
        extraction_type="block",
        instruction=instruction,
        chunk_token_threshold=800, # Bloques pequeños = procesamiento más rápido y preciso
        overlap_rate=0.2,
        extra_args={
            "temperature": 0.1,      # 0.06 es casi igual, 0.1 es estándar para hechos
            "max_tokens": 50,       # Limita la respuesta del modelo (ahorra VRAM)
            "top_p": 0.97,            # Ayuda a que no se repita
            "presence_penalty": 0.1  # Evita que repita las mismas frases
        }
    )
    pruning_filter = PruningContentFilter(
        threshold=0.48
    )
    md_generator = DefaultMarkdownGenerator(content_filter=pruning_filter, options={"ignore_links": True})

    crawl_config = CrawlerRunConfig(
        markdown_generator=md_generator,
        extraction_strategy=strategy
        
    )
    litellm._turn_on_debug()

    async with AsyncWebCrawler() as crawler:

        for link in links:
            result = await crawler.arun(link, config=crawl_config)
            if result.success:
                # If a filter is used, we also have .fit_markdown:
                md_object = result.markdown  # or your equivalent
                print("Filtered markdown:\n", md_object.fit_markdown)
            else:
                print("Crawl failed:", result.error_message)

if __name__ == "__main__":
    asyncio.run(main())
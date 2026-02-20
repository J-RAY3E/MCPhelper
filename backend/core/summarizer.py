"""LLM-based Summarizer implementation."""
from typing import List

from core.interfaces import BaseSummarizer


class LLMSummarizer(BaseSummarizer):
    """Uses an LLM to generate final responses."""
    
    def __init__(self, llm_client):
        """
        Args:
            llm_client: LLMClient instance (supports .chat() method)
        """
        self.llm = llm_client
    
    async def summarize(self, task: str, results: List[str]) -> str:
        """Create a user-facing summary from execution results."""
        
        # Filter out error-only results
        valid_results = [r for r in results if not r.startswith("Error executing")]
        
        if not valid_results:
            return "No se pudieron obtener resultados. Por favor intenta de nuevo."
        
        results_text = chr(10).join(
            f'--- Result {i+1} ---\n{r[:2000]}' for i, r in enumerate(valid_results)
        )
        
        summary_prompt = f"""USER QUESTION: {task}

TOOL RESULTS (this data is REAL, already fetched from the internet/APIs):
{results_text}

Using ONLY the data above, write a clear and helpful answer for the user.
Do NOT add disclaimers about not being able to access real-time data.
The data above IS real-time data, already fetched by tools on your behalf."""
        
        system_msg = (
            "You are a helpful assistant. You have been given REAL DATA that was already "
            "fetched from the internet by automated tools. This data is REAL and CURRENT. "
            "Your job is to summarize it clearly for the user. "
            "FORBIDDEN PHRASES (never use these): "
            "'I cannot access real-time data', "
            "'I cannot browse the internet', "
            "'As an AI language model', "
            "'I don't have access to'. "
            "The data is ALREADY PROVIDED TO YOU. Use it."
        )
        
        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": summary_prompt}
        ]
        return self.llm.chat(messages, temperature=0.5)

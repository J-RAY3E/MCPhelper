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
        summary_prompt = f"""Task: {task}
Execution Log:
{chr(10).join(f'- Step {i+1}: {r[:300]}...' for i, r in enumerate(results))}

Based on the execution log above, provide a final answer to the user.
"""
        
        messages = [{"role": "user", "content": summary_prompt}]
        return self.llm.chat(messages, temperature=0.7)

"""Professional LLM Summarizer implementation."""
from typing import List
from core.interfaces import BaseSummarizer

class LLMSummarizer(BaseSummarizer):
    """Refined summarizer for high-quality, professional reports."""
    
    def __init__(self, llm_client):
        self.llm = llm_client
    
    async def summarize(self, task: str, results: List[str]) -> str:
        """Create a professional market intelligence summary."""
        
        valid_results = [r for r in results if not r.startswith("Error executing")]
        if not valid_results:
            return "Unable to process the request due to missing tool data. Please try a more specific topic."
        
        results_text = chr(10).join(f'--- Tool Result {i+1} ---\n{r}' for i, r in enumerate(valid_results))
        
        system_msg = (
            "You are a Senior Intelligence Analyst. You have been provided with REAL-TIME DATA "
            "already fetched from the internet. Your job is to deliver a professional report. "
            "\n\nSTYLE RULES:\n"
            "1. USE LaTeX for ALL mathematical notation and statistics (e.g. use $\\mu$, $\\sigma$, $E=mc^2$).\n"
            "2. Wrap LaTeX blocks in double dollar signs $$ ... $$ for clarity.\n"
            "3. Use professional, clean Markdown with clear headers and bullet points.\n"
            "4. NEVER use filler phrases like 'As an AI language model' or 'I don't have access to live data'.\n"
            "5. The data provided is REAL. Trust it and summarize it elegantly."
        )
        
        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": f"USER INQUIRY: {task}\n\nRAW DATA GATHERED:\n{results_text}"}
        ]
        return self.llm.chat(messages, temperature=0.3)

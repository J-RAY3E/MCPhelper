"""Conversation Context and Query Rewriter."""
from typing import List, Dict, Optional

class ConversationContext:
    """Maintains a sliding window of conversation history and rewrites queries."""
    
    def __init__(self, max_turns: int = 2):
        self.history: List[Dict[str, str]] = []
        self.max_turns = max_turns  # Keep last N exchanges (Reduced for speed)
    
    def add(self, user_text: str, assistant_response: str):
        """Add an exchange to history."""
        self.history.append({"user": user_text, "assistant": assistant_response})
        if len(self.history) > self.max_turns:
            self.history.pop(0)
            
    def get_context_string(self) -> str:
        """Format history for the LLM."""
        if not self.history:
            return ""
        
        ctx = "CONVERSATION HISTORY:\n"
        for turn in self.history:
            ctx += f"User: {turn['user']}\n"
            # Summarize assistant response heavily to save tokens/time
            summary = turn['assistant'][:100] + "..." if len(turn['assistant']) > 100 else turn['assistant']
            ctx += f"Assistant: {summary}\n\n"
        return ctx

    async def rewrite_query(self, user_input: str, llm_client) -> str:
        """
        Rewrites user input to be self-contained based on context.
        If context is empty or query is already clear, returns original.
        """
        if not self.history:
            return user_input
            
        prompt = f"""You are a Query Rewriter. Your job is to make the user's last question SELF-CONTAINED by adding missing context from history.

{self.get_context_string()}
CURRENT USER INPUT: "{user_input}"

INSTRUCTIONS:
1. If the input is a follow-up (e.g. "what about usage?", "how much?", "process for that?"), REWRITE it to include the subject from history.
2. If the input is a new topic or command (e.g. "clear", "exit", "weather in London"), RETURN IT AS IS.
3. Do NOT answer the question. Only rewrite it.
4. Output ONLY the rewritten query. No quotes.

REWRITTEN QUERY:"""

        messages = [{"role": "user", "content": prompt}]
        
        # chat() is SYNCHRONOUS - do NOT use await
        rewritten = llm_client.chat(messages, temperature=0.1)
        
        # Cleanup
        rewritten = rewritten.strip().strip('"')
        return rewritten

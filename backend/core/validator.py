"""Plan Validator implementation."""
import re
import json
from typing import List, Dict, Any

from core.interfaces import BasePlanValidator
from prompts.validator_prompt import VALIDATOR_PROMPT


class LLMPlanValidator(BasePlanValidator):
    """Uses an LLM to validate and normalize plans."""
    
    def __init__(self, llm_client):
        """
        Args:
            llm_client: LLMClient instance (supports .chat() method)
        """
        self.llm = llm_client
    
    def _extract_json(self, text: str) -> List[Dict[str, Any]]:
        """Helper to extract JSON list from text."""
        try:
            # Try to find JSON array block
            match = re.search(r'\[.*\]', text, re.DOTALL)
            if match:
                return json.loads(match.group())
            return []
        except json.JSONDecodeError:
            return []

    async def validate(self, raw_plan: str) -> List[Dict[str, Any]]:
        """
        Validate raw plan.
        1. Fast Path: Try to parse directly.
        2. Slow Path: If parse fails, ask LLM to fix it.
        """
        # FAST PATH: Try direct parse first to avoid LLM rewriting (and breaking) args
        params_fast = self._extract_json(raw_plan)
        if params_fast and isinstance(params_fast, list) and len(params_fast) > 0:
            # Basic schema check
            if all('tool' in step and 'args' in step for step in params_fast):
                return params_fast

        # SLOW PATH: LLM Validation
        messages = [
            {"role": "system", "content": VALIDATOR_PROMPT},
            {"role": "user", "content": raw_plan}
        ]
        
        validated = self.llm.chat(messages, temperature=0.0) # Zero temp for strictness
        
        return self._extract_json(validated)

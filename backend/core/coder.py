"""
Direct Code Generator.
Bypasses the planner for pure code generation tasks.
"""
import re
import os
from typing import Dict
from utils.llm_client import LLMClient
from prompts.coder_prompt_v2 import CODER_PROMPT_V2

class DirectCoder:
    """Generates code files directly from user descriptions."""
    
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        
    async def generate_code(self, user_request: str) -> Dict[str, str]:
        """
        Generates code based on request.
        Returns dict with keys: 'path', 'code', 'description'.
        """
        prompt = CODER_PROMPT_V2.format(user_request=user_request)
        
        messages = [
            {"role": "system", "content": prompt},
            # The user message is now empty as the query is part of the system prompt.
            {"role": "user", "content": ""}
        ]
        
        # Use a temperature of 0.0 for deterministic and high-quality code.
        response = self.llm.chat(messages, temperature=0.0)
        
        return self._parse_response(response)
    
    def _parse_response(self, text: str) -> Dict[str, str]:
        """Parses the specialized output format."""
        path_match = re.search(r"FILEPATH:\s*(.+)", text)
        desc_match = re.search(r"DESCRIPTION:\s*(.+)", text)
        code_match = re.search(r"CODE:\s*```(?:python)?\n(.*?)```", text, re.DOTALL)
        
        path = path_match.group(1).strip() if path_match else "generated_script.py"
        desc = desc_match.group(1).strip() if desc_match else "Generated script"
        code = code_match.group(1).strip() if code_match else text # Fallback to raw text if no block
        
        # Clean up path separators
        path = path.replace("\\", "/")
        if not path.startswith("scripts/"):
             # Force into scripts/ if not specified otherwise
             if "/" not in path:
                 path = f"scripts/{path}"
        
        return {
            "path": path,
            "code": code,
            "description": desc
        }

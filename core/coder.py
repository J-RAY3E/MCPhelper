"""
Direct Code Generator.
Bypasses the planner for pure code generation tasks.
"""
import re
import os
from typing import Dict
from utils.llm_client import LLMClient

CODER_SYSTEM_PROMPT = """You are an Expert Python Developer.
Your task is to write COMPLETE, PRODUCTION-READY code files based on user requests.

Rules:
1. Output ONLY the code for a single file.
2. NO conversational filler ("Here is the code...").
3. Include imports, type hints, and docstrings.
4. If the user asks for a script, make it runnable (if __name__ == "__main__":).
5. Use modern Python best practices (SOLID, clean code).

Format your response exactly like this:

FILEPATH: <suggested/path/filename.py>
DESCRIPTION: <brief description of what the code does>
CODE:
```python
<your code here>
```
"""

class DirectCoder:
    """Generates code files directly from user descriptions."""
    
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        
    async def generate_code(self, user_request: str) -> Dict[str, str]:
        """
        Generates code based on request.
        Returns dict with keys: 'path', 'code', 'description'.
        """
        messages = [
            {"role": "system", "content": CODER_SYSTEM_PROMPT},
            {"role": "user", "content": f"Create a script for: {user_request}"}
        ]
        
        # Use higher temperature for creativity in coding, but still controlled
        response = self.llm.chat(messages, temperature=0.2)
        
        return self._parse_response(response)
    
    def _parse_response(self, text: str) -> Dict[str, str]:
        """Parses the specialized output format."""
        path_match = re.search(r"FILEPATH:\s*(.+)", text)
        desc_match = re.search(r"DESCRIPTION:\s*(.+)", text)
        code_match = re.search(r"CODE:\s*```(?:\w+)?\n(.*?)```", text, re.DOTALL)
        
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

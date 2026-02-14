import os
from mcp.server.fastmcp import FastMCP
from system_tools import SystemTools
from navigation_tools import NavigationTools
from redaction_tools import RedactionTools

# Standard MCP server initialization
# Server name: MCP-Helper
mcp = FastMCP("MCP-Helper")

# Instance of original tools to maintain logic
workspace_path = os.getcwd()
system = SystemTools(workspace_path)
navigation = NavigationTools()
redaction = RedactionTools()

# --- SYSTEM TOOLS (SYSTEM) ---

@mcp.tool()
def create_file(path: str, content: str, purpose: str = "general") -> str:
    """
    Creates a file in the workspace. Files are auto-organized by purpose:
    - purpose='scripts' -> scripts/ folder, .py extension
    - purpose='research' -> research/ folder, .md extension
    - purpose='redaction' -> redaction/ folder, .md extension  
    - purpose='general' -> storage/ folder, .txt extension
    
    :param path: Just the filename (e.g. 'merge_sort'), folder and extension are auto-added.
    :param content: The FULL file content. For scripts, must be valid Python code.
    :param purpose: 'scripts' | 'research' | 'redaction' | 'general'
    """
    result = system.create_file(path, content, purpose)
    return f"File created at: {result.get('path')}"

@mcp.tool()
def configure_folder(purpose: str, folder_name: str) -> str:
    """
    Creates a new organization directory and registers it in the configuration.
    :param purpose: The category name (e.g. 'images', 'backups').
    :param folder_name: The physical folder name to be created.
    """
    result = system.add_managed_folder(purpose, folder_name)
    return result.get("message")

@mcp.tool()
def list_structure(directory: str = ".") -> str:
    """
    Shows all files and folders in the workspace. Use FIRST to find existing files.
    Folders: scripts/ (Python), research/ (docs), redaction/ (writing), storage/ (misc)
    :param directory: Optional subfolder to list (e.g. 'scripts' or '.' for root)
    """
    return system.list_directory_tree(directory)

@mcp.tool()
def read_file(path: str) -> str:
    """
    Reads content of an existing file. Use list_structure first to find files.
    :param path: Relative path (e.g. 'scripts/merge_sort.py' or 'storage/notes.txt')
    """
    return system.read_file(path)

@mcp.tool()
def delete_file(path: str, confirm: bool = False) -> str:
    """
    Permanently deletes a file or directory.
    WARNING: This is a destructive action. 
    To confirm deletion, you MUST set the 'confirm' parameter to True. 
    If 'confirm' is False, the tool will only return a warning message without deleting anything.
    """
    result = system.delete_file(path, confirm)
    return result.get("message", "Error deleting")

@mcp.tool()
def code_review(path: str) -> str:
    """
    Reviews a Python script for syntax errors. Use AFTER create_file to verify code.
    :param path: Path to .py file (e.g. 'scripts/merge_sort.py')
    """
    result = system.code_review(path)
    if result["status"] == "ok":
        return "✅ Code review passed. No errors."
    elif result["status"] == "warning":
        return f"⚠️ {result['message']}: {', '.join(result.get('issues', []))}"
    else:
        return f"❌ {result.get('error_type', 'Error')}: {result.get('message', '')} (Line {result.get('line', '?')})"

@mcp.tool()
def code_fix(path: str, error_description: str) -> str:
    """
    Auto-fixes Python errors (tabs, whitespace). Use after code_review finds issues.
    :param path: Path to .py file (e.g. 'scripts/merge_sort.py')
    :param error_description: Error message from code_review
    """
    result = system.code_fix(path, error_description)
    if result["status"] == "fixed":
        return f"✅ Fixed: {', '.join(result.get('fixes', []))}"
    elif result["status"] == "no_changes":
        return f"⚠️ {result['message']} Hint: {result.get('hint', '')}"
    else:
        return f"❌ Error: {result.get('message', '')}"

# --- REDACTION TOOLS (REDACTION) ---

@mcp.tool()
def summarize_text(text: str, level: str = "basic") -> str:
    """
    Generates a summary of the provided text.
    :param text: Original text.
    :param level: Summary level ('basic' or 'technical').
    """
    return redaction.summarize_text(text, level)

@mcp.tool()
def parse_to_latex(text: str) -> str:
    """
    Converts plain text into a legal LaTeX document structure.
    """
    return redaction.parse_to_latex(text)

# --- NAVIGATION TOOLS (NAVIGATION) ---

@mcp.tool()
def arxiv_research(query: str, max_results: int = 5) -> str:
    """
    SCIENTIFIC TOOL (Arxiv / Avix / Papers). 
    USE IT for any 'avix', 'technical research' or 'science' topic.
    Returns papers with summaries and PDF download links.
    """
    results = navigation.arxiv_search(query, max_results)
    if not results:
        return "No results found on arXiv."
    
    formatted = "PAPERS FOUND ON ARXIV:\n\n"
    for i, r in enumerate(results, 1):
        formatted += f"## Paper {i}: {r['title']}\n"
        formatted += f"Summary: {r['summary'][:300]}...\n"
        formatted += f"Web Link: {r['link']}\n"
        formatted += f"PDF Link: {r.get('pdf_link', 'Not available')}\n"
        formatted += "---\n\n"
    
    formatted += "\nINSTRUCTION: For each important paper, create a .md file with:\n"
    formatted += "- Title as filename\n"
    formatted += "- Content: Full summary + PDF download link\n"
    formatted += "- purpose='research'\n"
    return formatted

@mcp.tool()
async def web_search_general(query: str) -> str:
    """
    Basic web search (News, Weather, General). 
    NEVER use it if the user asks for 'avix', 'science' or 'papers'.
    :param query: The search query (e.g. "weather in Tokyo")
    """
    return await navigation.autonomous_research(query)

@mcp.tool()
def voice_to_query(transcript: str) -> str:
    """
    Cleans and extracts search intent from a voice transcript.
    """
    return navigation.voice_intent_to_query(transcript)

if __name__ == "__main__":
    # Starts the MCP server in stdio mode (standard for clients like Claude or Llama-cpp)
    mcp.run()



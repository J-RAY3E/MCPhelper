import os
import shutil
import subprocess
from typing import List, Optional
from utils.tool_decorator import tool

class SystemTools:
    """
    SYSTEM_TOOLS: Local file operations.
    ALL operations are sandboxed inside ./storage/ directory.
    """
    
    # Fixed subdirectory structure inside storage/
    SUBDIRS = {
        "scripts": "scripts",
        "research": "research",
        "redaction": "redaction",
        "docs": "docs",
        "general": "",  # root of storage/
    }
    
    def __init__(self, allowed_base_path: str):
        # The ONLY writable directory — everything lives here
        self.storage_root = os.path.abspath(os.path.join(allowed_base_path, "storage"))
        self.base_path = os.path.abspath(allowed_base_path)  # kept for compatibility
        os.makedirs(self.storage_root, exist_ok=True)
        self._initialize_structure()

    def _initialize_structure(self):
        """Creates subdirectories inside storage/."""
        for subdir in self.SUBDIRS.values():
            if subdir:
                os.makedirs(os.path.join(self.storage_root, subdir), exist_ok=True)

    def _validate_path(self, path: str) -> str:
        """
        Resolves ANY path to be inside storage/.
        Strips leading directories that look like 'storage/' to avoid doubling.
        """
        # Strip absolute paths — force relative
        if os.path.isabs(path):
            path = os.path.basename(path)
        
        # Strip leading 'storage/' or 'storage\\' to avoid storage/storage/
        path = path.replace("\\", "/")
        if path.startswith("storage/"):
            path = path[len("storage/"):]
        
        full_path = os.path.abspath(os.path.join(self.storage_root, path))
        
        # Security check: must stay inside storage/
        if not full_path.startswith(self.storage_root):
            raise PermissionError(f"Access denied: {path} is outside storage/")
        return full_path

    def get_organized_path(self, filename: str, purpose: str = "general") -> str:
        """Returns path inside storage/ based on purpose."""
        subdir = self.SUBDIRS.get(purpose, "")
        if subdir:
            return os.path.join(subdir, filename)
        return filename

    @tool()
    def configure_folder(self, purpose: str, folder_name: str) -> str:
        """
        Creates a new subdirectory inside storage/ for a specific purpose.
        :param purpose: The category name (e.g. 'images', 'backups').
        :param folder_name: The folder name to create inside storage/.
        """
        purpose = purpose.strip().lower()
        folder_name = folder_name.strip().rstrip('/')
        
        self.SUBDIRS[purpose] = folder_name
        target = os.path.join(self.storage_root, folder_name)
        os.makedirs(target, exist_ok=True)
            
        return f"Folder 'storage/{folder_name}' registered for purpose '{purpose}'"

    @tool()
    def create_file(self, path: str, content: str, purpose: str = "general") -> str:
        """
        Creates a file inside storage/. All files are sandboxed here.
        Files are auto-organized by purpose:
        - purpose='scripts' -> storage/scripts/ (.py)
        - purpose='research' -> storage/research/ (.md)
        - purpose='redaction' -> storage/redaction/ (.md)
        - purpose='general' -> storage/ (.txt)
        
        :param path: Just the filename (e.g. 'merge_sort'), folder and extension are auto-added.
        :param content: The FULL file content.
        :param purpose: 'scripts' | 'research' | 'redaction' | 'general'
        """
        filename = os.path.basename(path)
        ext = os.path.splitext(filename)[1]
        
        # Extension deduction if missing
        if not ext:
            if purpose == "scripts":
                path += ".py"
            elif purpose == "research":
                path += ".md"
            elif purpose == "redaction":
                path += ".md"
            else:
                path += ".txt"

        if not os.path.dirname(path) or os.path.dirname(path) == '.':
            path = self.get_organized_path(os.path.basename(path), purpose)
            
        target = self._validate_path(path)
        
        if os.path.isdir(target):
            raise IOError(f"Cannot create file: {path} is an existing directory.")

        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, 'w', encoding='utf-8') as f:
            f.write(content)
        rel_path = os.path.relpath(target, self.storage_root)
        return f"File created at: storage/{rel_path}"

    @tool()
    def read_file(self, path: str) -> str:
        """
        Reads content of an existing file inside storage/.
        :param path: Relative path inside storage (e.g. 'scripts/merge_sort.py' or 'notes.txt')
        """
        target = self._validate_path(path)
        with open(target, 'r', encoding='utf-8') as f:
            return f.read()

    @tool()
    def list_structure(self, directory: str = ".") -> str:
        """
        Shows all files and folders inside storage/. Use FIRST to find existing files.
        Subfolders: scripts/ (Python), research/ (docs), redaction/ (writing)
        :param directory: Subfolder to list inside storage (e.g. 'scripts' or '.' for all)
        """
        target_dir = self._validate_path(directory)
        tree = []
        for root, dirs, files in os.walk(target_dir):
            level = root.replace(target_dir, '').count(os.sep)
            indent = ' ' * 4 * level
            tree.append(f"{indent}{os.path.basename(root)}/")
            sub_indent = ' ' * 4 * (level + 1)
            for f in files:
                tree.append(f"{sub_indent}{f}")
        return "\n".join(tree)

    @tool()
    def delete_file(self, path: str, confirm: bool = False) -> str:
        """
        Permanently deletes a file or directory.
        WARNING: This is a destructive action. 
        To confirm deletion, you MUST set the 'confirm' parameter to True. 
        If 'confirm' is False, the tool will only return a warning message without deleting anything.
        """
        if not confirm:
            return "This is a DESTRUCTIVE action. Please confirm deletion."
        
        target = self._validate_path(path)
        os.remove(target)
        return f"Deleted {path}"

    async def generate_code_file(self, description: str, filename: str = None) -> dict:
        """
        [CODER] Generates a full code file based on description.
        Use this tool when the user asks to 'create a script', 'write code', etc.
        """
        from core.coder import DirectCoder
        from utils.llm_client import LLMClient
        
        # Initialize Coder independently
        llm = LLMClient()
        coder = DirectCoder(llm)
        
        import sys
        sys.stderr.write(f"[CODER] Generating code for: {description}...\n")
        result = await coder.generate_code(description)
        
        # If filename provided, override the one from coder
        if filename:
            result["path"] = filename if "scripts/" in filename else f"scripts/{filename}"
            
        # Ensure path is valid
        target_path = self.get_organized_path(result["path"], "scripts")
        target_path = self._validate_path(target_path)
        
        # Write
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(result["code"])
            
        return {
            "status": "success", 
            "path": result["path"], 
            "description": result["description"]
        }

    # run_script is not a tool because it requires user confirmation and special handling

    @tool()
    def code_review(self, path: str) -> str:
        """
        Reviews a Python script for syntax errors. Use AFTER create_file to verify code.
        :param path: Path to .py file (e.g. 'scripts/merge_sort.py')
        """
        import ast
        import py_compile
        
        target = self._validate_path(path)
        
        if not target.endswith('.py'):
            return "❌ Error: Only Python files can be reviewed"
        
        try:
            with open(target, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # Check 1: Syntax validation with AST
            try:
                ast.parse(code)
            except SyntaxError as e:
                return f"❌ SyntaxError: {str(e.msg)} (Line {e.lineno})"
            
            # Check 2: Compile check (catches more issues)
            try:
                py_compile.compile(target, doraise=True)
            except py_compile.PyCompileError as e:
                return f"❌ CompileError: {str(e)}"
            
            # Check 3: Basic code quality checks
            issues = []
            lines = code.split('\n')
            for i, line in enumerate(lines, 1):
                if len(line) > 120:
                    issues.append(f"Line {i}: Line too long ({len(line)} chars)")
                if '\t' in line and '    ' in line:
                    issues.append(f"Line {i}: Mixed tabs and spaces")
            
            if issues:
                return f"⚠️ Code is valid but has style issues: {', '.join(issues[:5])}"
            
            return "✅ Code review passed. No errors."
            
        except FileNotFoundError:
            return f"❌ Error: File not found: {path}"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    @tool()
    def code_fix(self, path: str, error_description: str) -> str:
        """
        Auto-fixes Python errors (tabs, whitespace). Use after code_review finds issues.
        :param path: Path to .py file (e.g. 'scripts/merge_sort.py')
        :param error_description: Error message from code_review
        """
        target = self._validate_path(path)
        
        if not target.endswith('.py'):
            return "❌ Error: Only Python files can be fixed"
        
        try:
            with open(target, 'r', encoding='utf-8') as f:
                original_code = f.read()
            
            fixed_code = original_code
            fixes_applied = []
            
            # Fix 1: Replace tabs with spaces
            if '\t' in fixed_code:
                fixed_code = fixed_code.replace('\t', '    ')
                fixes_applied.append("Replaced tabs with 4 spaces")
            
            # Fix 2: Remove trailing whitespace
            lines = fixed_code.split('\n')
            cleaned_lines = [line.rstrip() for line in lines]
            if lines != cleaned_lines:
                fixed_code = '\n'.join(cleaned_lines)
                fixes_applied.append("Removed trailing whitespace")
            
            # Fix 3: Ensure file ends with newline
            if not fixed_code.endswith('\n'):
                fixed_code += '\n'
                fixes_applied.append("Added trailing newline")
            
            if fixed_code != original_code:
                with open(target, 'w', encoding='utf-8') as f:
                    f.write(fixed_code)
                return f"✅ Fixed: {', '.join(fixes_applied)}"
            else:
                return f"⚠️ No automatic fixes could be applied. Manual review needed. Hint: {error_description}"
                
        except FileNotFoundError:
            return f"❌ Error: File not found: {path}"
        except Exception as e:
            return f"❌ Error: {str(e)}"

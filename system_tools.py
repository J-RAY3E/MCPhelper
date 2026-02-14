import os
import shutil
import subprocess
from typing import List, Optional

class SystemTools:
    """
    SYSTEM_TOOLS: Local operations.
    The model MUST propose 'SYSTEM' label for these.
    """
    
    def __init__(self, allowed_base_path: str):
        self.base_path = os.path.abspath(allowed_base_path)
        self.folders = self._load_folder_config()
        self._initialize_structure()

    def _load_folder_config(self) -> dict:
        config_path = os.path.join(self.base_path, "sources", "folder_config.txt")
        folders = {"general": "storage"}
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if ':' in line and not line.startswith('['):
                        key, val = line.split(':')
                        folders[key.strip()] = val.strip().rstrip('/')
        return folders

    def _initialize_structure(self):
        """Creates base folders if they don't exist."""
        for folder in self.folders.values():
            target = os.path.join(self.base_path, folder)
            os.makedirs(target, exist_ok=True)

    def _validate_path(self, path: str) -> str:
        # Si el path ya es absoluto y está dentro de base_path, lo respetamos
        if os.path.isabs(path):
            full_path = path
        else:
            full_path = os.path.abspath(os.path.join(self.base_path, path))
            
        if not full_path.startswith(self.base_path):
            raise PermissionError(f"Access denied: {path} is outside allowed directory.")
        return full_path

    def get_organized_path(self, filename: str, purpose: str = "general") -> str:
        """Returns the suggested path based on purpose."""
        folder = self.folders.get(purpose, self.folders["general"])
        return os.path.join(folder, filename)

    def add_managed_folder(self, purpose: str, folder_name: str):
        """Adds a new purpose and folder to the system and config file."""
        purpose = purpose.strip().lower()
        folder_name = folder_name.strip().rstrip('/')
        
        self.folders[purpose] = folder_name
        target = os.path.join(self.base_path, folder_name)
        os.makedirs(target, exist_ok=True)
        
        # Update config file in sources folder
        config_path = os.path.join(self.base_path, "sources", "folder_config.txt")
        new_entry = f"{purpose}: {folder_name}\n"
        
        # Read current content to avoid duplicates
        lines = []
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        
        # Remove if key exists to overwrite
        lines = [l for l in lines if not l.startswith(f"{purpose}:")]
        lines.append(new_entry)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
            
        return {"status": "success", "message": f"Folder '{folder_name}' registered for purpose '{purpose}'"}

    def create_file(self, path: str, content: str, purpose: Optional[str] = None):
        """Creates a file with smart extension deduction."""
        filename = os.path.basename(path)
        ext = os.path.splitext(filename)[1]
        
        # Extension deduction if missing
        if not ext:
            if purpose == "scripts":
                path += ".py"
            elif purpose == "reportes":
                path += ".tex"
            elif purpose == "redaction":
                path += ".md"
            else:
                path += ".txt"

        if purpose and not os.path.dirname(path):
            path = self.get_organized_path(path, purpose)
            
        target = self._validate_path(path)
        
        # Ensure target is not an existing directory
        if os.path.isdir(target):
            raise IOError(f"Cannot create file: {path} is an existing directory.")

        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, 'w', encoding='utf-8') as f:
            f.write(content)
        return {"status": "success", "path": os.path.relpath(target, self.base_path)}

    def read_file(self, path: str) -> str:
        target = self._validate_path(path)
        with open(target, 'r', encoding='utf-8') as f:
            return f.read()

    def list_directory_tree(self, directory: str = ".") -> str:
        """Returns a visual representation of the file structure."""
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

    def search_files(self, query: str, directory: str = ".") -> List[str]:
        target_dir = self._validate_path(directory)
        matches = []
        for root, _, files in os.walk(target_dir):
            for file in files:
                if query in file:
                    matches.append(os.path.relpath(os.path.join(root, file), self.base_path))
        return matches

    def delete_file(self, path: str, confirmed: bool = False):
        """
        DESTRUCTIVE Tool.
        Requires MCP-level confirmation.
        """
        if not confirmed:
            return {"status": "pending_confirmation", "message": "This is a DESTRUCTIVE action. Please confirm deletion."}
        
        target = self._validate_path(path)
        os.remove(target)
        return {"status": "success", "message": f"Deleted {path}"}

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
        
        print(f"[CODER] Generating code for: {description}...")
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


    def run_script(self, path: str, args: Optional[List[str]] = None):
        """
        EXECUTION Tool.
        Requires extra validation and confirmation.
        """
        target = self._validate_path(path)
        # Validation: only allow certain extensions
        if not path.endswith('.py') and not path.endswith('.sh'):
            return {"status": "error", "message": "Execution only allowed for .py or .sh files"}
        
        cmd = ["python", target] if path.endswith('.py') else ["bash", target]
        if args:
            cmd.extend(args)
            
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return {"status": "success", "stdout": result.stdout, "stderr": result.stderr}
        except subprocess.CalledProcessError as e:
            return {"status": "error", "stdout": e.stdout, "stderr": e.stderr}

    def code_review(self, path: str) -> dict:
        """
        Reviews Python code for syntax errors and basic issues.
        Returns errors found or 'OK' if code is valid.
        """
        import ast
        import py_compile
        
        target = self._validate_path(path)
        
        if not target.endswith('.py'):
            return {"status": "error", "message": "Only Python files can be reviewed"}
        
        try:
            with open(target, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # Check 1: Syntax validation with AST
            try:
                ast.parse(code)
            except SyntaxError as e:
                return {
                    "status": "error",
                    "error_type": "SyntaxError",
                    "line": e.lineno,
                    "message": str(e.msg),
                    "code_snippet": e.text.strip() if e.text else ""
                }
            
            # Check 2: Compile check (catches more issues)
            try:
                py_compile.compile(target, doraise=True)
            except py_compile.PyCompileError as e:
                return {
                    "status": "error",
                    "error_type": "CompileError",
                    "message": str(e)
                }
            
            # Check 3: Basic code quality checks
            issues = []
            lines = code.split('\n')
            for i, line in enumerate(lines, 1):
                if len(line) > 120:
                    issues.append(f"Line {i}: Line too long ({len(line)} chars)")
                if '\t' in line and '    ' in line:
                    issues.append(f"Line {i}: Mixed tabs and spaces")
            
            if issues:
                return {
                    "status": "warning",
                    "message": "Code is valid but has style issues",
                    "issues": issues[:5]  # Limit to 5 issues
                }
            
            return {"status": "ok", "message": "Code review passed. No errors found."}
            
        except FileNotFoundError:
            return {"status": "error", "message": f"File not found: {path}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def code_fix(self, path: str, error_description: str) -> dict:
        """
        Attempts to fix common Python errors in a file.
        Currently supports: missing colons, indentation fixes, missing imports.
        
        :param path: Path to the Python file to fix.
        :param error_description: Description of the error to fix.
        """
        target = self._validate_path(path)
        
        if not target.endswith('.py'):
            return {"status": "error", "message": "Only Python files can be fixed"}
        
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
                return {
                    "status": "fixed",
                    "message": "Applied automatic fixes",
                    "fixes": fixes_applied
                }
            else:
                return {
                    "status": "no_changes",
                    "message": "No automatic fixes could be applied. Manual review needed.",
                    "hint": f"Error to investigate: {error_description}"
                }
                
        except FileNotFoundError:
            return {"status": "error", "message": f"File not found: {path}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

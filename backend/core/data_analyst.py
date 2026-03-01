"""
Data Analyst module

Handles /plot and /describe commands.
- Searches for files recursively across all storage subdirectories.
- If the target name looks like a stock ticker/company name rather than a file,
  dynamically fetches historical data via yfinance, saves it to storage/.cache/
  as a temporary CSV, and uses it for analysis.
- The .cache/ directory is purged on DataAnalyst shutdown (registered via atexit).
"""
import os
import re
import json
import atexit
import shutil
import pandas as pd
from typing import Dict, Any, Optional
import yfinance as yf

KNOWN_FILE_EXTENSIONS = {".csv", ".json", ".xls", ".xlsx", ".txt"}


class DataAnalyst:
    def __init__(self, llm, storage_dir: str):
        self.llm = llm
        self.storage_dir = storage_dir
        self.cache_dir = os.path.join(storage_dir, ".cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        # Auto-purge cache directory on process exit
        atexit.register(self._purge_cache)

    # ─────────────────── Cache Lifecycle ──────────────────────────────────────

    def _purge_cache(self):
        """Delete all temporary files in .cache/ on shutdown."""
        try:
            shutil.rmtree(self.cache_dir, ignore_errors=True)
        except Exception:
            pass

    # ─────────────────── File Resolution ──────────────────────────────────────

    def _find_file_recursive(self, target: str) -> Optional[str]:
        """
        Recursively search all subdirectories of storage_dir for a file
        whose name contains the target string (case-insensitive).
        Returns the full absolute path if found, else None.
        """
        for root, dirs, files in os.walk(self.storage_dir):
            # Skip the .cache folder from search matches
            dirs[:] = [d for d in dirs if d != ".cache"]
            for f in files:
                if target.lower() in f.lower():
                    return os.path.join(root, f)
        return None

    def _is_stock_request(self, target: str) -> bool:
        """
        Heuristic: if the target has no file extension and is 1-5 uppercase-ish chars,
        treat it as a stock ticker / company name instead of a filename.
        """
        if not target:
            return False
        _, ext = os.path.splitext(target)
        if ext.lower() in KNOWN_FILE_EXTENSIONS:
            return False
        # If it's short (likely ticker) or doesn't look like a filename
        return len(target) <= 10 or target.replace(" ", "").isalpha()

    def _resolve_ticker(self, query: str) -> Optional[str]:
        """
        Use the LLM to resolve a company name or partial query to a valid stock ticker.
        """
        prompt = (
            f"Return ONLY the stock ticker symbol for: '{query}'. "
            "If it already is a ticker (like AAPL), return it as-is. "
            "Return ONLY the ticker symbol, nothing else. No explanations."
        )
        try:
            result = self.llm.chat([{"role": "user", "content": prompt}])
            ticker = result.strip().upper().split()[0].replace(".", "")
            return ticker
        except Exception:
            return query.upper().split()[0]

    def _fetch_stock_to_cache(self, ticker: str, period: str = "1y") -> Optional[str]:
        """
        Download historical OHLCV data for `ticker` and write it to .cache/.
        Returns the path of the created CSV file, or None on failure.
        """
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period=period)
            if df.empty:
                return None
            df.reset_index(inplace=True)
            # Remove timezone info from datetime column for clean CSV
            if "Date" in df.columns:
                df["Date"] = df["Date"].dt.tz_localize(None)
            cache_path = os.path.join(self.cache_dir, f"{ticker}_history.csv")
            df.to_csv(cache_path, index=False)
            return cache_path
        except Exception:
            return None

    # ─────────────────── Main Command Handler ─────────────────────────────────

    def handle_data_command(self, cmd: str) -> Dict[str, Any]:
        """
        Handles /plot and /describe commands with dynamic data fetching.
        """
        is_plot = cmd.startswith("/plot")
        remainder = cmd.replace("/plot" if is_plot else "/describe", "").strip()
        parts = remainder.split(" ", 1)
        target_token = parts[0] if parts else ""
        user_context = parts[1] if len(parts) > 1 else "Analyze trends."

        # ── 1. Try to find an existing file in storage (recursive) ────────────
        file_path = self._find_file_recursive(target_token) if target_token else None

        # ── 2. If not found, try dynamic stock fetch ──────────────────────────
        if file_path is None and target_token and self._is_stock_request(target_token):
            ticker = self._resolve_ticker(target_token)
            file_path = self._fetch_stock_to_cache(ticker, period="1y")
            if file_path:
                display_name = f"{ticker} (live data)"
            else:
                return {
                    "type": "text",
                    "content": (
                        f"❌ Could not find a file matching **'{target_token}'** "
                        f"and failed to fetch stock data for **{target_token.upper()}**. "
                        "Please verify the ticker symbol or upload a dataset."
                    )
                }
        elif file_path is None:
            # Try fallback: use first available file in storage
            all_files = []
            for root, dirs, files in os.walk(self.storage_dir):
                dirs[:] = [d for d in dirs if d != ".cache"]
                for f in files:
                    all_files.append(os.path.join(root, f))
            if not all_files:
                return {"type": "text", "content": "❌ No datasets found in storage. Upload a file or specify a stock ticker."}
            file_path = all_files[0]
            display_name = os.path.basename(file_path)
        else:
            display_name = os.path.basename(file_path)

        # ── 3. Load the data ──────────────────────────────────────────────────
        try:
            ext = os.path.splitext(file_path)[1].lower()
            if ext == ".csv":
                df = pd.read_csv(file_path)
            elif ext in [".xls", ".xlsx"]:
                df = pd.read_excel(file_path)
            elif ext == ".json":
                df = pd.read_json(file_path)
            else:
                return {"type": "text", "content": f"⚠️ Unsupported format: {ext}"}

            # Heuristics: if header looks like data, re-read without header
            try:
                [float(str(c)) for c in df.columns[:2]]
                df = pd.read_csv(file_path, header=None)
            except Exception:
                pass

            # Sanitize column names for Vega-Lite
            df.columns = [
                str(c).strip() if not str(c).strip().isdigit() else f"Feature_{c}"
                for c in df.columns
            ]
            numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
            if not numeric_cols:
                return {"type": "text", "content": "⚠️ No numeric columns found in the dataset."}

            top_cols = numeric_cols[:5]
            stats = df[top_cols].describe().to_string()

            # ── 4. LLM Vega-Lite generation ───────────────────────────────────
            analyst_prompt = f"""
            ROLE: Senior Data Scientist.
            DATA: {display_name} | STATS: {stats}
            REQUEST/FEEDBACK: {user_context}
            
            TASK:
            1. Create a Vega-Lite spec answering the REQUEST. 
               - For Histograms: Use 'mark': 'bar', 'x': {{'bin': true, 'field': 'YOUR_COLUMN'}}, 'y': {{'aggregate': 'count'}}.
               - ALWAYS add: "selection": {{"grid": {{"type": "interval", "bind": "scales"}}}} for ZOOM/PAN.
               - DO NOT include data 'values' inside the spec. They will be injected automatically.
               - CRITICAL: You MUST use the EXACT column names provided in the STATS table above. Do not invent column names.
            2. Provide a Strategic Insight.
            3. OUTPUT ONLY A SINGLE RAW JSON OBJECT. No markdown, no conversational text.
            
            EXPECTED JSON FORMAT:
            {{
               "insight": "Your strategic insight here...",
               "vega_lite_spec": {{
                   "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                   "mark": "...",
                   "encoding": {{...}}
               }}
            }}
            """

            analyst_response = self.llm.chat([{"role": "user", "content": analyst_prompt}])

            # ── 5. Parse Vega-Lite JSON safely ────────────────────────────────
            try:
                clean_res = re.sub(r"```json\s*", "", analyst_response)
                clean_res = re.sub(r"```\s*", "", clean_res)
                start_idx = clean_res.find("{")
                end_idx = clean_res.rfind("}") + 1
                res_j = json.loads(clean_res[start_idx:end_idx])
                spec = res_j.get("vega_lite_spec", {})
                if "selection" not in spec:
                    spec["selection"] = {"grid": {"type": "interval", "bind": "scales"}}
                insight = res_j.get("insight", analyst_response)
            except Exception:
                spec = {
                    "mark": "line",
                    "encoding": {
                        "x": {"field": top_cols[0], "type": "quantitative"},
                        "y": {"field": top_cols[0], "type": "quantitative"},
                    },
                }
                insight = f"*(Error parsing structured response)*\n\n{analyst_response}"

            # ── 6. Return formatted result ────────────────────────────────────
            if is_plot:
                return {
                    "type": "mixed",
                    "items": [
                        {"type": "text", "content": f"## 🔬 Intelligence Report: `{display_name}`\n{insight}"},
                        {"type": "vega_lite", "data": df[top_cols].to_dict(orient="records"), "spec": spec},
                    ],
                }
            else:
                return {
                    "type": "text",
                    "content": (
                        f"## 📊 Data Summary: `{display_name}`\n{insight}\n\n"
                        + df[top_cols].describe().to_markdown()
                    ),
                }

        except Exception as e:
            return {"type": "text", "content": f"**Data Analyst Error:** {str(e)}"}

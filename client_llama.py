"""
MCP Client - Entry Point (SOLID Architecture)
This file is a thin orchestrator. All logic lives in core/ modules.
"""
import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Core components (Dependency Inversion: depend on abstractions)
from core.planner import LLMPlanner
from core.validator import LLMPlanValidator
from core.executor import ToolExecutor
from core.summarizer import LLMSummarizer

# Unified LLM Client (local or Gemini fallback)
from utils.llm_client import LLMClient


async def run_bridge():
    """Main loop: connects to MCP server and orchestrates plan-execute-summarize."""
    
    # Initialize LLM client (auto-detects local vs cloud)
    llm = LLMClient()
    print(f"[SYSTEM] LLM Mode: {llm.mode.upper()}")
    
    # Initialize components (Dependency Injection)
    planner = LLMPlanner(llm)
    validator = LLMPlanValidator(llm)
    executor = ToolExecutor()
    summarizer = LLMSummarizer(llm)
    
    # MCP Server connection
    server_params = StdioServerParameters(
        command="python",
        args=["main.py"],
        env=None
    )
    
    print(f"[SYSTEM] Connecting to MCP Server...")
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Load tools
            tools = await session.list_tools()
            tool_descriptions = "\n".join(
                f"- {t.name}: {t.description}" for t in tools.tools
            )
            print(f"[SYSTEM] Tools loaded: {len(tools.tools)}")
            
            # Main loop
            while True:
                try:
                    user_input = input("\n👤 You: ").strip()
                    
                    if not user_input:
                        continue
                    if user_input.lower() in ("exit", "quit", "bye"):
                        print("[SYSTEM] Bye!")
                        break
                    
                    # ========== PHASE 1: PLANNING ==========
                    print("\n[PLANNER] Creating execution plan...")
                    raw_plan = await planner.plan(user_input, tool_descriptions)
                    print(f"[DEBUG] Raw plan: {raw_plan[:200]}...")
                    
                    # ========== PHASE 3: VALIDATION ==========
                    plan = await validator.validate(raw_plan)
                    
                    if not plan:
                        # No valid plan = direct response from raw_plan
                        print(f"\n🤖 Assistant: {raw_plan}")
                        continue
                    
                    print(f"\n[PLAN] {len(plan)} steps:")
                    for step in plan:
                        print(f"  {step.get('step', '?')}. {step.get('tool', 'chat')} - {step.get('description', '')[:50]}")
                    
                    # ========== PHASE 3: EXECUTION ==========
                    print("\n[EXECUTOR] Executing plan...")
                    results = await executor.execute(plan, session)
                    
                    # ========== PHASE 4: SUMMARIZATION ==========
                    print("\n[SUMMARIZER] Generating final response...")
                    response = await summarizer.summarize(user_input, results)
                    print(f"\n🤖 Assistant: {response}")
                
                except KeyboardInterrupt:
                    print("\n[SYSTEM] Bye!")
                    break
                except Exception as e:
                    print(f"[ERROR] {e}")


if __name__ == "__main__":
    try:
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(run_bridge())
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass
    except Exception as e:
        if "Connection closed" not in str(e):
            print(f"Fatal error: {e}")
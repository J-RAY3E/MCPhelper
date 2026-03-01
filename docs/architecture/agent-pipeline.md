# Agent Pipeline

The agent pipeline is the core AI orchestration system that processes user queries through multiple stages.

## Pipeline Stages

```
User Query
    │
    ▼
┌─────────────────┐
│     Planner     │  ← Decompose into steps
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Validator    │  ← Validate plan safety
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Executor     │  ← Execute tools
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Summarizer    │  ← Generate response
└─────────────────┘
         │
         ▼
    Final Output
```

## Stage Details

### 1. Planner

The planner uses an LLM to decompose user queries into executable steps.

**Input:** Natural language query
**Output:** Structured plan with steps

Example:
```
User: "Find the P/E ratio of AAPL and compare with MSFT"
Plan:
1. Get stock info for AAPL
2. Extract P/E ratio
3. Get stock info for MSFT
4. Extract P/E ratio
5. Compare and summarize
```

### 2. Validator

The validator reviews the plan for:
- Safety (no harmful operations)
- Feasibility (tools exist)
- Completeness (all required steps)

**Input:** Proposed plan
**Output:** Validated plan or rejection with reason

### 3. Executor

The executor runs each step:
- Invokes appropriate tools
- Handles errors and retries
- Collects results

**Input:** Validated plan
**Output:** List of tool results

### 4. Summarizer

The summarizer generates the final response:
- Formats tool results
- Adds context and explanations
- Returns natural language output

**Input:** Tool results
**Output:** Final response

## Data Analysis Pipeline

For data commands, a separate pipeline is used:

```
/plot, /describe
    │
    ▼
┌─────────────────┐
│  DataAnalyst    │  ← Pandas operations
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Vega-Lite     │  ← Chart generation
└─────────────────┘
         │
         ▼
    Interactive Chart
```

## Implementation

See:
- `backend/core/agent_orchestrator.py`
- `backend/core/planner.py`
- `backend/core/validator.py`
- `backend/core/executor.py`
- `backend/core/summarizer.py`
- `backend/core/data_analyst.py`

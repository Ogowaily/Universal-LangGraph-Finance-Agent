# 🤖 Universal LangGraph Finance Agent

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Latest-green.svg)](https://github.com/langchain-ai/langgraph)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> A production-ready, config-driven agentic AI framework built with LangGraph that demonstrates scalable multi-domain assistant architecture through intelligent intent routing and modular executor design.
## ⚠️ Known Issues

- Some transactions may not be recorded due to edge cases.
- Monthly summaries may occasionally miss recent entries.
- Core functionality (intent routing, executors, budget & debt planning) is working.
- Future improvements can fix the issues above and add full coverage for all intents.

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [How It Works](#-how-it-works)
- [Project Structure](#-project-structure)
- [Extending the Framework](#-extending-the-framework)
- [Logging & Tracing](#-logging--tracing)
- [Deployment](#-deployment)
- [Contributing](#-contributing)
- [License](#-license)

---
<img width="1027" height="474" alt="Screenshot 2026-02-16 211841" src="https://github.com/user-attachments/assets/d6483a0c-5996-4d0d-9b90-bb217f4a54d0" />

## 🎯 Overview

### The Problem

Building production-grade AI agents often leads to monolithic codebases where adding new capabilities requires extensive code changes. Traditional chatbot architectures struggle with:
- Hard-coded business logic scattered across multiple files
- Tight coupling between conversation flow and domain logic
- Difficulty scaling to multiple domains or use cases
- Complex state management and memory handling

### The Solution

**Universal LangGraph Finance Agent** is a **config-driven agentic framework** that separates concerns through:
- **Dynamic Intent Routing**: User requests are automatically classified and routed to specialized executors
- **Modular Executor Pattern**: Each capability (budgeting, debt planning, transactions) is an independent, testable module
- **Universal Configuration**: New domains can be added by updating YAML configs without touching core code
- **Persistent Memory**: Automatic extraction and storage of structured data using Pydantic schemas

This architecture enables developers to build scalable, maintainable AI assistants that can grow from a single-domain demo to a multi-tenant production system.

---

## ✨ Key Features

### 🏦 Finance Domain Capabilities

- **💰 Transaction Tracking**: Log income and expenses with automatic categorization
- **📊 Budget Planning**: Create and monitor spending limits across categories
- **🎯 Financial Goals**: Set and track savings goals with progress monitoring
- **💳 Debt Payoff Planning**: Generate month-by-month payment schedules with interest calculations
- **🔄 Recurring Payments**: Manage subscriptions and repeating expenses
- **📈 Financial Summaries**: Get comprehensive spending reports and insights
- **🧠 AI Financial Advice**: Receive personalized recommendations based on spending patterns

### 🔧 Framework Features

- **🎯 Intent-Based Routing**: Automatic classification of user requests to appropriate executors
- **📦 Modular Executor Pattern**: Each capability is an isolated, reusable node
- **🔄 Universal Config Schema**: Domain-agnostic configuration system
- **💾 Automatic Memory Management**: Trustcall-powered structured data extraction
- **🧪 Type-Safe Schemas**: Pydantic models ensure data consistency
- **🔍 LangSmith Integration**: Optional tracing for debugging and monitoring
- **🚀 LangGraph Studio Ready**: Compatible with LangGraph Dev Server

---

## 🏗️ Architecture

### High-Level Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          USER INPUT                                     │
│                     "I have $20,000 debt at 2.5%                       │
│                   monthly interest. Create a payoff plan"               │
└──────────────────────────┬──────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      MAIN ASSISTANT NODE                                │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  1. Load Configuration (assistant_type, enabled_memory_types)   │  │
│  │  2. Retrieve Memories from Store (profile, transactions, etc.)  │  │
│  │  3. Format System Prompt with Role + Memories                   │  │
│  │  4. Call LLM with RouteIntent Tool Binding                      │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  Output: AI Message with RouteIntent Tool Call                         │
│          { intent: "debt_payoff_plan", reasoning: "..." }              │
└──────────────────────────┬──────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         ROUTER NODE                                     │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  1. Extract RouteIntent tool call from last AI message          │  │
│  │  2. Read intent field ("debt_payoff_plan")                      │  │
│  │  3. Query Intent Registry for executor mapping                  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  Conditional Edge Decision:                                            │
│  └──> "finance_debt_payoff_executor"                                   │
└──────────────────────────┬──────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                  FINANCE DEBT PAYOFF EXECUTOR                           │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  1. Load FinanceDebtPlan schema                                 │  │
│  │  2. Bind schema as LLM tool for structured extraction           │  │
│  │  3. Extract parameters: debt, interest, salary, expenses        │  │
│  │  4. Run deterministic Python calculation:                       │  │
│  │     - Month-by-month payment schedule                           │  │
│  │     - Interest compounding (rounded to 2 decimals)              │  │
│  │     - Remaining balance tracking                                │  │
│  │  5. Return JSON with MonthlyPaymentRow[] + summary              │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  Output: ToolMessage with complete payment schedule JSON              │
└──────────────────────────┬──────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      MEMORY UPDATE NODE                                 │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  1. Identify memory types to update based on intent             │  │
│  │  2. Use Trustcall to extract structured data from conversation  │  │
│  │  3. Save to LangGraph Store with namespacing:                   │  │
│  │     namespace = (memory_type, assistant_type, user_id)          │  │
│  │  4. Update: finance_debt_plans, profile (if mentioned)          │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  Store Namespaces Updated:                                             │
│  - ("finance_debt_plans", "finance", "user_123")                       │
│  - ("profile", "finance", "user_123") [if applicable]                  │
└──────────────────────────┬──────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   MAIN ASSISTANT NODE (2nd Pass)                        │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  1. NO RouteIntent tool binding (route_count_this_turn > 0)     │  │
│  │  2. Special system prompt: "FORMATTING ONLY - NO CALCULATIONS"  │  │
│  │  3. Parse JSON from executor tool message                       │  │
│  │  4. Format results into user-friendly markdown table            │  │
│  │  5. Add explanatory text and recommendations                    │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  Output: Final AI message with formatted response                      │
└──────────────────────────┬──────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          END STATE                                      │
│                                                                         │
│  Conversation complete. State includes:                                │
│  - Full message history (HumanMessage, AIMessage, ToolMessage)         │
│  - Updated memories in Store                                           │
│  - Thread ID for conversation resumption                               │
└─────────────────────────────────────────────────────────────────────────┘
```

### Core Components

#### 1. **Configuration Layer** (`configuration.py`)
```python
@dataclass
class Configuration:
    user_id: str
    assistant_type: Literal["finance", "todo"]
    role_prompt: str
    enabled_memory_types: list[str]
    router_intents: list[str]
```
- Defines universal schema for assistant behavior
- Pre-configured templates for finance and todo domains
- Extensible to new domains without code changes

#### 2. **Graph Structure** (`graph.py`)
```
START 
  ↓
main_assistant [conditional: should_continue]
  ↓ (has RouteIntent tool call)
router [conditional: route_to_executor]
  ↓ (intent-based routing)
executor_* (finance_debt_payoff, finance_budget, etc.)
  ↓
memory_update
  ↓
main_assistant (final response, no tool binding)
  ↓
END
```

#### 3. **Intent Registry** (`utils/intent_registry.py`)
Maps intents to executor nodes:
```python
{
    "finance": {
        "debt_payoff_plan": "finance_debt_payoff_executor",
        "add_transaction": "finance_add_transaction_executor",
        "set_budget": "finance_budget_executor",
        ...
    }
}
```

#### 4. **Memory System**
- **LangGraph Store**: Namespaced key-value store `(memory_type, assistant_type, user_id)`
- **Trustcall**: Automatic extraction of structured data from conversation
- **Pydantic Schemas**: Type-safe memory models in `schemas/`
- **Schema Registry**: Dynamic schema loading based on memory type

---

## 🛠️ Tech Stack

| Category | Technology | Purpose |
|----------|-----------|---------|
| **Framework** | [LangGraph](https://github.com/langchain-ai/langgraph) | State graph orchestration |
| **LLM Provider** | [Groq API](https://groq.com) | Fast inference with Llama models |
| **Schema Validation** | [Pydantic V2](https://docs.pydantic.dev/latest/) | Type-safe data models |
| **Memory Extraction** | [Trustcall](https://github.com/parlance-labs/trustcall) | Structured data extraction from conversations |
| **Tracing** | [LangSmith](https://smith.langchain.com) | Optional debugging and monitoring |
| **Language** | Python 3.11+ | Modern Python with type hints |

---

## 📥 Installation

### Prerequisites

- Python 3.11 or higher
- Groq API key ([Get one here](https://console.groq.com))
- (Optional) LangSmith API key for tracing

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/universal-finance-agent.git
cd universal-finance-agent
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your API keys:

```env
# Required: Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here

# Optional: LangSmith Tracing (for debugging)
LANGSMITH_TRACING_V2=true
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_PROJECT=universal-langgraph
LANGSMITH_WORKSPACE_ID=your_workspace_id_here
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `GROQ_API_KEY` | ✅ Yes | API key for Groq LLM provider | - |
| `LANGSMITH_TRACING_V2` | ❌ No | Enable LangSmith tracing | `false` |
| `LANGSMITH_API_KEY` | ❌ No | LangSmith API key | - |
| `LANGSMITH_PROJECT` | ❌ No | LangSmith project name | - |
| `LANGSMITH_WORKSPACE_ID` | ❌ No | LangSmith workspace ID | - |

### Assistant Configuration

The framework supports multiple assistant types via `configuration.py`. Currently implemented:

#### Finance Assistant
```python
config = get_finance_config(user_id="user_123")
```
- **Enabled Memory Types**: profile, transactions, budgets, goals, recurring payments, debt plans
- **Available Intents**: add_transaction, set_budget, create_goal, debt_payoff_plan, advice, monthly_summary
- **Role**: Personal Finance Assistant with budgeting and planning capabilities

#### Todo Assistant (Example)
```python
config = get_todo_config(user_id="user_123")
```
- **Enabled Memory Types**: profile, tasks, task instructions
- **Available Intents**: add_task, update_task, task_summary
- **Role**: Task Management Assistant

---

## 🚀 Usage

### Running the Application

#### Option 1: Interactive Finance Session
```bash
python app.py
# Select option 2
```

#### Option 2: Run Demo (Automated Conversation)
```bash
python app.py
# Select option 1
```

#### Option 3: Direct Python Import
```python
from langchain_core.messages import HumanMessage
from configuration import get_finance_config
from graph import create_graph

# Create graph
graph = create_graph(with_persistence=True)

# Configure for finance assistant
config = get_finance_config(user_id="user_123")
config["configurable"]["thread_id"] = "my_conversation"

# Send message
result = graph.invoke(
    {"messages": [HumanMessage(content="I spent $50 on groceries")]},
    config=config
)

# Get response
print(result["messages"][-1].content)
```

### Example Prompts & Expected Outputs

#### Example 1: Debt Payoff Plan

**User Input:**
```
I have 20,000 EGP credit card debt at 2.5% monthly interest. 
My salary is 12,000 EGP and fixed expenses are 7,500 EGP. 
I want to save 10%. Create an 8-month payoff plan.
```

**System Flow:**
1. main_assistant → RouteIntent(intent="debt_payoff_plan")
2. router → finance_debt_payoff_executor
3. Executor runs Python calculation with compounding interest
4. Returns JSON with month-by-month schedule
5. memory_update → Saves plan to store
6. main_assistant → Formats as markdown table

**Expected Output:**
```markdown
Here's your 8-month debt payoff plan:

| Month | Salary | Fixed Expenses | Savings | Debt Payment | Interest | Remaining Balance |
|-------|--------|----------------|---------|--------------|----------|-------------------|
| 1     | 12,000 | 7,500          | 1,200   | 3,300        | 500.00   | 17,200.00        |
| 2     | 12,000 | 7,500          | 1,200   | 3,300        | 430.00   | 14,330.00        |
| 3     | 12,000 | 7,500          | 1,200   | 3,300        | 358.25   | 11,388.25        |
| ...   | ...    | ...            | ...     | ...          | ...      | ...              |

✅ Debt cleared in 7 months!
💰 Total interest paid: 1,850.00 EGP
💵 Total saved: 8,400 EGP
```

#### Example 2: Budget Planning

**User Input:**
```
My salary is 12,000 EGP. My rent is 3,000 and monthly expenses 
are around 6,000. Create a monthly budget.
```

**Expected Output:**
```markdown
I've created a monthly budget for you:

📊 Income: 12,000 EGP

💸 Fixed Expenses:
- Rent: 3,000 EGP
- Other expenses: 6,000 EGP
Total: 9,000 EGP

💰 Remaining: 3,000 EGP

Recommendations:
- Save 20%: 2,400 EGP/month
- Emergency fund: 600 EGP/month
- Discretionary: Keep under 1,000 EGP
```

#### Example 3: Add Transaction

**User Input:**
```
Add a transaction: I spent 250 EGP on food today.
```

**Expected Output:**
```markdown
✅ Transaction recorded!

Amount: 250 EGP
Category: Food
Date: 2026-02-16

Your food spending this month: 1,450 EGP (58% of budget)
```

---

## 🔍 How It Works

### 1. Intent-Based Routing System

The framework uses a two-pass architecture:

**First Pass (Routing):**
```python
# main_assistant binds RouteIntent tool
model = LLM_chat.bind_tools([RouteIntent], parallel_tool_calls=False)

# LLM classifies intent
response = model.invoke([SystemMessage(...)] + state["messages"])
# Returns: AIMessage with tool_calls=[{name: "RouteIntent", args: {intent: "debt_payoff_plan"}}]
```

**Second Pass (Response):**
```python
# After executor completes, main_assistant called again WITHOUT tools
model = SafeLLM(temperature=0)  # No tool binding
response = model.invoke([SystemMessage("FORMATTING ONLY...")] + messages)
# Returns: AIMessage with formatted natural language response
```

### 2. Configuration-Driven Architecture

Adding a new domain requires zero code changes to core nodes:

```python
def get_legal_config(user_id: str = "default_user") -> dict:
    return {
        "configurable": {
            "assistant_type": "legal",
            "role_prompt": "You are a Legal Assistant...",
            "enabled_memory_types": ["profile", "legal_cases", "legal_documents"],
            "router_intents": ["file_case", "search_precedent", "draft_contract"]
        }
    }
```

Then add executor nodes:
```python
builder.add_node("legal_file_case_executor", legal_file_case_executor)
```

And update intent registry:
```python
INTENT_EXECUTOR_MAP["legal"] = {
    "file_case": "legal_file_case_executor",
    ...
}
```

### 3. Memory System with Trustcall

**Automatic Schema-Based Extraction:**
```python
# memory_update.py
extractor = create_extractor(
    LLM_chat,
    tools=[FinanceDebtPlan],  # Pydantic schema
    tool_choice="FinanceDebtPlan",
    enable_inserts=True
)

result = extractor.invoke({
    "messages": conversation_history,
    "existing": existing_memories
})

# Save to store with namespace
store.put(
    namespace=("finance_debt_plans", "finance", "user_123"),
    key=uuid4(),
    value=result["responses"][0].model_dump()
)
```

**Memory Retrieval:**
```python
# main_assistant.py
memories = get_all_memories_by_type(
    store, 
    memory_type="finance_transactions",
    assistant_type="finance",
    user_id="user_123"
)
```

### 4. Deterministic Calculations

All financial calculations are done in **Python**, not by the LLM:

```python
# finance_debt_payoff.py
for month in range(1, months + 1):
    interest = round(balance * monthly_interest_rate, 2)
    balance = round(balance + interest, 2)
    
    payment = min(available, balance)
    balance = round(balance - payment, 2)
    
    rows.append(MonthlyPaymentRow(
        month=month,
        debt_payment=payment,
        interest_charged=interest,
        remaining_balance=balance
    ))
```

The LLM's role is **formatting only**:
```python
system_prompt = """
⚠️ NEVER RECALCULATE ANY NUMBERS
⚠️ ONLY FORMAT AND EXPLAIN
The calculations are done by Python and are 100% accurate.
"""
```

---

## 📁 Project Structure

```
Universal-Finance-Agent/
├── app.py                          # Main entry point (CLI interface)
├── Agent.py                        # Graph export for LangGraph Studio
├── graph.py                        # LangGraph state graph definition
├── configuration.py                # Universal configuration schema
├── safe_llm.py                     # LLM wrapper (Groq integration)
├── requirements.txt                # Python dependencies
├── Langgraph.json                  # LangGraph Studio config
├── .env                            # Environment variables (not in repo)
├── .env.example                    # Example environment file
│
├── prompts/                        # System prompt templates
│   ├── universal_system_prompt.txt # Main assistant system prompt
│   ├── router_prompt.txt           # Router classification prompt
│   ├── confirmation_prompt.txt     # Confirmation message template
│   └── finance_role_prompt.txt     # Finance domain role description
│
├── nodes/                          # LangGraph nodes
│   ├── __init__.py
│   ├── main_assistant.py           # Primary conversational interface
│   ├── router.py                   # Intent classification & routing
│   ├── memory_update.py            # Trustcall-powered memory extraction
│   │
│   └── executors/                  # Domain-specific executor nodes
│       ├── __init__.py
│       ├── finance_advice.py       # AI financial recommendations
│       ├── finance_budget.py       # Budget creation & tracking
│       ├── finance_goal.py         # Savings goal planning
│       ├── finance_add_transaction.py  # Transaction logging
│       ├── finance_summary.py      # Spending report generation
│       ├── finance_recurring.py    # Recurring payment management
│       └── finance_debt_payoff.py  # Debt payoff schedule calculator
│
├── schemas/                        # Pydantic data models
│   ├── __init__.py
│   ├── profile.py                  # Universal user profile schema
│   ├── finance_budget.py           # Budget limit schema
│   ├── finance_debt_plan.py        # Debt payoff plan schema
│   ├── finance_goal.py             # Financial goal schema
│   ├── finance_recurring.py        # Recurring payment schema
│   └── finance_transaction.py      # Transaction record schema
│
└── utils/                          # Utility modules
    ├── __init__.py
    ├── intent_registry.py          # Intent → Executor mapping
    ├── schema_registry.py          # Memory type → Schema mapping
    ├── schema_flattener.py         # Schema field extraction utilities
    ├── store_utils.py              # LangGraph Store helper functions
    ├── formatting.py               # Memory formatting for prompts
    └── debt_plan_formatter.py      # Debt plan table formatting
```

---

## 🔧 Extending the Framework

### Adding a New Executor

**1. Create Executor File** (`nodes/executors/finance_investment.py`):
```python
from langchain_core.runnables import RunnableConfig
from langgraph.graph import MessagesState
from langgraph.store.base import BaseStore
from schemas.finance_investment import FinanceInvestment
from safe_llm import LLM_chat

def finance_investment_executor(
    state: MessagesState, 
    config: RunnableConfig, 
    store: BaseStore
):
    """Execute investment portfolio analysis."""
    
    # Bind schema as tool
    model = LLM_chat.bind_tools([FinanceInvestment])
    
    # Extract structured data
    response = model.invoke(state["messages"])
    
    # Process and return result
    return {"messages": [response]}
```

**2. Create Schema** (`schemas/finance_investment.py`):
```python
from pydantic import BaseModel, Field

class FinanceInvestment(BaseModel):
    portfolio_name: str
    initial_amount: float = Field(gt=0)
    expected_return: float = Field(ge=0, le=1)
    time_horizon_years: int = Field(gt=0)
```

**3. Register in Graph** (`graph.py`):
```python
from nodes.executors.finance_investment import finance_investment_executor

builder.add_node("finance_investment_executor", finance_investment_executor)
builder.add_edge("finance_investment_executor", "memory_update")

builder.add_conditional_edges("router", route_to_executor, {
    # ... existing routes
    "finance_investment_executor": "finance_investment_executor"
})
```

**4. Update Intent Registry** (`utils/intent_registry.py`):
```python
INTENT_EXECUTOR_MAP = {
    "finance": {
        # ... existing intents
        "analyze_investment": "finance_investment_executor"
    }
}
```

**5. Update Configuration** (`configuration.py`):
```python
def get_finance_config(user_id: str = "default_user") -> dict:
    return {
        "configurable": {
            # ... existing config
            "enabled_memory_types": [
                # ... existing types
                "finance_investments"
            ],
            "router_intents": [
                # ... existing intents
                "analyze_investment"
            ]
        }
    }
```

**That's it!** No changes to core nodes (main_assistant, router, memory_update).

---

## 📊 Logging & Tracing

### LangSmith Integration

Enable detailed execution tracing for debugging:

**1. Set Environment Variables:**
```bash
LANGSMITH_TRACING_V2=true
LANGSMITH_API_KEY=your_api_key
LANGSMITH_PROJECT=universal-finance-agent
```

**2. View Traces:**
Visit [LangSmith Dashboard](https://smith.langchain.com) to see:
- Full conversation flow
- LLM calls with prompts and responses
- Tool invocations
- Execution timing
- Error stack traces

### Console Logging

The framework includes debug prints in key locations:

```python
# memory_update.py
print(f"✅ Successfully extracted {schema_name} via direct method")
print(f"⚠️ Trustcall error for {memory_type}, using fallback")

# router.py
print(f"🔀 Routing to executor: {executor_name}")
```

---

## 🚢 Deployment

### LangGraph Studio (Recommended)

**1. Install LangGraph CLI:**
```bash
pip install langgraph-cli
```

**2. Start Dev Server:**
```bash
langgraph dev
```

**3. Access UI:**
Open browser to `http://localhost:8123`

The `Agent.py` file exports the compiled graph:
```python
from graph import graph
__all__ = ["graph"]
```

### Docker Deployment (Future)

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["python", "app.py"]
```

Build and run:
```bash
docker build -t finance-agent .
docker run -p 8000:8000 --env-file .env finance-agent
```

### Cloud Deployment

**LangGraph Cloud (Coming Soon):**
```bash
langgraph deploy
```

**Alternative: Deploy as FastAPI Service:**
```python
from fastapi import FastAPI
from graph import create_graph

app = FastAPI()
graph = create_graph(with_persistence=True)

@app.post("/chat")
async def chat(message: str, user_id: str):
    result = graph.invoke(...)
    return result
```

---

## 🤝 Contributing

Contributions are welcome! This framework is designed to be extended by the community.

### Development Setup

```bash
# Clone and setup
git clone https://github.com/yourusername/universal-finance-agent.git
cd universal-finance-agent
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run tests (when added)
pytest tests/
```

### Contribution Guidelines

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/new-executor`)
3. **Add** your executor/schema following the patterns in `nodes/executors/`
4. **Test** your changes thoroughly
5. **Document** new features in README
6. **Submit** a Pull Request with clear description

### Ideas for Contribution

- [ ] Add new finance executors (investment analysis, tax planning)
- [ ] Implement todo domain executors
- [ ] Create legal assistant domain
- [ ] Add unit tests for executors
- [ ] Improve error handling
- [ ] Add persistent database (SQLite/Postgres)
- [ ] Create vector store integration for semantic search
- [ ] Build REST API wrapper
- [ ] Add authentication/multi-tenancy

---

## 📄 License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2026 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🙏 Acknowledgments

- **LangChain Team** for LangGraph framework
- **Groq** for ultra-fast LLM inference
- **Anthropic** for Trustcall library
- **Pydantic** for elegant data validation

---

## 📞 Contact & Support

 
- **LinkedIn**: [Connect with me](https://www.linkedin.com/in/omar-gowaily-787536298/)
 

---

<div align="center">

**⭐ Star this repo if you find it useful!**

Built with ❤️ using LangGraph | Made for AI Engineers

</div>

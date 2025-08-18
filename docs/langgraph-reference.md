# LangGraph Documentation

This documentation is provided to help understand LangGraph 0.6.x patterns and suggest better code completions. It covers the essential concepts, patterns, and examples for building stateful AI agents with LangGraph.

## Overview

LangGraph is a Python library for building stateful, multi-actor applications with Large Language Models (LLMs). It provides a graph-based framework for orchestrating complex agent workflows with built-in state management, human-in-the-loop capabilities, and robust error handling.

**Key Features:**

- **Stateful execution**: Persistent state across graph operations
- **Cyclical workflows**: Support for conditional loops and branching logic
- **Human-in-the-loop**: Built-in interruption and approval mechanisms
- **Tool integration**: Seamless integration with LangChain tools
- **Streaming support**: Real-time output streaming and intermediate step visibility
- **Checkpointing**: Automatic state persistence and recovery

## Core Concepts

### 1. State Management

State in LangGraph is the shared data structure that flows through your graph. It's typically defined using `TypedDict` with optional reducer functions for handling state updates.

```python
from typing_extensions import TypedDict, Annotated
from langgraph.graph.message import add_messages

# Basic state definition
class BasicState(TypedDict):
    count: int
    user_input: str
    bot_response: str

# State with message handling
class MessageState(TypedDict):
    messages: Annotated[list, add_messages]  # Built-in message reducer

# State with custom reducer
import operator
class CounterState(TypedDict):
    values: Annotated[list[int], operator.add]  # Appends new values to list
```

### 2. Graph Architecture

```python
from langgraph.graph import StateGraph, START, END

# Create a state graph
graph = StateGraph(State)

# Add nodes (functions that process state)
graph.add_node("node_name", node_function)

# Add edges (define flow between nodes)
graph.add_edge(START, "node_name")  # Entry point
graph.add_edge("node_name", END)    # Exit point

# Add conditional edges (dynamic routing)
graph.add_conditional_edges(
    "source_node",
    routing_function,      # Function that determines next node
    {
        "continue": "next_node",
        "end": END
    }
)

# Compile the graph
app = graph.compile()
```

### 3. Node Functions

Node functions are the core processing units that take state as input and return state updates:

```python
def my_node(state: State) -> dict:
    """
    Node functions should:
    1. Take state as first parameter
    2. Return a dictionary with state updates
    3. Not mutate the input state directly
    """
    # Process current state
    current_value = state["count"]

    # Return state updates
    return {
        "count": current_value + 1,
        "bot_response": f"Count is now {current_value + 1}"
    }

# Async node functions are also supported
async def async_node(state: State) -> dict:
    # Async processing
    result = await some_async_operation()
    return {"result": result}
```

### 4. Tool Integration

```python
from langchain_core.tools import tool
from langgraph.prebuilt import ToolExecutor, ToolInvocation

@tool
def search_tool(query: str) -> str:
    """Search for information"""
    return f"Search results for: {query}"

# Create tool executor
tools = [search_tool]
tool_executor = ToolExecutor(tools)

def tool_calling_node(state: State):
    # Extract tool calls from messages
    last_message = state["messages"][-1]

    # Execute tools
    tool_invocations = []
    for tool_call in last_message.tool_calls:
        action = ToolInvocation(
            tool=tool_call["name"],
            tool_input=tool_call["args"]
        )
        tool_invocations.append(action)

    # Execute and return results
    responses = tool_executor.batch(tool_invocations)
    return {"messages": responses}
```

## Common Patterns

### 1. Simple Chain Pattern

```python
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    input: str
    output: str

def process_input(state: State) -> dict:
    return {"output": f"Processed: {state['input']}"}

# Build graph
workflow = StateGraph(State)
workflow.add_node("process", process_input)
workflow.add_edge(START, "process")
workflow.add_edge("process", END)

app = workflow.compile()

# Usage
result = app.invoke({"input": "Hello"})
# {'input': 'Hello', 'output': 'Processed: Hello'}
```

### 2. Conditional Routing Pattern

```python
def should_continue(state: State) -> str:
    """Routing function that determines next step"""
    if state["count"] < 3:
        return "continue"
    else:
        return "end"

# Add conditional edge
workflow.add_conditional_edges(
    "counter_node",
    should_continue,
    {
        "continue": "counter_node",  # Loop back
        "end": END
    }
)
```

### 3. Agent with Tools Pattern

```python
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

# Initialize LLM
llm = ChatOpenAI(model="gpt-4")

def agent_node(state: AgentState):
    """Main agent reasoning node"""
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

def tool_node(state: AgentState):
    """Execute tools based on last message"""
    last_message = state["messages"][-1]

    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        # Execute tools
        tool_responses = []
        for tool_call in last_message.tool_calls:
            # Tool execution logic here
            result = execute_tool(tool_call)
            tool_responses.append(result)
        return {"messages": tool_responses}

    return {"messages": []}

def should_continue(state: AgentState) -> str:
    """Determine if agent should continue or end"""
    last_message = state["messages"][-1]

    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    else:
        return "end"

# Build agent graph
workflow = StateGraph(AgentState)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "agent")
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        "end": END
    }
)
workflow.add_edge("tools", "agent")

agent = workflow.compile()
```

### 4. Multi-Agent Collaboration Pattern

```python
class MultiAgentState(TypedDict):
    messages: Annotated[list, add_messages]
    next_agent: str
    task_complete: bool

def researcher_agent(state: MultiAgentState):
    """Agent specialized in research"""
    # Research logic
    return {
        "messages": [AIMessage(content="Research completed")],
        "next_agent": "writer"
    }

def writer_agent(state: MultiAgentState):
    """Agent specialized in writing"""
    # Writing logic
    return {
        "messages": [AIMessage(content="Draft written")],
        "task_complete": True
    }

def route_to_agent(state: MultiAgentState) -> str:
    """Route to next agent or end"""
    if state.get("task_complete"):
        return "end"
    return state.get("next_agent", "researcher")

# Multi-agent workflow
workflow = StateGraph(MultiAgentState)
workflow.add_node("researcher", researcher_agent)
workflow.add_node("writer", writer_agent)

workflow.add_edge(START, "researcher")
workflow.add_conditional_edges(
    "researcher",
    route_to_agent,
    {
        "writer": "writer",
        "end": END
    }
)
workflow.add_conditional_edges(
    "writer",
    route_to_agent,
    {
        "researcher": "researcher",
        "end": END
    }
)
```

## Advanced Features

### 1. Streaming and Real-time Output

```python
# Stream graph execution
for chunk in app.stream({"input": "Hello"}, stream_mode="updates"):
    print(chunk)

# Stream with different modes
for chunk in app.stream(input_data, stream_mode="values"):
    print("Current state:", chunk)

# Async streaming
async for chunk in app.astream(input_data, stream_mode="updates"):
    print("Update:", chunk)
```

### 2. Checkpointing and Persistence

```python
from langgraph.checkpoint.memory import InMemorySaver

# Add checkpointing
checkpointer = InMemorySaver()
app = workflow.compile(checkpointer=checkpointer)

# Run with thread_id for persistence
config = {"configurable": {"thread_id": "conversation-1"}}
result = app.invoke(input_data, config=config)

# Continue from checkpoint
continued_result = app.invoke(more_input, config=config)
```

### 3. Human-in-the-Loop

```python
# Add interruptions before/after nodes
app = workflow.compile(
    checkpointer=checkpointer,
    interrupt_before=["human_review"],
    interrupt_after=["critical_decision"]
)

# Get current state when interrupted
state = app.get_state(config)
print("Current state:", state.values)

# Update state and continue
app.update_state(config, {"approved": True})
result = app.invoke(None, config=config)  # Continue from checkpoint
```

### 4. Error Handling and Retries

```python
from langgraph.types import RetryPolicy

def fallible_node(state: State):
    if random.random() < 0.5:
        raise Exception("Random failure")
    return {"result": "success"}

# Add retry policy
workflow.add_node(
    "risky_operation",
    fallible_node,
    retry_policy=RetryPolicy(
        max_attempts=3,
        delay=1.0,
        backoff_factor=2.0
    )
)
```

### 5. Context API and Runtime Configuration (v0.6+)

```python
from langgraph.runtime import Runtime
from typing_extensions import TypedDict

# Define context schema (NEW in v0.6)
class Context(TypedDict):
    user_id: str
    api_key: str
    db_connection: str

# Define state with context support
class State(TypedDict):
    messages: list
    count: int

# Create graph with context schema
workflow = StateGraph(State, context_schema=Context)

def context_aware_node(state: State, runtime: Runtime[Context]) -> dict:
    """Node that accesses runtime context"""
    user_id = runtime.context.user_id
    api_key = runtime.context.api_key

    # Access other runtime utilities
    store = runtime.store  # For persistent data

    return {
        "count": state["count"] + 1,
        "processed_by": user_id
    }

workflow.add_node("process", context_aware_node)
app = workflow.compile()

# Usage - pass context at runtime
result = app.invoke(
    {"messages": [], "count": 0},
    context={
        "user_id": "123",
        "api_key": "secret",
        "db_connection": "conn_string"
    }
)
```

### 6. Durability Control (v0.6+)

```python
# Durability options (replaces checkpoint_during):
# - "async": Persist after each node (default)
# - "sync": Persist synchronously after each node
# - "exit": Only persist at completion

app.invoke(
    input_data,
    durability="async"  # Choose based on your needs
)

# Migration from v0.5
# OLD: app.invoke(data, config={"checkpoint_during": True})
# NEW: app.invoke(data, durability="async")
```

## Best Practices

### 1. State Design

```python
# ✅ Good: Clear, typed state
class WellDesignedState(TypedDict):
    user_input: str
    processing_step: str
    results: list[dict]
    error_message: Optional[str]

# ❌ Avoid: Unclear, untyped state
class PoorState(TypedDict):
    data: Any  # Too generic
    stuff: dict  # Unclear purpose
```

### 2. Node Function Design

```python
# ✅ Good: Pure function, clear purpose
def validate_input(state: UserState) -> dict:
    """Validate user input and return validation results"""
    is_valid = len(state["user_input"]) > 0
    return {
        "input_valid": is_valid,
        "validation_message": "Input valid" if is_valid else "Input required"
    }

# ❌ Avoid: Side effects, unclear purpose
def bad_node(state):
    # Modifies external state - bad!
    global some_global_var
    some_global_var = state["data"]

    # No clear return contract
    if random.random() > 0.5:
        return {"result": "maybe"}
    # Sometimes returns nothing - bad!
```

### 3. Error Handling

```python
def robust_node(state: State) -> dict:
    """Node with proper error handling"""
    try:
        result = risky_operation(state["input"])
        return {
            "result": result,
            "status": "success",
            "error": None
        }
    except Exception as e:
        return {
            "result": None,
            "status": "error",
            "error": str(e)
        }

def error_router(state: State) -> str:
    """Route based on error status"""
    if state.get("status") == "error":
        return "error_handler"
    return "success_handler"
```

### 4. Conditional Logic

```python
# ✅ Good: Clear, explicit routing
def clear_router(state: AgentState) -> str:
    """Determine next step based on current state"""
    if not state.get("user_input"):
        return "request_input"
    elif state.get("needs_validation"):
        return "validate"
    elif state.get("ready_to_process"):
        return "process"
    else:
        return "error"

# ❌ Avoid: Complex, hard-to-follow logic
def confusing_router(state):
    return "a" if state.get("x") and not state.get("y") or state.get("z", {}).get("nested") else "b" if state["other"] else "c"
```

## Integration with LangChain

LangGraph works seamlessly with LangChain components:

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Use LangChain chains in nodes
prompt = ChatPromptTemplate.from_template("Process this: {input}")
llm = ChatOpenAI()
chain = prompt | llm | StrOutputParser()

def langchain_node(state: State):
    """Node using LangChain chain"""
    result = chain.invoke({"input": state["user_input"]})
    return {"processed_output": result}
```

## Common Use Cases

### 1. Chatbot with Memory

```python
class ChatState(TypedDict):
    messages: Annotated[list, add_messages]

def chatbot(state: ChatState):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

workflow = StateGraph(ChatState)
workflow.add_node("chat", chatbot)
workflow.add_edge(START, "chat")
workflow.add_edge("chat", END)

chatbot_app = workflow.compile(checkpointer=InMemorySaver())
```

### 2. Research Assistant

```python
def research_node(state: ResearchState):
    """Conduct research on the topic"""
    query = state["research_query"]
    results = search_tool.invoke(query)
    return {"research_results": results}

def analyze_node(state: ResearchState):
    """Analyze research results"""
    analysis = analyze_tool.invoke(state["research_results"])
    return {"analysis": analysis}

def report_node(state: ResearchState):
    """Generate final report"""
    report = generate_report(state["analysis"])
    return {"final_report": report}
```


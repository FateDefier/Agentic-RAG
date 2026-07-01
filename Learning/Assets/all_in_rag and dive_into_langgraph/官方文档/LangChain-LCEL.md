# LangChain LCEL / Runnable / Runtime Concepts

Source: https://docs.langchain.com/oss/python/langchain/runtime and https://docs.langchain.com/oss/python/langgraph/pregel

## Overview

LangChain's `create_agent` runs on LangGraph's runtime under the hood. The runtime (Pregel) manages the execution of LangGraph applications.

**LCEL (LangChain Expression Language)** is the declarative syntax for composing LangChain components into chains. In the current architecture, LCEL is built on top of LangGraph's Pregel runtime, and PregelNodes implement LangChain's **Runnable** interface.

## Runtime Object

LangGraph exposes a `Runtime` object with the following information:

1. **Context**: static information like user id, db connections, or other dependencies for an agent invocation
2. **Store**: a `BaseStore` instance used for long-term memory
3. **Stream writer**: an object used for streaming information via the "custom" stream mode
4. **Execution info**: identity and retry information for the current execution (thread ID, run ID, attempt number)
5. **Server info**: server-specific metadata when running on LangGraph Server (assistant ID, graph ID, authenticated user)

Runtime context provides **dependency injection** for your tools and middleware. Instead of hardcoding values or using global state, you can inject runtime dependencies (like database connections, user IDs, or configuration) when invoking your agent.

### Using context_schema

```python
from dataclasses import dataclass
from langchain.agents import create_agent

@dataclass
class Context:
    user_name: str

agent = create_agent(
    model="gpt-5-nano",
    tools=[...],
    context_schema=Context  
)

agent.invoke(
    {"messages": [{"role": "user", "content": "What's my name?"}]},
    context=Context(user_name="John Smith")
)
```

### Accessing Runtime in Tools

```python
from dataclasses import dataclass
from langchain.tools import tool, ToolRuntime

@dataclass
class Context:
    user_id: str

@tool
def fetch_user_email_preferences(runtime: ToolRuntime[Context]) -> str:
    """Fetch the user's email preferences from the store."""
    user_id = runtime.context.user_id  
    preferences: str = "The user prefers you to write a brief and polite email."
    if runtime.store:
        if memory := runtime.store.get(("users",), user_id):
            preferences = memory.value["preferences"]
    return preferences
```

### Accessing Runtime in Middleware

```python
from dataclasses import dataclass
from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import dynamic_prompt, ModelRequest, before_model, after_model
from langgraph.runtime import Runtime

@dataclass
class Context:
    user_name: str

# Dynamic prompts with runtime context
@dynamic_prompt
def dynamic_system_prompt(request: ModelRequest) -> str:
    user_name = request.runtime.context.user_name  
    system_prompt = f"You are a helpful assistant. Address the user as {user_name}."
    return system_prompt

# Before model hook
@before_model
def log_before_model(state: AgentState, runtime: Runtime[Context]) -> dict | None:
    print(f"Processing request for user: {runtime.context.user_name}")
    return None

agent = create_agent(
    model="gpt-5-nano",
    tools=[...],
    middleware=[dynamic_system_prompt, log_before_model],
    context_schema=Context
)
```

## LangGraph Runtime (Pregel)

**Pregel** implements LangGraph's runtime, managing the execution of LangGraph applications. Compiling a `StateGraph` or creating an `@entrypoint` produces a Pregel instance that can be invoked with input.

### How Pregel Works

Pregel combines **actors** and **channels** into a single application. Actors read data from channels and write data to channels. Pregel organizes execution into multiple steps following the **Bulk Synchronous Parallel** model.

Each step consists of three phases:
1. **Plan**: Determine which actors to execute in this step
2. **Execution**: Execute all selected actors in parallel
3. **Update**: Update the channels with the values written by the actors

Repeat until no actors are selected for execution, or a maximum number of steps is reached.

### Actors (PregelNodes)

An actor is a **PregelNode**. It subscribes to channels, reads data from them, and writes data to them. **PregelNodes implement LangChain's Runnable interface.**

### Channels

Channels communicate between actors:

| Channel Type | Description |
|---|---|
| **LastValue** | Default. Stores the last value written, overwriting previous values. |
| **Topic** | Configurable PubSub channel for sending multiple values between actors or accumulating output across steps. |
| **BinaryOperatorAggregate** | Stores persistent value updated by applying a binary operator to current value and each new update. |
| **DeltaChannel** | Stores only incremental delta at each step (beta, langgraph>=1.2). |

### Example: Pregel Direct Usage

```python
from langgraph.channels import EphemeralValue
from langgraph.pregel import Pregel, NodeBuilder

node1 = (
    NodeBuilder().subscribe_only("a")
    .do(lambda x: x + x)
    .write_to("b")
)

app = Pregel(
    nodes={"node1": node1},
    channels={
        "a": EphemeralValue(str),
        "b": EphemeralValue(str),
    },
    input_channels=["a"],
    output_channels=["b"],
)

app.invoke({"a": "foo"})
# Returns: {'b': 'foofoo'}
```

### High-Level APIs

LangGraph provides two high-level APIs for creating a Pregel application:

1. **StateGraph (Graph API)** - Define a graph of nodes and edges. When compiled, automatically creates the Pregel application.

2. **Functional API** - Use `@entrypoint` decorator for a more functional programming style.

### StateGraph Example

```python
from typing import TypedDict
from langgraph.constants import START
from langgraph.graph import StateGraph

class Essay(TypedDict):
    topic: str
    content: str | None
    score: float | None

def write_essay(essay: Essay):
    return {"content": f"Essay about {essay['topic']}"}

def score_essay(essay: Essay):
    return {"score": 10}

builder = StateGraph(Essay)
builder.add_node(write_essay)
builder.add_node(score_essay)
builder.add_edge(START, "write_essay")
builder.add_edge("write_essay", "score_essay")

# Compile returns a Pregel instance
graph = builder.compile()

# Inspect nodes and channels
print(graph.nodes)
print(graph.channels)
```

### LCEL in Practice (from LangGraph docs)

From the LangSmith evaluation guide, LCEL declarative syntax works like this:

```python
# We use LCEL declarative syntax here
# Remember that langgraph graphs are also langchain runnables
target = example_to_state | app
```

This pipes the output of `example_to_state` into the `app` graph, demonstrating the familiar `|` operator from LCEL.

## Key Concept: Runnable Interface

- **PregelNodes implement LangChain's Runnable interface**, meaning any compiled LangGraph graph can be used as a Runnable in LCEL pipelines.
- The `Runnable` interface provides a standard way to invoke, stream, batch, and compose chains.
- `RunnableConfig` is used for passing configuration (like thread_id) to invocations.

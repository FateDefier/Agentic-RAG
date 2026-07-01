# MCP Server - 学习笔记

> 对应课程：[[07-MCP_Server|📖 第7章 MCP Server]]

---

## 练习题

### 基础题

1. MCP 的全称是什么？它主要解决什么问题？




2. MCP Server 支持哪两种传输方式（transport）？它们分别适用于什么场景？




3. 使用 `python -m 包名` 启动 MCP Server 的原理是什么？这依赖于哪个特殊文件？




4. `MultiServerMCPClient` 的作用是什么？如何同时接入多个 MCP Server？




5. `supervisord` 在 MCP 服务管理中扮演什么角色？它的核心功能有哪些？




6. 在 `.py` 文件中调用 MCP 服务与在 Jupyter Notebook 中调用有何不同？应该如何处理？




### 进阶题

1. 比较 MCP 的 stdio 和 streamable_http 两种传输方式在性能、安全性和部署复杂度上的差异。什么场景下应该选择 stdio？什么场景下应该选择 HTTP？




2. MCP（Model Context Protocol）与 Function Calling 有何区别与联系？它们在大模型工具调用生态中各自扮演什么角色？




3. 如果需要在生产环境中部署多个 MCP Server 并保证高可用，应该如何设计架构？请考虑负载均衡、健康检查、自动重启等机制。




### 编程/实践题

1. 请编写一个自定义的 MCP Server，提供两个工具：
   - `search_news(keyword: str)`：根据关键词搜索新闻（返回模拟数据即可）
   - `get_date()`：返回当前日期
   然后使用 `MultiServerMCPClient` 将该 MCP Server 接入 LangGraph Agent。

```python
# server.py - MCP Server 实现
from fastmcp import FastMCP

# 请在这里完成代码

```

```python
# agent.py - 接入 LangGraph
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

# 请在这里完成代码

```

---

## 大厂面试题精选

1. **什么是 MCP 协议？它解决了什么问题？**（大模型架构岗/算法岗）
   - 来源：Anthropic/OpenAI/字节跳动面试题
   - 解析：MCP（Model Context Protocol）是 Anthropic 于 2024 年底推出的开放协议，标准化了 AI 应用与外部工具/数据源的交互方式，解决了工具接入碎片化问题。

2. **MCP 与 Function Calling 的区别是什么？**（AI 工程化岗）
   - 来源：多家大厂面试高频题
   - 解析：Function Calling 解决的是"模型如何输出结构化的工具调用请求"，MCP 解决的是"工具如何标准化接入"。两者是不同层面的概念，可互补使用。

3. **MCP 的 Client-Server 架构是怎样的？Host、Client、Server 三层如何分工？**（系统设计岗）
   - 来源：Google/Microsoft 面试题
   - 解析：Host 是用户交互的 AI 应用（如 Claude Desktop），Client 负责与 Server 建立连接和管理通信，Server 暴露工具能力。

4. **MCP Server 开发中需要注意哪些关键设计决策？常见坑有哪些？**（后端/全栈岗）
   - 来源：AI Agent 工程师面试题
   - 解析：需关注认证状态持久化、并发安全、工具描述清晰度、工具数量控制、生命周期管理等。

5. **MCP 和 A2A（Agent-to-Agent Protocol）的关系是什么？**（高级架构师岗）
   - 来源：2025-2026 年新兴面试题
   - 解析：MCP 解决 Agent 与工具的连接，A2A 解决 Agent 与 Agent 的通信，两者互补，未来大概率共存。

---

## 要点整理

### MCP 核心概念

| 概念 | 说明 |
|------|------|
| **MCP** | Model Context Protocol，模型上下文协议，Anthropic 推出的开放标准 |
| **目的** | 让大模型能够标准化地连接外部数据源和工具 |
| **架构** | Host → Client → Server 三层架构 |
| **传输方式** | stdio（本地进程通信）和 streamable_http（远程 HTTP 通信） |
| **通信协议** | JSON-RPC 2.0 |

### MCP Server 开发流程

| 步骤 | 说明 |
|------|------|
| 1. 创建包结构 | `__init__.py` + `__main__.py` + `server.py` |
| 2. 定义工具 | 使用 `FastMCP` 和 `@mcp.tool` 装饰器 |
| 3. 配置入口 | `__main__.py` 中定义 stdio() 和 http() 入口 |
| 4. 部署运行 | `python -m 包名` 或使用 supervisord 管理 |
| 5. 接入 LangGraph | 使用 `MultiServerMCPClient` 获取 tools |

### 依赖包

```
langchain[openai]          # LangChain 核心
langchain-mcp-adapters     # MCP 适配器
langgraph                  # LangGraph 核心
langgraph-supervisor       # 监督者模式
langgraph-checkpoint-sqlite # 持久化检查点
```

### supervisor 常用命令

| 命令 | 说明 |
|------|------|
| `supervisord -c <conf>` | 启动 supervisord |
| `pkill -f supervisord` | 关闭 supervisord |
| `lsof -i :8000` | 检查端口状态 |

---

## 参考答案汇总

### 基础题答案

1. MCP 全称是 **Model Context Protocol（模型上下文协议）**。它主要解决的是大模型与外部工具/数据源集成的碎片化问题，通过标准化接口让 AI 应用能够可靠、高效地连接到不同的数据源和工具，实现"一次实现、到处复用"。

2. MCP Server 支持 **stdio** 和 **streamable_http** 两种传输方式：
   - **stdio**：通过标准输入输出进行本地进程间通信，适合本地运行的 MCP Server
   - **streamable_http**：通过 HTTP 协议进行远程通信，适合远程部署的 MCP Server

3. `python -m 包名` 的原理是执行包中的 `__main__.py` 特殊文件。`__main__.py` 中定义并启动了 http() 函数，从而启动 MCP Server。

4. `MultiServerMCPClient` 是 `langchain-mcp-adapters` 提供的客户端类，可以同时管理多个 MCP Server 的连接。通过传入字典配置每个 Server 的传输方式、地址等参数，然后调用 `client.get_tools()` 获取所有工具列表。

5. `supervisord` 是一个进程管理工具，核心功能包括：管理 MCP 进程的启动/停止、在 MCP 挂掉时自动拉起、日志管理、进程组管理等。

6. 在 Jupyter Notebook 中可以直接使用 `await use_mcp(messages)` 调用。在 `.py` 文件中需要使用 `asyncio.run()` 包裹异步调用，即定义 `async def main()` 函数然后 `asyncio.run(main())`。

### 进阶题参考答案

1. **stdio**：优点是无网络开销，安全性高（本地通信），部署简单；缺点是只能在本地使用，无法远程调用。适合开发和单机部署。**streamable_http**：优点是支持远程调用，适合分布式部署和多个客户端共享；缺点是需要网络配置和安全防护。适合生产环境多服务部署。

2. **Function Calling** 是模型层面输出结构化调用请求的能力，解决"模型怎么表示想用工具"的问题。**MCP** 是工具层面的标准化接入协议，解决"工具怎么被 Agent 发现和调用"的问题。两者互补：Function Calling 是模型输出格式，MCP 是工具接入标准。

3. 生产环境架构建议：（1）使用 supervisord 或 systemd 管理单个节点的 MCP 进程，配置 auto-restart；（2）多个 MCP Server 实例部署在不同节点，前端加负载均衡；（3）使用健康检查端点定期检测服务状态；（4）使用 streamable_http 传输方式，方便横向扩展。

### 编程题参考实现

```python
# server.py
from fastmcp import FastMCP
from datetime import datetime

mcp = FastMCP("news_mcp")

@mcp.tool
def search_news(keyword: str) -> str:
    """Search news by keyword."""
    # 模拟新闻搜索
    news_db = {
        "AI": ["AI 大模型突破新纪录", "AI 安全框架发布"],
        "科技": ["芯片技术新突破", "量子计算最新进展"],
    }
    results = news_db.get(keyword, [f"关于{keyword}的模拟新闻"])
    return "\n".join(results)

@mcp.tool
def get_date() -> str:
    """Get current date."""
    return datetime.now().strftime("%Y-%m-%d")

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

```python
# agent.py
async def main():
    client = MultiServerMCPClient({
        "news": {
            "command": "python",
            "args": ["path/to/server.py"],
            "transport": "stdio",
        }
    })
    tools = await client.get_tools()
    agent = create_agent(llm, tools=tools)
    response = await agent.ainvoke({
        "messages": [{"role": "user", "content": "搜索AI相关新闻"}]
    })
    print(response["messages"][-1].content)
```

### 大厂面试题参考解答

1. **MCP 协议**：由 Anthropic 在 2024 年 11 月发布，2025 年 12 月捐献给 Linux 基金会旗下的 Agentic AI Foundation。MCP 定义了 Client-Server 架构，通过 JSON-RPC 2.0 通信，提供 Tools、Resources、Prompts 三类核心能力。它解决了之前每个 Agent 框架对接每个工具都要写一套适配代码的问题（M×N 复杂度降为 M+N）。

2. **MCP vs Function Calling**：Function Calling 是模型自身的能力，决定"什么时候调用什么工具"。MCP 是工具接入的协议标准，决定"工具如何被描述、发现和调用"。一个 MCP Server 的工具最终通过 Function Calling 机制被模型调用。

3. **Host-Client-Server 三层**：Host 是用户直接交互的 AI 应用（如 Claude Desktop），Client 是嵌入 Host 中的 MCP 客户端组件（负责连接 Server、管理会话），Server 是独立的工具服务进程（暴露具体工具能力）。一个 Client 可连接多个 Server。

4. **MCP 开发注意事项**：认证状态不持久（重启后 session 丢失）、并发安全问题（多 Agent 同时调用）、工具描述要清晰（影响模型调用准确率）、工具数量要适度（过多增加上下文负担）。

5. **MCP 与 A2A 的关系**：MCP 是 Agent-to-Tools 协议，A2A（Agent-to-Agent）是 Google 推出的 Agent 间通信协议。MCP 让 Agent 能拿工具，A2A 让 Agent 能互相交流。两者互补共存，构成未来 Agent 生态的基础设施。

# LangGraph CLI - 学习笔记

> 对应课程：[[14-LangGraph_CLI|📖 LangGraph CLI]]

---

## 练习题

### 基础题

1. LangGraph CLI 是什么？它主要用来解决什么问题？

2. 使用 LangGraph CLI 调试功能时需要满足什么条件？为什么说这个功能「不是端侧的」？

3. LangSmith 是什么？它和 LangGraph CLI 是什么关系？

4. `langgraph.json` 配置文件的作用是什么？它包含哪三个核心字段？

5. `langgraph dev` 命令的作用是什么？如何指定非默认的配置文件？

### 进阶题

1. 比较 `langgraph dev` 和 `langgraph up` 的区别。在什么场景下应该使用哪一个？

2. LangGraph CLI 的调试页面通过 LangSmith Studio 提供可视化界面。请分析该调试页面能够展示哪些 Agent 运行信息？这对 Agent 开发调试有什么帮助？

3. 当使用 LangGraph CLI 部署到生产环境时，数据会经过 LangChain 的服务器。这一设计在数据安全方面有哪些考虑？作者给出了什么建议？

### 编程/实践题

1. 编写一个简单的 Agent 后端的 Python 文件 `simple_agent.py`，并创建对应的 `langgraph.json` 配置文件，使该 Agent 可以通过 LangGraph CLI 启动和调试。

---

## 大厂面试题精选

1. **（LangChain 生态面试题）** 请解释 LangChain、LangGraph、LangSmith 三者的定位和关系。在构建一个生产级 Agent 应用时，这三个工具分别扮演什么角色？

2. **（通用大厂面试题 - Agent 部署）** 如何将一个 LangGraph Agent 部署到生产环境？请描述从本地开发到线上部署的完整流程，包括 CLI 配置、容器化、监控等环节。

3. **（面试高频题）** LangGraph 在可观测性（Observability）方面提供了哪些支持？请解释 `stream`、`events`、`channels` 以及 LangSmith 集成在调试和监控 Agent 行为中的作用。

4. **（阿里/腾讯 - AI 工程化）** 在 Agent 应用中，如何追踪和调试每一步的工具调用？如果某一步返回了错误结果，你如何定位问题并进行重试或回滚？

---

## 要点整理

### LangGraph CLI 概述
- **LangGraph CLI**：LangGraph 的命令行工具，用于本地启动、调试、测试和托管 Agent
- **调试页面**：通过 LangSmith Studio 提供可视化调试界面
- ⚠️ **注意**：该功能需要联网，数据会发送到 LangChain 服务器，不要用于敏感数据

### 环境要求
```bash
pip install "langgraph-cli[inmem]"
```

### LangSmith
- **LangSmith**：LangChain 团队推出的 LLM 应用数据分析平台
- 功能：可视化地管理和优化应用开发全流程
- 性质：付费 PaaS（提供部分免费功能）
- 用途：调试、测试、评估、监控 LLM 应用

### 配置文件 langgraph.json

```json
{
    "dependencies": ["./"],
    "graphs": {
        "supervisor": "./simple_agent.py:get_app"
    },
    "env": "./.env"
}
```

| 字段 | 说明 |
|------|------|
| `dependencies` | 项目依赖路径 |
| `graphs` | Agent 入口映射（名称 → 文件:函数） |
| `env` | 环境变量文件路径 |

### 启动命令

| 命令 | 说明 |
|------|------|
| `langgraph dev` | 启动开发调试服务器（开发环境） |
| `langgraph dev --config [your_agent].json` | 使用自定义配置文件启动 |
| `langgraph up` | 启动生产环境测试服务器（Docker） |
| `langgraph build` | 构建 Docker 镜像 |
| `langgraph deploy` | 构建并部署到 LangSmith Deployments |

### Agent 后端示例

```python
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

_ = load_dotenv()

llm = ChatOpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
    model="qwen3-coder-plus",
)

agent = create_agent(model=llm)

# langgraph-cli 入口函数
def get_app():
    return agent
```

### 调试页面的功能
- 可视化展示 Agent 执行流程（Graph 结构）
- 实时查看每一步的输入/输出
- 查看 Prompt、Tool Calls、Tool Results
- 支持多轮对话调试
- 集成 LangSmith Trace 追踪

### 生产环境替代方案
- 由于调试页面不开源，生产环境建议使用开源替代方案
- 推荐：[clickhouse-chatbi](https://github.com/luochang212/clickhouse-chatbi)（基于 Next.js + nextjs-ai-chatbot 模板）

### LangChain 生态总结

| 工具 | 定位 | 功能 |
|------|------|------|
| **LangChain** | 应用框架 | 构建 LLM 应用的组件库（模型 I/O、检索、工具、Agent） |
| **LangGraph** | 编排引擎 | 有状态、循环、条件分支的工作流编排 |
| **LangSmith** | 监控平台 | 调试、测试、评估、监控 LLM 应用 |

---

## 参考答案汇总

### 基础题

1. **LangGraph CLI** 是 LangGraph 的命令行开发工具，用于本地启动、调试、测试和托管 LangGraph Agent。它解决了 Agent 开发过程中的可视化调试和测试需求。

2. 使用该功能需要：安装 `langgraph-cli[inmem]`、配置 `langgraph.json`、拥有有效的 LangSmith API Key。"不是端侧"指的是调试页面运行在 LangChain 的云端服务器上，数据必须联网发送到 LangChain 服务器才能展示。

3. **LangSmith** 是 LangChain 团队的 LLM 应用全生命周期管理平台。LangGraph CLI 的调试页面通过 LangSmith Studio 提供可视化界面，两者是底层平台与前端工具的关系——CLI 启动本地服务，LangSmith 提供调试 UI。

4. **配置文件作用**：定义 Agent 的入口、依赖和环境变量。
   - `dependencies`：项目依赖
   - `graphs`：Agent 名称到入口函数的映射
   - `env`：环境变量文件路径

5. `langgraph dev` 启动轻量级开发调试服务。使用 `--config` 参数指定自定义配置文件，如 `langgraph dev --config my_agent.json`。

### 进阶题

1. **`langgraph dev` vs `langgraph up`**：
   - `langgraph dev`：轻量级，直接运行在当前环境，适合日常开发迭代
   - `langgraph up`：通过 Docker 启动完整服务（含 PostgreSQL、Redis），更接近生产环境，适合集成测试

2. **调试页面展示的信息**：
   - Agent 的整体图结构（节点和边）
   - 每一步的 Input/Output
   - LLM 调用的 Prompt 和 Response
   - 工具调用的参数和返回结果
   - 整个执行链路的 Trace 追踪
   
   这些信息让开发者可以逐帧审视 Agent 的"思考过程"，快速定位推理错误、工具调用失败等问题。

3. **数据安全考虑**：由于调试页面需要联网将数据发送到 LangChain 服务器，敏感信息（API Key、用户隐私数据、商业机密）会暴露给第三方。作者建议：不要在调试页面访问敏感数据，生产环境使用开源前端方案替代。

### 编程/实践题

```python
# simple_agent.py
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

_ = load_dotenv()

llm = ChatOpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
    model="qwen3-coder-plus",
)

agent = create_agent(model=llm)

def get_app():
    return agent
```

```json
// langgraph.json
{
    "dependencies": ["./"],
    "graphs": {
        "supervisor": "./simple_agent.py:get_app"
    },
    "env": "./.env"
}
```

启动命令：
```bash
pip install "langgraph-cli[inmem]"
langgraph dev
```

浏览器将自动打开调试页面，可在可视化界面中与 Agent 进行对话和调试。

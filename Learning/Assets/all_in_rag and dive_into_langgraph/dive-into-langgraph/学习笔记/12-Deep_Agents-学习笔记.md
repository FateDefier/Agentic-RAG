# Deep Agents - 学习笔记

> 对应课程：[[12-Deep_Agents|📖 Deep Agents]]

---

## 练习题

### 基础题

1. Deep Agents 是什么？它和普通的 LangChain Agent 在能力上有哪些主要区别？

2. 本章用 Deep Agents 查询的示例问题是什么？为什么选择这个问题来验证 Deep Agents 的能力？

3. Deep Agents 的 `create_deep_agent` 函数需要哪些关键参数？与 `create_agent` 相比有何异同？

4. 在 Deep Agents 中，`get_today_date` 这个工具的作用是什么？为什么 Deep Research 场景需要获取当前日期？

5. Deep Agents 的 System Prompt 中包含了 `research_instructions`，这段提示词的核心作用是什么？

### 进阶题

1. Deep Agents 的"深度研究"能力通过哪些机制实现？与传统的 ReAct 循环相比，Deep Agents 在长任务规划上有哪些优势？

2. 在 Deep Agents 中，多个工具（如 `dashscope_search` 和 `get_today_date`）是如何协同工作的？Agent 如何决定在什么时机调用哪个工具？

3. 如果 Deep Agents 在执行研究任务时中途失败（如搜索 API 超时），框架是否有内置的重试或容错机制？请结合 LangGraph 的图结构来说明。

### 编程/实践题

1. 使用 `create_deep_agent` 编写一个深度研究 Agent，要求能够回答"请介绍 2025 年诺贝尔化学奖得主及其主要贡献"。需要包含搜索工具和日期工具，并输出研究结果。

---

## 大厂面试题精选

1. **（阿里巴巴 - 大模型应用开发）** Deep Research 类应用的核心架构是什么？如何设计一个支持多步推理、多源信息检索的深度研究 Agent？请描述 Supervisor-Sub-agent 架构的设计思路。

2. **（字节跳动 - AI Agent 开发岗）** Deep Agents 和传统 ReAct Agent 在长任务处理上有何本质区别？当 Agent 需要执行 20 步以上的工具调用时，如何处理上下文窗口限制和上下文丢失问题？

3. **（通用大厂面试题）** 什么是 IterResearch 框架？它如何解决 ReAct 在长任务中上下文线性增长的问题？请说明「常量工作空间」的概念。

4. **（LangChain 相关面试题）** 在构建复杂 Agent 系统时，如何规划 Agent 的记忆机制？短期记忆和长期记忆分别适用于什么场景？如何将搜索历史纳入 Agent 的推理上下文？

---

## 要点整理

### Deep Agents 概述
- **Deep Agents** = LangChain 团队出品的 DeepResearch 类框架
- 定位：解决复杂、长时程、需要深度研究的任务
- 核心能力：主动调用搜索、多步推理、深度洞察、生成研究报告

### 与普通 Agent 的对比

| 特性 | 普通 Agent (ReAct) | Deep Agents |
|------|-------------------|-------------|
| 任务复杂度 | 适合单步或少步任务 | 适合多步深度研究 |
| 推理深度 | 浅层推理 | 深层推理（Supervisor + Sub-agent） |
| 搜索策略 | 单次搜索 | 多轮、多源搜索 |
| 输出形式 | 简短回答 | 结构化研究报告 |
| 任务规划 | 缺乏显式规划 | 内置 Planning Tool |

### Deep Agents 核心架构（LangChain Open Deep Research）
- **Scope 阶段**：澄清用户需求，生成 Research Brief
- **Research 阶段**：Supervisor 拆解子任务，Sub-agents 并行研究
- **写作阶段**：独立写作 LLM 整合信息生成结构化报告

### 关键代码解析

```python
from deepagents import create_deep_agent

# 系统提示词：引导 Agent 扮演资深研究员
research_instructions = """你是一名资深研究员。你的工作是进行全面深入的研究，
并撰写一份精炼的报告。"""

# 创建深度 Agent（含搜索工具和日期工具）
agent = create_deep_agent(
    model=llm,
    tools=[dashscope_search, get_today_date],
    system_prompt=research_instructions
)

# 执行深度研究
result = agent.invoke({"messages": [
    {"role": "user", "content": "新上任的玻利维亚总统是谁？"}
]})
```

### 验证方法
- 示例问题：**"新上任的玻利维亚总统是谁？"**
- 玻利维亚总统 `罗德里戈·帕斯·佩雷拉` 于 2025 年 11 月 8 日上任
- 该信息不在模型预训练数据中，必须通过联网搜索获取
- 验证了 Deep Agents 是否真的具备联网搜索和深度研究能力

### 关键设计原则
1. **Task Planning**：将复杂任务分解为可执行的子任务
2. **Parallel Execution**：Sub-agents 并行研究，提高效率
3. **Context Isolation**：每个 Sub-agent 拥有独立上下文，避免干扰
4. **Structured Output**：最终输出结构化的研究报告，附带引用来源

---

## 参考答案汇总

### 基础题

1. **Deep Agents** 是 LangChain 团队推出的深度研究框架，可视为 LangChain 版的 DeepResearch。与普通 Agent 的主要区别在于：它具备显式的任务规划、多 Agent 协作、深度推理和结构化报告生成能力，而不仅仅是简单的 ReAct 循环。

2. **示例问题**："新上任的玻利维亚总统是谁？请介绍一下这位总统。"该问题涉及 2025 年 11 月的实时信息，不在模型预训练数据中，可以验证 Deep Agents 是否真正实现了联网搜索和深度研究能力。

3. `create_deep_agent` 需要三个关键参数：`model`（语言模型）、`tools`（工具列表）、`system_prompt`（系统提示词）。与 `create_agent` 基本相同，但 Deep Agents 内部使用更复杂的图结构来编排任务。

4. `get_today_date` 工具获取当前日期，帮助 Agent 在搜索时确定时间范围。Deep Research 场景中，很多问题需要基于当前时间进行时效性判断（如查询最新新闻）。

5. `research_instructions` 系统提示词定义 Agent 的角色（资深研究员）和工作方式，引导其进行全面深入的研究并撰写精炼报告，同时说明如何使用搜索工具。

### 进阶题

1. **深度研究机制**：通过 Supervisor-Sub-agent 架构实现任务拆解和并行执行，配合 Planning Tool 进行长程规划。相比传统 ReAct，Deep Agents 能处理更长的任务链路，通过子任务隔离上下文避免信息混淆，并通过独立写作节点保证最终报告的结构一致性。

2. **工具协同**：Agent 根据任务需求自主决定调用时机。例如，先调用 `get_today_date` 获取日期，然后调用 `dashscope_search` 搜索相关信息。Agent 通过分析当前上下文和子目标完成情况，动态决策下一步调用哪个工具。

3. Deep Agents 基于 LangGraph 构建，LangGraph 的图结构天然支持条件分支和循环。可以通过设计重试节点（retry node）或 fallback 路径来实现容错。框架本身不提供自动重试，但开发者可以在图中添加错误处理逻辑。

### 编程/实践题

```python
import os
from datetime import datetime
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from deepagents import create_deep_agent
from dashscope import Generation

_ = load_dotenv()

llm = ChatOpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
    model="qwen3-max",
)

@tool
def dashscope_search(query: str) -> str:
    """使用夸克搜索 API 搜索互联网信息"""
    response = Generation.call(
        model='qwen-max',
        prompt=query,
        enable_search=True,
        result_format='message'
    )
    if response.status_code == 200:
        return response.output.choices[0].message.content
    else:
        return f"Search failed: {response.status_code}"

@tool
def get_today_date() -> str:
    """获取今天的日期"""
    return datetime.now().strftime("%Y-%m-%d")

research_instructions = """你是一名资深研究员。你的工作是进行全面深入的研究，
并撰写一份精炼的报告。你可以使用互联网搜索工具作为获取信息的主要方式。"""

agent = create_deep_agent(
    model=llm,
    tools=[dashscope_search, get_today_date],
    system_prompt=research_instructions
)

result = agent.invoke({"messages": [
    {"role": "user", "content": "请介绍2025年诺贝尔化学奖得主及其主要贡献"}
]})

print(result["messages"][-1].content)
```

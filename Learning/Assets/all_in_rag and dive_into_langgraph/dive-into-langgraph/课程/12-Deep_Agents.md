# 第12章 Deep Agents

# Deep Agents

[deepagents](https://docs.langchain.com/oss/python/deepagents/overview) 可以看作是 LangChain 团队出品的 DeepResearch。本节通过查询一个近期新闻，检验 Deep Agents 是否有主动调用搜索、深度洞察的能力。

> 这里只是简单 quickstart 一下，更多信息大家去官网看吧！

```python
# !pip install deepagents dashscope
```


**1）加载模型**

```python
import os
import dashscope

from datetime import datetime
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from deepagents import create_deep_agent
from dashscope import Generation

# 加载模型配置
_ = load_dotenv()

# 为灵积配置 api_key
dashscope.api_key=os.getenv("DASHSCOPE_API_KEY")

# 加载模型
llm = ChatOpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
    model="qwen3-max",
)
```


**2）创建搜索工具**

我们使用上一节创建的 `dashscope_search` 搜索工具。

```python
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
        return (
            "Search failed with status code: "
            f"{response.status_code}, message: {response.message}"
        )
```


**3）创建深度代理**

```python
# System prompt to steer the agent to be an expert researcher
research_instructions = """你是一名资深研究员。你的工作是进行全面深入的研究，并撰写一份精炼的报告。

你可以使用互联网搜索工具作为获取信息的主要方式。

## `dashscope_search`

使用该工具对指定查询进行互联网搜索。
"""

@tool
def get_today_date() -> str:
    """获取今天的日期"""
    return datetime.now().strftime("%Y-%m-%d")

agent = create_deep_agent(
    model=llm,
    tools=[dashscope_search, get_today_date],
    system_prompt=research_instructions
)
```


**4）运行 Agent**

我们的问题是：

```
新上任的玻利维亚总统是谁？请介绍一下这位总统。
```

因为近期（2025 年 11 月 8 日）玻利维亚总统 `罗德里戈・帕斯・佩雷拉` 刚刚上任，这条信息肯定不在预训练数据里。可以用这个问题验证 Deep Agents 是否真的联网了。

```python
result = agent.invoke({"messages": [
    {"role": "user", "content": "新上任的玻利维亚总统是谁？请介绍一下这位总统。"}
]})

# 最终回复
print(result["messages"][-1].content)
```


```python
# 思考过程
for message in result["messages"]:
    message.pretty_print()
```

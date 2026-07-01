# RAGAS 评估框架 - 学习笔记

> 来源：[RAGAS 官方文档](https://docs.ragas.io/en/stable/)
> 最后更新：2025-12-09

---

## 一、RAGAS 是什么

Ragas 是一个帮助你将 LLM 应用评估从"感觉还行"升级到**系统化评估循环**的库。它提供 LLM-driven metrics + systematic experimentation，形成持续改进闭环。

### 核心功能

- **Experiments（实验）**：以实验驱动的方式评估变更效果
- **Metrics（指标）**：预设指标库 + 自定义指标（装饰器方式）
- **Datasets（数据集）**：内置数据集管理、结果追踪
- **集成**：与 LangChain、LlamaIndex 等主流框架兼容

---

## 二、安装

```bash
# 基础安装
pip install ragas

# 最新开发版
pip install git+https://github.com/vibrantlabsai/ragas.git

# 如需使用 langchain_openai
pip install -U "langchain-core>=0.2,<0.3" "langchain-openai>=0.1,<0.2" openai
```

---

## 三、快速开始

### 3.1 创建项目

```bash
# uvx 方式（无需安装）
uvx ragas quickstart rag_eval
cd rag_eval

# 安装依赖
uv sync
# 或
pip install -e .
```

### 3.2 设置 API Key

```bash
export OPENAI_API_KEY="your-openai-key"
```

### 3.3 项目结构

```
rag_eval/
├── README.md              # 项目文档
├── pyproject.toml         # 项目配置
├── rag.py                 # RAG 应用
├── evals.py               # 评估工作流
├── __init__.py
└── evals/
    ├── datasets/          # 测试数据
    ├── experiments/       # 评估结果
    └── logs/              # 执行日志
```

### 3.4 运行评估

```bash
uv run python evals.py
```

评估流程：加载测试数据 → 查询 RAG 系统 → 评估回答 → 控制台显示结果 → 保存 CSV 到 `evals/experiments/`

### 3.5 添加测试用例

```python
from ragas import Dataset

def load_dataset():
    dataset = Dataset(
        name="test_dataset",
        backend="local/csv",
        root_dir=".",
    )
    data_samples = [
        {"question": "What is Ragas?", "grading_notes": "Ragas is an evaluation framework for LLM applications"},
        {"question": "How do metrics work?", "grading_notes": "Metrics evaluate the quality and performance of LLM responses"},
    ]
    for sample in data_samples:
        dataset.append(sample)
    dataset.save()
    return dataset
```

### 3.6 自定义评估指标

```python
from ragas.metrics import DiscreteMetric
from ragas.llms import llm_factory

my_metric = DiscreteMetric(
    name="custom_evaluation",
    prompt="Evaluate this response: {response} based on: {context}. Return 'excellent', 'good', or 'poor'.",
    allowed_values=["excellent", "good", "poor"],
)
```

---

## 四、核心概念

### 4.1 Experiments（实验）

实验是**对应用进行的可控变更**，用于测试假设。例如：替换检索器模型，评估新 embedding 模型的影响。

#### 好实验的原则

1. **可量化指标**：用准确率、精确率、召回率等量化变更影响
2. **系统化结果存储**：结果有序存放，便于对比追踪
3. **隔离变更**：一次只改一个变量
4. **迭代流程**：`做变更 → 跑评估 → 观察结果`

#### 实验的组成部分

- **测试数据集**：评估系统所用的数据
- **应用端点**：被测试的应用、组件或模型
- **指标**：衡量性能的量化标准

#### 执行流程

```
Setup（定义参数+加载数据）→ Run（逐条执行）→ Evaluate（应用指标）→ Store（保存结果）
```

#### @experiment 装饰器

```python
from ragas import experiment
import asyncio

@experiment()
async def my_experiment(row):
    response = await asyncio.to_thread(my_system_function, row["input"])
    return {
        **row,
        "response": response,
        "experiment_name": "baseline_v1",
        "model_version": "gpt-4o",
        "timestamp": datetime.now().isoformat()
    }

# 运行
dataset = Dataset.load(name="test_data", backend="local/csv", root_dir="./data")
results = await my_experiment.arun(dataset)
```

#### 参数化实验（A/B 测试）

```python
@experiment()
async def model_comparison_experiment(row, model_name: str, temperature: float):
    response = await my_system_function(row["input"], model=model_name, temperature=temperature)
    return {
        **row,
        "response": response,
        "experiment_name": f"{model_name}_temp_{temperature}",
        "model_name": model_name,
        "temperature": temperature
    }

results_gpt4 = await model_comparison_experiment.arun(dataset, model_name="gpt-4o", temperature=0.1)
results_gpt35 = await model_comparison_experiment.arun(dataset, model_name="gpt-3.5-turbo", temperature=0.1)
```

#### 实验管理最佳实践

```
experiments/
├── 20241201-143022-baseline_v1.csv
├── 20241201-143515-gpt4o_improved_prompt.csv
└── 20241201-144001-comparison.csv
```

建议追踪的元数据：`experiment_name`, `git_commit`, `environment`, `model_version`, `total_tokens`, `response_time_ms`

### 4.2 Metrics（指标）

Ragas 提供两大类指标：

#### RAG 评估指标

| 指标 | 说明 |
|------|------|
| **Context Precision** | 检索到的上下文精确度 |
| **Context Recall** | 检索到的上下文召回率 |
| **Context Entities Recall** | 上下文实体召回率 |
| **Noise Sensitivity** | 对噪声的敏感度 |
| **Response Relevancy** | 回答相关性 |
| **Faithfulness** | 回答忠实度（是否基于检索内容） |
| **Answer Accuracy** | 回答准确率 |
| **Context Relevance** | 上下文相关性 |
| **Response Groundedness** | 回答依据充分性 |

#### Agent / Tool 评估指标

| 指标 | 说明 |
|------|------|
| **Topic Adherence** | 主题遵从度 |
| **Tool Call Accuracy** | 工具调用准确率 |
| **Tool Call F1** | 工具调用 F1 分数 |
| **Agent Goal Accuracy** | Agent 目标达成率 |

#### 自然语言对比指标

| 指标 | 说明 |
|------|------|
| **Factual Correctness** | 事实正确性 |
| **Semantic Similarity** | 语义相似度 |

#### 非 LLM 指标（字符串匹配）

| 指标 | 说明 |
|------|------|
| **BLEU Score** | 机器翻译评估 |
| **CHRF Score** | 字符级 n-gram 评估 |
| **ROUGE Score** | 文本摘要评估 |
| **String Presence** | 字符串存在性 |
| **Exact Match** | 精确匹配 |

#### 通用指标

| 指标 | 说明 |
|------|------|
| **Aspect Critic** | 方面评判 |
| **Simple Criteria Scoring** | 简单标准评分 |
| **Rubrics Based Scoring** | 基于量规的评分 |
| **Instance Specific Rubrics** | 实例特定量规 |

### 4.3 Datasets（数据集）

```python
from ragas import Dataset

# 创建数据集
dataset = Dataset(
    name="test_dataset",
    backend="local/csv",    # 存储后端
    root_dir=".",
)

# 追加样本
for sample in data_samples:
    dataset.append(sample)
dataset.save()

# 加载数据集
dataset = Dataset.load(name="test_data", backend="local/csv", root_dir="./data")
```

### 4.4 Test Data Generation（测试数据生成）

Ragas 提供合成测试数据生成的算法，支持：
- **RAG 场景**：生成含检索和生成的测试数据
- **Agentic 场景**：生成含多步工具调用的测试数据

---

## 五、评估一个简单的 RAG 系统

### 步骤 1：准备测试数据

```python
import pandas as pd

samples = [
    {"query": "What is Ragas 0.3?", "grading_notes": "- Ragas 0.3 is a library for evaluating LLM applications."},
    {"query": "How to install Ragas?", "grading_notes": "- install from source - install from pip using ragas[examples]"},
    {"query": "What are the main features of Ragas?", "grading_notes": "organised around - experiments - datasets - metrics."}
]
pd.DataFrame(samples).to_csv("datasets/test_dataset.csv", index=False)
```

### 步骤 2：定义评估指标

```python
from ragas.metrics import DiscreteMetric

my_metric = DiscreteMetric(
    name="correctness",
    prompt="Check if the response contains points mentioned from the grading notes and return 'pass' or 'fail'.\nResponse: {response} Grading Notes: {grading_notes}",
    allowed_values=["pass", "fail"],
)
```

### 步骤 3：编写实验循环

```python
@experiment()
async def run_experiment(row):
    response = rag_client.query(row["query"])
    score = my_metric.score(
        llm=llm,
        response=response.get("answer", " "),
        grading_notes=row["grading_notes"]
    )
    experiment_view = {
        **row,
        "response": response.get("answer", ""),
        "score": score.value,
        "log_file": response.get("logs", " "),
    }
    return experiment_view
```

### 步骤 4：运行评估

```bash
export OPENAI_API_KEY="your_openai_api_key"
python -m ragas_examples.rag_eval.evals
```

结果保存在 `experiments/experiment_name.csv`。

---

## 六、面试要点

### 常见问题

**Q: Ragas 的核心设计理念是什么？**
A: 用实验驱动（Experiment-driven）替代人工抽查，用 LLM-based metrics 替代传统 NLP 指标。

**Q: Ragas 中 Experiment 和 Metric 的关系？**
A: Experiment 定义评估流程（加载数据→运行系统→收集结果），Metric 定义评分标准。两者可组合使用。

**Q: 最常用的 RAG 评估指标有哪些？**
A: Faithfulness（忠实度）、Context Precision（上下文精确率）、Context Recall（上下文召回率）、Answer Relevancy（回答相关性）。

**Q: 如何创建自定义指标？**
A: 用 `DiscreteMetric` 或 `ContinuousMetric`，传入自定义 prompt 和可选 allowed_values。

---

## 七、要点整理

| 概念 | 核心要点 |
|------|---------|
| **安装** | `pip install ragas`，或 `uvx ragas quickstart` 一键创建项目 |
| **项目结构** | rag.py（应用）+ evals.py（评估）+ evals/datasets（测试数据）+ evals/experiments（结果）|
| **Experiment** | `@experiment()` 装饰器定义评估流程，`.arun(dataset)` 执行 |
| **Metric** | 离散型（DiscreteMetric）或连续型，LLM-based 或非 LLM（BLEU/ROUGE）|
| **RAG 关键指标** | Faithfulness, Context Precision, Context Recall |
| **Agent 关键指标** | Tool Call Accuracy, Agent Goal Accuracy, Topic Adherence |
| **结果管理** | CSV 自动保存，建议记录 experiment_name + git_commit + model_version |

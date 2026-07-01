# 第六章 RAG系统评估 - 学习笔记

> 对应课程：[[all-in-rag/课程/chapter6|📖 第六章 RAG系统评估]]

---

## 练习题

### 基础题

1. 为什么要对 RAG 系统进行系统化评估？评估的意义是什么？
   *(留白区——在此写下你的答案)*

2. RAG 系统的评估可以分为哪三个主要维度？
   *(留白区——在此写下你的答案)*

3. 什么是 Hit Rate（命中率）？什么是 MRR（平均倒数排名）？
   *(留白区——在此写下你的答案)*

4. 什么是 Faithfulness（忠实度）？为什么它是 RAG 评估的关键指标？
   *(留白区——在此写下你的答案)*

5. 请列举至少 3 种常用的 RAG 评估工具或框架。
   *(留白区——在此写下你的答案)*

### 进阶题

1. RAGAS 评估框架包含哪些核心指标？请解释每个指标的含义和计算方式。
   *(留白区——在此写下你的答案)*

2. 检索阶段的评估指标和生成阶段的评估指标如何协同工作？完整评估 RAG 系统的策略是什么？
   *(留白区——在此写下你的答案)*

3. 在线评估和离线评估的区别是什么？在 RAG 系统中如何设计一套完整的评估体系？
   *(留白区——在此写下你的答案)*

### 编程/实践题

1. 使用 RAGAS 框架对一个简单的 RAG 系统进行评估，计算其 Context Precision、Faithfulness 和 Answer Relevancy 指标。
   *(留白区——在此写下你的代码)*

---

## 大厂面试题精选

### 题目 1（阿里巴巴）
如何全面地评估一个 RAG 系统的性能？请分别从检索和生成两个阶段提出评估指标。
**考察点：** RAG 评估体系理解
   *(留白区——写出你的思路和解答)*

### 题目 2（字节跳动）
RAG 系统的自动化评估和人工评估如何配合？在实际项目中你如何做评估？
**考察点：** 评估工程化实践
   *(留白区——写出你的思路和解答)*

---

## 要点整理

### 1. 评估的三个维度
| 维度 | 说明 | 核心指标 |
|------|------|----------|
| **检索质量** | 评估检索到的文档是否相关和完整 | Hit Rate, MRR, Recall@K, Precision@K |
| **生成质量** | 评估生成的答案是否准确和忠实 | Faithfulness, Answer Relevancy |
| **端到端质量** | 评估整个系统的用户体验 | ROUGE-L, BLEU, 人工评分 |

### 2. 核心评估指标

#### 检索阶段
| 指标 | 含义 |
|------|------|
| **Hit Rate@K** | Top-K 结果中是否包含正确答案 |
| **MRR** | 第一个正确答案的排名倒数均值 |
| **Recall@K** | Top-K 中召回的相关文档比例 |
| **Precision@K** | Top-K 中相关文档的比例 |

#### 生成阶段
| 指标 | 含义 |
|------|------|
| **Faithfulness** | 答案是否忠实于检索上下文，没编造 |
| **Answer Relevancy** | 答案是否与问题相关 |
| **Context Relevancy** | 检索上下文是否精炼、不冗余 |
| **Aspect Critique** | 多维度评分（有用性、安全性等） |

### 3. RAGAS 框架核心指标
- **Context Precision**：检索到的上下文中，与答案相关的比例
- **Context Recall**：正确答案需要的信息是否都出现在检索结果中
- **Faithfulness**：答案中的每个声明是否都可从检索上下文推导出来
- **Answer Relevancy**：答案与问题的相关性
- **Answer Correctness**：答案与真实答案的一致程度

### 4. 评估策略
| 方式 | 特点 | 适用场景 |
|------|------|----------|
| **离线评估** | 使用测试集批量评估，可自动化 | 模型迭代、版本对比 |
| **在线评估** | 用户真实反馈收集 | 生产环境监控 |
| **LLM-as-Judge** | 用 LLM 进行自动评分 | 大规模评估 |
| **人工评估** | 人工标注和评分 | 小规模高精度评估 |

---

## 参考答案汇总

> ⚠️ 先自己作答，再对照检查

### 基础题答案

1. 系统化评估可以量化 RAG 系统的性能表现，发现检索和生成环节的问题，指导优化方向，确保系统达到生产环境的质量要求。

2. 检索质量、生成质量、端到端质量（或称为检索评估、生成评估、综合评估）。

3. **Hit Rate**：检索出的 Top-K 结果中是否包含正确答案的比率。**MRR**：对于多个查询，计算第一个正确答案在检索结果中的排名的倒数，再取平均。

4. **Faithfulness** 衡量 LLM 的答案是否忠实于检索到的上下文，不包含上下文之外的信息。它是关键指标，直接反映 RAG "基于检索生成"的核心价值。

5. RAGAS、TruLens、LangSmith、DeepEval、Phoenix（Arize）。

### 进阶题参考答案

1. **Context Precision**：计算检索结果中与答案相关的文档比例。**Context Recall**：正确答案所需信息被检索到的比例。**Faithfulness**：逐一检查答案声明是否能从上下文推导。**Answer Relevancy**：答案与问题的语义相关性。**Answer Correctness**：答案与标准答案的匹配度（结合准确性和忠实度）。

2. 检索和生成评估是互补的：检索质量影响生成质量的上限。完整评估策略：先用召回率/MRR 评估检索是否找对了内容，再用 Faithfulness 评估 LLM 是否忠实使用这些内容，最后用端到端指标（ROUGE/BLEU/人工）评估整体效果。

3. **离线评估**：用预标注的测试集跑指标，可自动化、可重复，适合开发迭代阶段。**在线评估**：收集真实用户的反馈（点赞/点踩/满意度评分），适合生产环境。完整体系：离线跑自动化指标 + 上线后收集在线反馈 + LLM-as-Judge 持续监控。

### 编程题参考实现

```python
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision
from datasets import Dataset

# 准备评估数据
data = {
    "question": ["什么是RAG？"],
    "answer": ["RAG是检索增强生成技术..."],
    "contexts": [["RAG（Retrieval-Augmented Generation）是一种..."], 
                 ["检索增强生成的核心是..."]],
}
dataset = Dataset.from_dict(data)

# 计算指标
result = evaluate(
    dataset,
    metrics=[context_precision, faithfulness, answer_relevancy]
)

print(f"Context Precision: {result['context_precision']:.2f}")
print(f"Faithfulness: {result['faithfulness']:.2f}")
print(f"Answer Relevancy: {result['answer_relevancy']:.2f}")
```

### 大厂面试题参考解答

**题目 1（阿里巴巴）：**
检索阶段：Hit Rate@K、MRR、Recall@K（看找没找到对的内容）。
生成阶段：Faithfulness（看有没有编造）、Answer Relevancy（答案是否相关）、Answer Correctness（答案是否正确）。
端到端：ROUGE-L、BLEU 与标准答案对比。
推荐用 RAGAS 框架一站式评估，结合 LLM-as-Judge 自动化打分。

**题目 2（字节跳动）：**
自动化评估用 RAGAS/LangSmith 跑指标，覆盖检索和生成阶段，每天/每次发布时自动运行。人工评估定期抽检（每周100-200条），重点评估模糊边界案例。LLM-as-Judge 作为中介层：先让 LLM 评分，对低分样本进行人工审核。生产环境同时收集用户反馈（埋点/满意度评分）。

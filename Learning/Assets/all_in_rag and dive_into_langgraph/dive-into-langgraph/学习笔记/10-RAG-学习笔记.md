# RAG - 学习笔记

> 对应课程：[[10-RAG|📖 第10章 RAG]]

---

## 练习题

### 基础题

1. RAG 的全称是什么？它主要解决大模型的哪些问题？




2. RAG 的提示词模板（Prompt Template）通常包含哪两个核心占位符？各代表什么含义？




3. 什么是 Embedding？Embedding 在多语言场景下有什么优势？




4. 向量检索的基本原理是什么？如何计算两个文本之间的语义相似度？




5. 简述工程化向量检索的标准流程（至少包含 5 个步骤）。




6. BM25 是什么算法？它在 RAG 中的作用是什么？




### 进阶题

1. 什么是混合检索（Hybrid Search）？为什么工业界的 RAG 系统通常采用"向量检索 + 关键词检索"的混合方案？




2. 比较 RAG 的三种主流架构（2-Step RAG、Agentic RAG、Hybrid RAG），它们各自解决了什么问题？在什么场景下应该选择哪种架构？




3. 什么是 RRF（Reciprocal Rank Fusion）分数？它是如何计算和使用的？与 Agentic Hybrid Search（用 LLM 做重排）相比，各自的优缺点是什么？




4. RAG 系统中如何评估检索质量？有哪些常用指标？




### 编程/实践题

1. 实现一个基于 Agentic RAG 的智能问答系统：
   - 使用 `WebBaseLoader` 加载网页内容
   - 使用 `RecursiveCharacterTextSplitter` 分割文档
   - 使用向量存储（InMemoryVectorStore）存储文档 Embedding
   - 创建一个检索工具，Agent 自主决定何时调用检索
   - 包含混合检索（向量检索 + BM25）和 RRF 重排

```python
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain.tools import tool
from langchain.agents import create_agent

# 请在这里完成代码

```

---

## 大厂面试题精选

1. **RAG 与微调（Fine-tuning）的区别是什么？什么场景应该选择 RAG？**（AI 算法岗）
   - 来源：腾讯云/字节跳动面试高频题
   - 解析：RAG 是"查资料再回答"，微调是"背下来再回答"。RAG 成本低、可插拔、可溯源；微调适合需要改变模型语感或输出格式的场景。

2. **RAG 系统中如何解决幻觉（Hallucination）问题？**（大模型应用岗）
   - 来源：多家大厂面试必问题
   - 解析：从 Prompt 约束、检索质量（重排序）、引用溯源（Citation）、知识图谱交叉验证等多维度入手。

3. **向量检索和 BM25 关键词检索各自的优缺点是什么？为什么需要混合检索？**（搜索推荐岗）
   - 来源：百度/Google 面试题
   - 解析：向量检索擅长语义匹配但可能遗漏精确关键词，BM25 精确匹配但无法处理同义词。混合检索实现优势互补。

4. **Agentic RAG 和传统 2-Step RAG 有什么区别？**（AI 架构师岗）
   - 来源：2025-2026 年新兴面试题
   - 解析：2-Step RAG 固定流程"检索→生成"；Agentic RAG 中 Agent 自主判断是否需要检索、检索什么、检索几次，更加灵活智能。

5. **你如何评估和优化 RAG 系统的检索质量？**（AI 工程化岗）
   - 来源：RAG 系统面试核心题
   - 解析：三步法——查切块策略（语义切块 vs 固定字数）、换检索方式（混合检索）、加重排序（Cross-Encoder 精排）。

---

## 要点整理

### RAG 核心概念

| 概念 | 说明 |
|------|------|
| **RAG** | Retrieval-Augmented Generation，检索增强生成 |
| **作用** | 让大模型"打小抄"——先查资料再回答 |
| **优势** | 有据可依、减少幻觉、知识可更新 |
| **代价** | 需要构建和维护知识库 |

### 检索方式对比

| 检索方式 | 原理 | 优点 | 缺点 |
|---------|------|------|------|
| **向量检索（Dense）** | Embedding 语义匹配 | 理解同义词、语义改写 | 可能遗漏精确关键词 |
| **关键词检索（Sparse/BM25）** | 词频统计 | 精确匹配能力强 | 无法处理同义词 |
| **混合检索（Hybrid）** | 两路召回 + RRF 融合 | 优势互补 | 系统复杂度增加 |

### RAG 三种架构

| 架构 | 流程 | 适用场景 |
|------|------|---------|
| **2-Step RAG** | 用户问题 → 检索 → 生成 | 简单问答，固定流程 |
| **Agentic RAG** | Agent 自主判断检索时机和方式 | 复杂推理，需要多步决策 |
| **Hybrid RAG** | Agentic RAG + Query 改写 + 相关性确认 | 企业级复杂应用 |

### 工程化向量检索流程

```
Sources → Document Loaders → Documents → Split into chunks
→ Turn into embeddings → Vector Store → Retrieval → LLM → Answer
```

### 核心组件及可替换方案

| 组件 | 可选方案 |
|------|---------|
| **Document Loader** | TextLoader, PyMuPDFLoader, WebBaseLoader |
| **Document Splitter** | RecursiveCharacterTextSplitter |
| **Embedding 模型** | DashScopeEmbeddings, HuggingFaceEmbeddings |
| **Vector Store** | Chroma, Milvus, FAISS, InMemoryVectorStore |
| **Retriever** | EnsembleRetriever, BM25Retriever |
| **LLM** | ChatOpenAI, ChatGLM, Qwen |

---

## 参考答案汇总

### 基础题答案

1. RAG 全称 **Retrieval-Augmented Generation（检索增强生成）**。它主要解决大模型的两个问题：（1）**实时性不足**——训练数据有截止日期，之后的事不知道；（2）**专业性欠缺**——参数量有限，无法容纳所有专业知识。

2. RAG 提示词模板通常包含两个占位符：`{context}`（召回的上下文文本）和 `{question}`（用户问题）。

3. **Embedding** 是一种将文本转为向量的技术，输入文本、输出定长向量。其目的是把语义相近的词分配到同一片向量空间。在多语言场景下，经过充分训练的 Embedding 模型会将多语言内容在语义层面对齐，使一个向量在多语言环境中保持同一语义。

4. **向量检索原理**：将用户问题和知识库内容都转为 Embedding 向量，然后计算向量之间的距离（如余弦相似度）。距离越小，语义相似度越高。返回 Top-K 个最相似的文档。

5. 工程化向量检索标准流程：
   （1）使用 Document Loader 加载文档
   （2）使用 Splitter 分割文档为 Chunks
   （3）使用 Embedding 模型生成向量
   （4）存入 Vector Store
   （5）用户查询时转为 Query Embedding
   （6）在 Vector Store 中检索相似向量
   （7）将检索结果注入 LLM 生成答案

6. **BM25**（Best Matching 25）是一种基于词频的排序算法，用于估计文档与查询的相关性。在 RAG 中作为关键词检索器使用，适合精确匹配场景。

### 进阶题参考答案

1. **混合检索**：同时使用向量检索（稠密检索）和关键词检索（稀疏检索）两路召回，然后通过 RRF 等算法融合结果。向量检索擅长语义匹配但可能漏掉精确关键词，BM25 正好相反。两者互补使召回结果更全面、更准确。

2. **2-Step RAG**：固定流程，先检索再生成，简单高效，适合知识库稳定、问题类型固定的场景。**Agentic RAG**：Agent 自主控制检索流程，可多轮检索、根据需要决定是否检索，适合复杂推理和多步问答。**Hybrid RAG**：在 Agentic RAG 基础上增加 Query 改写、结果验证等步骤，适合企业级高要求场景。

3. **RRF 分数**：`RRF = Σ w_i / (k + r_i)`，其中 w_i 是检索器权重，k 是平滑参数（默认 60），r_i 是文档在检索器中的排名。优点是不依赖原始得分、鲁棒性强。Agentic Hybrid Search 用 LLM 做重排，更灵活但成本高、速度慢。RRF 适合批量自动化处理，LLM 重排适合对精度要求极高的场景。

4. **检索质量评估指标**：Hit Rate（命中率）、MRR（平均倒数排名）、Precision（精确率）、Recall（召回率）。生成质量评估：Faithfulness（忠实度）、ROUGE-L（与标准答案相似度）。可使用 RAGAS 框架做自动化评估。

### 编程题参考实现

```python
# 1. 加载文档
loader = WebBaseLoader(web_paths=("https://example.com/article",))
docs = loader.load()

# 2. 分割文档
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(docs)

# 3. 向量生成和存储
embeddings = DashScopeEmbeddings()
vector_store = InMemoryVectorStore(embedding=embeddings)
vector_store.add_documents(splits)

# 4. 创建检索工具
@tool(response_format="content_and_artifact")
def retrieve_context(query: str):
    """Retrieve relevant context for the query."""
    retrieved = vector_store.similarity_search(query, k=3)
    serialized = "\n\n".join(
        f"Source: {doc.metadata}\nContent: {doc.page_content}"
        for doc in retrieved
    )
    return serialized, retrieved

# 5. 创建 Agentic RAG Agent
agent = create_agent(
    model=llm,
    tools=[retrieve_context],
    system_prompt="You have access to a retrieval tool. Use it when you need external information."
)

# 6. 调用
response = agent.invoke({
    "messages": [{"role": "user", "content": "用户问题"}]
})
```

### 大厂面试题参考解答

1. **RAG vs 微调**：微调把知识固化进模型参数，更新成本高；RAG 知识外挂在向量库，插拔方便。做项目通常 RAG-First，先跑通验证想法，如果语感或输出格式不达标才考虑微调打补丁。

2. **解决幻觉**：第一道防线是 Prompt 约束（没答案就说不知道）；第二道是检索端加重排序（确保进上下文的文档高相关高置信）；第三道是引用溯源（强制 Citation）；第四道是高容错领域引入知识图谱做交叉验证。

3. **向量检索 vs BM25**：向量检索通过 Embedding 理解语义，能处理"苹果公司"和"Apple Inc."的同义关系；BM25 精确匹配专有名词（如"ERR_CONN_RESET_4XX"）。混合检索让两者互补，Hit Rate 可提升 10-30%。

4. **Agentic RAG vs 2-Step RAG**：2-Step RAG 是固定的一次检索，Agentic RAG 中 Agent 可以自主决定"检索什么、检索几次、是否继续检索"。Agentic RAG 更灵活但更复杂，适合需要多步推理的场景。

5. **检索质量优化三步法**：一查切块策略（语义切块避免关键信息被腰斩），二上混合检索（向量+BM25 双路召回），三加 Rerank 精排（用 Cross-Encoder 模型对召回结果重排序）。

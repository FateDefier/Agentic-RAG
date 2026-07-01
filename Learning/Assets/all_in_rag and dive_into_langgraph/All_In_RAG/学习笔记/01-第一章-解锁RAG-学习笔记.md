# 第一章 解锁RAG - 学习笔记

> 对应课程：[[all-in-rag/课程/chapter1|📖 第一章 解锁RAG]]

![[图1.1 RAG分类.png]]
这张图非常全面地展示了检索增强生成（RAG）技术的演进过程，从最基础的“朴素 RAG”到“进阶 RAG”，再到现在最复杂的“模块化 RAG”架构。
### 1. 总体演进与图例（左下角）
*   **图例说明**：
    *   **黑色实线框 (Key Module)**：RAG 中的核心基础模块（如索引、检索、生成）。
    *   **蓝色实线框 (New Module)**：在进阶或模块化 RAG 中新增的模块。
    *   **橙色菱形 (Process Control)**：流程控制节点，用于判断和分支。
*   **演进路线**：底部三个相交的圆展示了 RAG 的发展阶段：
    *   **Naive（朴素）**：最基础的链路。
    *   **Advance（进阶）**：增加了预处理和后处理。
    *   **Modular（模块化）**：高度解耦，每个环节都可以进行定制和组合。

---

### 2. Naive RAG（朴素 RAG - 左上角）
这是最基础的 RAG 流程，只有三个步骤：
*   **Indexing（索引）**：将文档切片并建立向量索引。
*   **Retrieval（检索）**：根据用户问题，从索引中检索出相关的文档片段（Chunks）。
*   **Generation（生成）**：将检索到的片段和用户问题一起输入大模型，生成最终答案。

---

### 3. Advanced RAG（进阶 RAG - 中上部）
在朴素 RAG 的基础上，增加了前后处理环节：
*   **Indexing（索引）**：同朴素 RAG。
*   **Pre-Retrieval（检索前）**：在检索之前对用户提问进行优化。
    *   *Query Rewrite（查询重写）*：改写用户的问题。
    *   *HyDE（假设性文档嵌入）*：先生成一个假设性的答案，再用这个答案去检索，提高召回率。
*   **Retrieval（检索）**：同朴素 RAG。
*   **Post-Retrieval（检索后）**：对检索回来的内容进行处理。
    *   *Rerank（重排序）*：对检索到的多个片段按相关性重新排序。
    *   *Filter（过滤）*：过滤掉无关或质量低的片段。

---

### 4. Modular RAG（模块化 RAG - 右侧大图）
这是目前最前沿的架构，将 RAG 的各个环节分解成独立的、可互换的模块。主要分为以下几个阶段：

#### A. Indexing（索引阶段）
*   **Chunk Optimization（分块优化）**：
    *   *Retrieve Smaller Chunk, Use Parent Large Chunk Context*：检索细粒度的小块，但向 LLM 提供其所属的较大的父块上下文。
    *   *Single Sentence / Big 2*：根据句子粒度或更大的块进行切分。
*   **Structural Organization（结构化组织）**：
    *   将文档按层级结构化（如章节、段落、句子）。
    *   **Knowledge Graph（知识图谱）**：提取实体和关系，构建图结构，支持语义关系检索。

#### B. Pre-Retrieval（检索前阶段）
*   **Query Transformation（查询转换）**：
    *   *HyDE*：生成假设文档。
    *   *Hypothetical Answer*：生成假设答案。
    *   *Query Rewrite*：改写查询。
*   **Query Expansion（查询扩展）**：
    *   *Sub-Query*：将复杂问题拆分为多个子问题分别检索。
    *   *Verification Chain*：通过验证链，让检索更加精准。
*   **Query Construction（查询构建）**：将自然语言问题转化为数据库查询语言。
    *   *Text-to-Cypher*：转为图数据库查询语言。
    *   *Text-to-SQL*：转为关系型数据库查询语言。

#### C. Retrieval（检索阶段）
*   **Retriever FT（检索器微调）**：
    *   利用外部知识，通过“正样本对”和“负样本对”对检索模型进行微调。
*   **Retriever Source（检索源）**：
    *   不仅限于文本块，还可以检索句子、实体、三元组（Subject-Predicate-Object）或子图。
*   **Retriever Selection（检索器选择）**：
    *   根据情况选择不同的检索方法，如：Embedding（向量检索）、Keyword（关键词检索）、Hybrid Retrieval（混合检索）。

#### D. Post-Retrieval（检索后阶段）
*   **Rerank（重排序）**：使用多类型文档重排序（如代码、表格、文本混排）。
*   **Compression（压缩）**：
    *   对检索到的大量信息进行压缩，提取最核心的内容（如使用 LongLLMLingua）。
    *   使用 LLM 选择核心 Chunk。

#### E. Generation（生成阶段）
*   **Generator FT（生成器微调）**：
    *   将检索器与大模型结合，或引入外部知识进行微调。
*   **Verification（验证）**（图表右下角）：
    *   对生成的答案进行多维度验证，包括：
        *   **Knowledge with KG**：用知识图谱验证事实。
        *   **Review Model**：用另一个模型审核。
        *   **Privacy Detection**：检测是否有隐私泄露。
    *   经过验证后，输出结果可能分为：**Output Answer（输出答案）**、**Do RAG Again（重新 RAG）**、**Refuse to Answer（拒绝回答）**。

#### F. Orchestration（编排层 - 底部蓝框）
这是整个模块化 RAG 的“大脑”，负责调度和控制：
*   **Routing（路由）**：根据语义分析，判断用户问题应该走哪条处理管道（Pipeline 1: Hard Prompt 纯靠检索内容；还是 Pipeline 2: Soft Prompt 允许 LLM 用自身知识）。
*   **Scheduling（调度）**：动态判断流程。
    *   例如：Query -> Judge（判断是否需要检索）-> Generate（如不需要，直接生成） -> 再次 Judge -> 输出。若需要检索则执行检索动作。
*   **Knowledge Guide（知识引导）**：
    *   结合知识图谱进行规划。
    *   将复杂的 Query 转化为 Reasoning Path（推理路径） -> 根据路径分配 Schedule -> 执行 Retrieve -> 生成。

---

## 练习题

### 基础题

1. RAG 的全称是什么？它的核心设计思想是什么？
   Retrieval-Augment-Generate，核心设计思想：引入外部知识库，让大模型结合内部知识和外部知识回答提示词的要求

2. RAG 的双阶段架构包括哪两个阶段？请简要描述每个阶段的主要功能。
   两个阶段：
1 检索：在向量知识库中检索相关内容并返回给大语言模型
2 生成：大模型根据检索的到的外部知识和模型权重中的内部知识回答提示词中的要求/问题

3. RAG 技术演进分为哪三个主要阶段？请列出每个阶段的名称。
   Naive RAG —> Advanced RAG —> Moduled RAG
   基础 RAG —> 高级 RAG —> 模块化 RAG

4. 在 LLM 优化技术选型中，通常推荐的优先级顺序是什么？
   Prompt Engineering > RAG > Fine-Tuning

5. RAG 相比纯 LLM（大语言模型）有哪些关键优势？（列举至少 3 点）
- 隐私化，可本地部署
- 可实时人为更新数据，解决知识时滞问题
- 可人为注入特定垂直领域知识，增强模型在特定领域的性能

6. 什么是"参数化知识"和"非参数化知识"？在 RAG 中它们分别对应什么？
- 参数化知识：大模型可以直接检索查看的数据，包括向量知识、Markdown 和 JSON 之类的数据
- 非参数化知识：供人为查看，但大模型看不懂的需要转化的知识，类似 PDF 和 Word 之类的数据

### 进阶题

1. 为什么说 RAG 是"开卷考试"？请从技术角度分析 RAG 如何解决 LLM 的幻觉问题。
-  原因：RAG 本质就是给大模型加一个外部知识库，相当于大模型在外部向量知识库中检索答案然后汇总并结合内部知识输出，这就类似“开卷考试”
-  技术角度：大模型幻觉本质就是大模型在回答没有见过的问题，内部没有相应问题的知识，就会“胡编乱造”的问题；而 RAG 就是大模型可以检索的知识库，这就让回答必有其源，每句回答都是根据人为加入的 RAG 数据库回答的，从而解决了幻觉问题，当然，这也可能“带偏”大模型

3. 对比 Naive RAG、Advanced RAG 和 Modular RAG 三种架构，分析它们在流程、关键技术和局限性方面的区别。
   - Naive RAG：流程：离线：索引；在线：检索 + 生成；关键技术：；局限性：
   - Advanced RAG：在上述检索前后加上 `pre-retrieval` 和 `post-retrieval`，关键技术：；局限性
   - Module RAG：路由(`Routing`) —> ；关键技术：；局限性：

4. 在什么场景下应该选择"提示词工程 → RAG → 微调"的技术路径？请结合实际应用场景分析三者的适用边界。
   - Prompt Engineering：难以找到相关领域的知识不能进行 RAG，没有优良的硬件环境不能进行微调，简单的日常提问
   - RAG：拥有特定领域的大量知识，且知识更新迭代快的场景
   - Fine-Tuning：硬件条件充分，该模型只用于特定领域的场景

### 编程/实践题

1. 使用 LangChain 或 LlamaIndex 框架，实现一个简单的 RAG 流程：加载本地 Markdown 文档 → 文本分块 → 使用嵌入模型生成向量 → 向量检索 → LLM 生成回答。
   *(留白区——在此写下你的代码)*

---

## 大厂面试题精选

**来源：** 互联网搜索整理

### 题目 1（字节跳动）
请详细解释 RAG 的工作原理，并说明它和微调（Fine-tuning）的主要区别。在实际项目中你会如何选择？
**考察点：** 对 RAG 本质的理解，技术选型能力
   *(留白区——写出你的思路和解答)*

### 题目 2（阿里巴巴）
RAG 系统的评估指标有哪些？分别从检索阶段和生成阶段说明。
**考察点：** RAG 评估体系的理解
   *(留白区——写出你的思路和解答)*

### 题目 3（腾讯）
请解释 Naive RAG → Advanced RAG → Modular RAG 的演进过程，并说明 Advanced RAG 在 Naive RAG 基础上增加了哪些优化步骤？
**考察点：** RAG 技术演进的理解深度
   *(留白区——写出你的思路和解答)*

### 题目 4（百度）
RAG 如何解决 LLM 的知识静态性和幻觉问题？RAG 的"可溯源性"具体指什么？
**考察点：** RAG 核心价值理解
   *(留白区——写出你的思路和解答)*

---

## 要点整理

### 1. RAG 核心概念
- **定义**：检索增强生成（Retrieval-Augmented Generation），让 LLM 在生成前先从外部知识库检索相关信息
- **本质**：将参数化知识（模型权重中的记忆）与非参数化知识（外部可检索知识库）相结合
- **一句话**：让 LLM 学会"开卷考试"

### 2. RAG 双阶段架构
| 阶段 | 功能 | 关键组件 |
|------|------|----------|
| **检索阶段** | 知识向量化 + 语义召回 | 嵌入模型（Embedding Model）、向量数据库 |
| **生成阶段** | 上下文整合 + 指令引导生成 | LLM、Prompt 模板 |

### 3. RAG 技术演进
| 阶段 | 流程 | 特点 | 关键技术 | 局限性 |
|------|------|------|----------|--------|
| **Naive RAG** | 索引 → 检索 → 生成 | 基础线性流程 | 基础向量检索 | 效果不稳定 |
| **Advanced RAG** | 检索前/后优化 | 增加优化步骤 | 查询重写、结果重排 | 流程相对固定 |
| **Modular RAG** | 积木式可编排 | 模块化、可组合 | 动态路由、查询转换、多路融合 | 系统复杂性高 |

### 4. 技术选型路径
**提示词工程 → RAG → 微调**
- 提示词工程：任务简单、模型已有相关知识
- RAG：模型缺乏特定或实时知识
- 微调：改变模型行为/风格/格式

### 5. RAG 关键优势
- ✅ 准确性与可信度提升（抑制幻觉、可溯源）
- ✅ 时效性保障（索引热拔插、动态更新）
- ✅ 综合成本效益（避免高频微调、可用小模型）
- ✅ 模块化可扩展性（多源集成、检索与生成解耦）

### 6. 适用场景风险分级
- 低风险（翻译/语法检查）：高可靠性
- 中风险（合同起草/法律咨询）：需要人工复核
- 高风险（医疗诊断）：仅作辅助参考

---

## 参考答案汇总

> ⚠️ 先自己作答，再对照检查

### 基础题答案

1. **RAG = Retrieval-Augmented Generation（检索增强生成）**。核心设计思想是将模型内部参数化知识与外部知识库的非参数化知识相结合，在 LLM 生成文本前先通过检索机制从外部知识库获取相关信息，提升输出的准确性和时效性。

2. **检索阶段**：嵌入模型将知识库编码为向量索引存入向量数据库，用户查询向量化后通过相似度搜索找到相关文档片段。**生成阶段**：生成模块接收检索到的文档片段和用户问题，按 Prompt 指令引导 LLM 生成答案。

3. **初级 RAG（Naive RAG）→ 高级 RAG（Advanced RAG）→ 模块化 RAG（Modular RAG）**。

4. **提示词工程（Prompt Engineering）→ RAG → 微调（Fine-tuning）**。

5. （1）准确性与可信度提升（抑制幻觉、可溯源）；（2）时效性保障（动态更新知识）；（3）综合成本效益（避免高频微调）；（4）模块化可扩展性。

6. **参数化知识**：存储在 LLM 模型权重中的固化知识，对应模型内部学到的"记忆"。**非参数化知识**：存储在外部知识库中的精准、可随时更新的外部数据，对应 RAG 检索到的文档片段。

### 进阶题参考答案

1. **RAG 作为"开卷考试"**：传统 LLM 像闭卷考试，完全依赖训练时记住的知识。RAG 让模型在作答前可以先"查资料"（检索外部知识库）。解决幻觉的机制：LLM 的幻觉源于其"自信地编造"不知道的信息，RAG 通过提供具体的参考材料，将生成过程约束在检索到的文档范围内，减少了模型"自由发挥"的空间。当检索到的上下文包含正确答案时，LLM 更倾向于基于这些信息生成，而非凭空想象。

2. 三种架构对比详见要点整理第 3 点表格。

3. **提示词工程**：适用于简单任务，如翻译、分类等，模型已有足够知识，只需指导输出格式。**RAG**：适用于需要外部知识或实时信息的场景，如企业知识库问答、最新新闻查询。**微调**：适用于需要改变模型行为/风格的场景，如让模型学会特定输出格式、模仿特定对话风格。实际项目通常 RAG-First，先跑通再考虑微调。

### 编程题参考实现

```python
# 基于 LangChain 的简单 RAG 流程
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_community.llms import OpenAI  # 或其他 LLM

# 1. 加载文档
loader = TextLoader("path/to/document.md")
documents = loader.load()

# 2. 文本分块
text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = text_splitter.split_documents(documents)

# 3. 嵌入 + 向量存储
embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-zh-v1.5")
vectorstore = Chroma.from_documents(chunks, embeddings)

# 4. 创建检索链
qa_chain = RetrievalQA.from_chain_type(
    llm=OpenAI(),  # 使用实际 API Key
    retriever=vectorstore.as_retriever(search_kwargs={"k": 3})
)

# 5. 问答
response = qa_chain.invoke("你的问题")
print(response)
```

### 大厂面试题参考解答

**题目 1（字节跳动）：**
RAG 工作原理：用户查询 → 向量化 → 从向量库检索相关文档 → 查询+文档作为上下文送给 LLM → LLM 生成基于检索内容的答案。
与微调区别：微调修改模型参数（闭卷），RAG 不修改参数（开卷）。RAG 优势：知识更新成本低、可溯源、适合知识密集型任务。微调优势：改变模型行为/风格。项目选择：知识问答类首选 RAG，风格/格式类考虑微调，通常 RAG-First 策略。

**题目 2（阿里巴巴）：**
检索阶段指标：Hit Rate（命中率）、MRR（平均倒数排名）、Recall@K。
生成阶段指标：Faithfulness（忠实度，是否基于检索内容）、Answer Relevance（答案相关性）、Context Relevance（上下文相关性）。
端到端指标：ROUGE-L、BLEU、人工评估。
工具：RAGAS 框架可自动化评估。

**题目 3（腾讯）：**
Naive RAG：线性流程 索引→检索→生成，效果不稳定。
Advanced RAG：增加检索前优化（查询重写）和检索后优化（结果重排、Rerank）。
Modular RAG：模块化编排，支持动态路由、查询转换、多路融合、自适应检索。

**题目 4（百度）：**
知识静态性：RAG 通过实时检索外部知识库解决，知识库可动态更新。
幻觉问题：RAG 基于检索到的具体文档生成，减少模型凭空编造的空间。
可溯源性：RAG 的每一条回答都可追溯到具体的原始文档出处，提高可信度。

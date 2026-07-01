# 安装依赖：pip install langchain langchain-text-splitters langchain-deepseek langchain-huggingface transformers torch bs4 requests ipykernel

# ============================================
# 第一部分：导入相关模块
# ============================================
import os                                                               # 环境变量
# 设置 Hugging Face 镜像（必须在任何 huggingface 导入之前）
os.environ["HF_ENDPOINT"]="https://hf-mirror.com"
import bs4                                                              # 解析 HTML
import requests                                                         # 发送 HTTP 请求，获取网页内容
from langchain_text_splitters import RecursiveCharacterTextSplitter     # 文本分割 -- 递归字符分割
from langchain_huggingface import HuggingFaceEmbeddings                 # 加载嵌入模型
from langchain_core.documents import Document                           # 文档对象
from langchain_core.vectorstores import InMemoryVectorStore             # 内存向量数据库
from langchain_core.prompts import ChatPromptTemplate                   # 构建聊天提示模板
from langchain_core.runnables import RunnablePassthrough                # 透传/直通组件
from langchain_core.output_parsers import StrOutputParser               # 字符串输出解析器
from langchain_deepseek import ChatDeepSeek                             # DeepSeek 大模型的 LangChain 封装
from dotenv import load_dotenv                                          # 加载环境变量

# ============================================
# 第二部分：Indexing（索引阶段）- Load 加载文档
# ============================================
def load_web_page(url: str, bs_kwargs: dict | None = None) -> list[Document]:
    """
    加载网页并解析为 Document 列表
    :param url: 目标网页 URL
    :param bs_kwargs: BeautifulSoup 解析参数
    :return: Document 对象列表（通常一个网页对应一个 Document）
    """
    # 发送 HTTP GET 请求获取网页 HTML，timeout=20 防止请求挂起
    response = requests.get(url, timeout=20)
    # raise_for_status()：如果响应状态码不是 200，会抛出异常（如 404, 500）
    response.raise_for_status()
    
    # 使用 BeautifulSoup 解析 HTML，**(bs_kwargs or {}) 将额外参数传入解析器
    soup = bs4.BeautifulSoup(response.text, "html.parser", **(bs_kwargs or {}))
    
    # 将解析后的纯文本内容封装为 Document 对象
    # metadata={"source": url} 记录文档来源，方便后续追溯
    return [Document(page_content=soup.get_text(), metadata={"source": url})]

# 配置 BeautifulSoup 的过滤规则：只保留掘金文章正文相关的 HTML 标签
# 掘金的文章正文通常在 article 标签或特定 class 中，这里用通用策略保留主要内容
# 过滤掉导航栏、广告、评论区等噪声内容
bs4_strainer = bs4.SoupStrainer(["article", "h1", "h2", "h3", "p", "pre"])

# 加载掘金中文博客文章：标题：8000字长文告诉你：懂这4项技能便可轻松入门深度学习
docs = load_web_page(
    "https://juejin.cn/post/6844904084571422734", 
    bs_kwargs={"parse_only": bs4_strainer}, 
)

# 验证加载结果：docs 是一个列表，每个元素是一个 Document
assert len(docs) == 1, "预期只加载到一个 Document"
print(f"1.【load】中文博客加载完成，总字符数：{len(docs[0].page_content)}")

# 调试：预览前 300 个字符
# print(f"内容预览：\n{docs[0].page_content[:300]}")

# ============================================
# 第三部分：Indexing（索引阶段）- Split 切分文档
# ============================================

# RecursiveCharacterTextSplitter: 递归字符文本切分器
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,      # 每个文本块最大 1000 个字符
    chunk_overlap=200,    # 相邻块之间重叠 200 字符，保证语义连贯，避免信息被截断
    add_start_index=True, # 记录每个 chunk 在原始文档中的起始位置，方便溯源
)

# split_document: 将 Document 列表切分为更小的 Document 列表
all_splits = text_splitter.split_documents(docs)
# 调试
print(f"2.【Split】文档切分完成，共生成 {len(all_splits)} 个子文档块")

# ============================================
# 第四部分：Indexing（索引阶段）- Embed 选择 Embedding 模型
# ============================================
# 加载 本地/远程(HuggingFace) 的 HuggingFace 嵌入模型，这里我在 .env 加入了镜像站
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-zh-v1.5",                # bge：BAAI General Embedding，small：大版本，512 维向量
    encode_kwargs={"normalize_embeddings": True},       # 对嵌入向量进行 L2 归一化，使余弦相似度等价于点积，提升检索准确性
)

# 调试
print("3.【Embed】Embedding 模型加载完成：BAAI/bge-small-zh-v1.5")

# ============================================
# 第五部分：Indexing（索引阶段）- Store 存储到向量库
# ============================================

# InMemoryVectorStore: 内存中的向量存储，适合演示/小规模数据，可换为 Chroma、Milvus、Qdrant 等持久化数据库
vector_store = InMemoryVectorStore(embeddings)

# add_documnets: 将切分后的文档块嵌入并存入向量库，返回每个文档块在向量库中的唯一 ID
document_ids = vector_store.add_documents(documents=all_splits)

# 调试
print(f"4.【Store】向量库存储完成，前 3 个文档 ID：{document_ids[:3]}")

# ============================================
# 第六部分：Retrieval（检索阶段）- 构建检索器
# ============================================
# Retriever 核心接口：invoke(query) -> list[Document]
# as_retriever() 将 VectorStore 转为 Retriever(检索器)
# search_kwargs={"k": 6}：每次检索返回最近似的 6 个文档块
retriever = vector_store.as_retriever(search_kwargs={"k": 6})
print(f"5.【Retriever】检索器构建完成，配置返回 Top-6 结果")

# ============================================
# 第七部分：Generation（生成阶段）- 构建 Prompt 模板
# ============================================
# chatPromptTemplate.from_template: 从字符串模板创建聊天提示模板
# {context} 和 {question} 是占位符，运行时会由 Chain 动态填充
# 提示词使用中文，与中文博客以及中文 Embedding 模型保持一致
template = """基于以下上下文回答问题。如果上下文中没有相关信息，请明确说明。

上下文：
{context}

问题：{question}

回答："""

prompt = ChatPromptTemplate.from_template(template)
print("6.【Prompt】提示模板构建完成")

# ============================================
# 第八部分：Generation（生成阶段）- 配置 LLM
# ============================================
# 读取当前文件夹下的 .env 文件的信息，override 参数指系统环境变量和 .env 中以 .env 文件优先（覆写）
# 这里自动加载了 DEEPSEEK_API_KEY 和 DEEPSEEK_BASE_URL 下面 llm 定义不需要手动传参
load_dotenv(override=True)

llm = ChatDeepSeek(
    model="deepseek-v4-flash",          # deepseek-chat 在 7 月 26 日后会被弃用
    temperature=0, 
    max_retries=2, 
)
print("7.【LLM】DeepSeek-V4-Flash 模型初始化完成")

# ============================================
# 第九部分：构建 RAG Chain（LCEL 表达式语言）
# ============================================
# LCEL（LangChain Expression Language）核心概念：使用 | 管道符将多个 Runnable 组件串联，数据从左向右流动
# RunnablePassthrough：透传组件，将输入原样传递到下一环节，在 RAG 中用于将用户问题透传给 prompt 的 {question} 占位符

# 步骤 1：定义辅助函数，将检索到的 Document 列表格式化为字符串
def format_docs(docs: list[Document]) -> str:
    """
    将 Document 列表拼接为单个字符串，用双换行分隔
    这是为了将多个检索结果合并为 prompt 中的 {context} 变量
    """
    return "\n\n".join(doc.page_content for doc in docs)


# 步骤 2：构建 RAG Chain
# 字典 {"context": .../ "question": ...} 构成一个隐式的 RunnableParallel（并行执行）
#   - context：将用户问题传入 retriever 检索，结果通过 format_docs 格式化
#   - question：通过 RunnablePassthrough 透传用户原始问题
rag_chain = (
    {
        "context": retriever | format_docs,         # 检索并格式化上下文
        "question": RunnablePassthrough(),          # 透传用户问题
    }
    | prompt                                        # 填充提示模板
    | llm                                           # 调用 DeepSeek 生成回答
    | StrOutputParser()                             # 解析为纯文本字符串
)

print("8.【Chain】RAG Chain 构建完成\n")

# ============================================
# 第十部分：运行 RAG 查询（中文问题）
# ============================================

# 定义要提问的问题（中文提问，与检索内容和嵌入模型相同）
question = "学习深度学习需要掌握哪些数学内容？"

# 执行流程：
# 1. RunnablePassthrough 将问题作为 question
# 2. 同事该问题也传给 retriever 进行相似度检索（bge-large-zh-v1.5 将中文问题转为向量）
# 3. 检索结果经 format_docs 合并为 context
# 4. prompt 将 context + question 合并为 context
# 5. llm 调用 API 生成回答
# 6. StrOutputPraser 从 AIMessage 中提取 content 字符串
# invoke：同步调用 Chain，传入问题字符串
answer = rag_chain.invoke(question)

print(f"DeepSeek 回答：\n{answer}")

"""
(RAG) PS D:\VSCode\Project\Agentic RAG> python '.\1. Langchain.py'
【load】中文博客加载完成，总字符数：9043
【Split】文档切分完成，共生成 14 个子文档块
Loading weights: 100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 71/71 [00:00<00:00, 5341.62it/s]
【Embed】Embedding 模型加载完成：BAAI/bge-small-zh-v1.5
【Store】向量库存储完成，前 3 个文档 ID：['d79dbbc6-25f5-4c4d-8bc7-18295346aef5', '2950762e-6cee-4d63-9831-2c3949a54743', '705eef72-1c46-4619-b512-5434bdb393b4']
{'【Retriever】检索器构建完成，配置返回 Top-6 结果'}
【Prompt】提示模板构建完成
【LLM】DeepSeek-V4-Flash 模型初始化完成
【Chain】RAG Chain 构建完成


DeepSeek 回答：
根据上下文，学习深度学习需要掌握以下数学内容：

- 高等数学（包括导数、极限、微分中值定理、泰勒公式、函数的单调性、凸优化等）
- 线性代数（研究向量，用于表示多维模型的多维参数）
- 微积分
- 概率与统计（概率论是很多机器学习算法的基础）

上下文还提到，这些知识在大学期间通常已经学过，可以在学习具体模型时重新拾起，不必从头学起。
"""

# ============================================
# 扩展：查看检索到的原始文档
# ============================================

print("\n" + "=" * 50)
print("【调试】检索到的原始文档片段：")
retrieved_docs = retriever.invoke(question)
for i, doc in enumerate(retrieved_docs, 1):
    # 显示每个检索结果的来源、起始索引和前 200 字符
    print(f"\n--- 文档 {i} ---")
    print(f"来源：{doc.metadata.get('source', 'unknown')}")
    print(f"起始位置：{doc.metadata.get('start_index', 'N/A')}")
    print(f"内容：{doc.page_content[:200]}...")
    
# ============================================
# 额外：再测试几个问题
# ============================================

test_questions = [
    "初学者学习深度学习容易踩哪些坑？",
    "深度学习和机器学习、人工智能之间是什么关系？",
    "为什么 Python 是深度学习的主流语言？",
]

print("\n" + "=" * 50)
print("【批量测试】多个中文问题：")
for q in test_questions:
    print(f"\n>>> 问题：{q}")
    ans = rag_chain.invoke(q)
    print(f">>> 回答：{ans[:200]}...")      # 只显示前 200 字符

"""
(RAG) PS D:\VSCode\Project\Agentic RAG> python '.\1. Langchain.py'                    
D:\VSCode\Project\Agentic RAG\1. Langchain.py:197: SyntaxWarning: invalid escape sequence '\V'
  (RAG) PS D:\VSCode\Project\Agentic RAG> python '.\1. Langchain.py'
1.【load】中文博客加载完成，总字符数：9043
2.【Split】文档切分完成，共生成 14 个子文档块
Loading weights: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 71/71 [00:00<00:00, 11783.62it/s]
3.【Embed】Embedding 模型加载完成：BAAI/bge-small-zh-v1.5
4.【Store】向量库存储完成，前 3 个文档 ID：['d7955160-1a7e-4d7a-b57d-9d0f8aa12a09', 'a3407541-0aaa-4c99-8758-51a435ce7139', 'f84603b4-208f-4e13-b7e0-cec9677b8d8c']
5.【Retriever】检索器构建完成，配置返回 Top-6 结果
6.【Prompt】提示模板构建完成
7.【LLM】DeepSeek-V4-Flash 模型初始化完成
8.【Chain】RAG Chain 构建完成

DeepSeek 回答：
根据上下文，学习深度学习需要掌握的数学内容包括：**高等数学**（导数、极限、微分中值定理、泰勒公式、函数的单调性、凸优化等）、**线性代数**（向量、矩阵等）、**微积分**、**概率与统计**。上下文明确提到这些是“重中之重”。

==================================================
【调试】检索到的原始文档片段：

--- 文档 1 ---
来源：https://juejin.cn/post/6844904084571422734
起始位置：1118
内容：深度学习（Deep Learning）是利用多层神经网络结构，从大数据中学习现实世界中各类事物能直接用于计算机计算的表示形式（如图像中的事物、音频中的声音等），被认为是智能机器可能的“大脑结构”
Learning：让计算机自动调整函数参数以拟合想要的函数的过程
Deep：多个函数进行嵌套，构成一个多层神经网络，利用非监督贪心逐层训练算法调整有效地自动调整函数参数
简单地说深度学习就是：使用多层神经...

--- 文档 2 ---
来源：https://juejin.cn/post/6844904084571422734
起始位置：762
内容：2 定位不准，三心二意
这里我想要先跟大家普及一个概念，深度学习是什么？很多初学者对深度学习一无所知，却在不停地找各种资料，堆积在自己的电脑或者云盘里，然后更加焦虑，我们要做到对一件事情有足够的了解，定位清晰，这样学起来才得心应手。
要想明白深度学习，你得先知道，深度学习，机器学习，人工智能之间的关系，各自包含哪些内容，便于你对自己的准确定位。
深度学习（deep learning）是机器学习的分...

--- 文档 3 ---
来源：https://juejin.cn/post/6844904084571422734
起始位置：3341
内容：值得注意的是，大脑中的表示是介于密集分布和纯局部之间，也就意味着它们是稀疏的：大脑中 1% 的神经元是同时活动的。
大脑的认知过程是深层次的
• 人们是使用层次化的方式来组织它们的想法和观念的
• 人们首先是学习简单的概念，然后将它们组合起来以表示更加抽象的概念
• 工程师们习惯于将解决问题的方案分解为多个层次的抽象和处理过程
如果能够像人一样学习到这些概念，那将会是非常棒的。知识工程（Knowl...

--- 文档 4 ---
来源：https://juejin.cn/post/6844904084571422734
起始位置：6157
内容：理解驱动深度学习的主要技术趋势。


能够搭建、训练并且运用全连接的深层神经网络。


了解如何实现高效的（向量化）的神经网络。


理解神经网络架构中的关键参数。


这门课将会详尽地介绍深度学习的基本原理，而不仅仅只进行理论概述。
6 数据比赛
除了大名鼎鼎的 kaggle，数据科学家可以参加的数据竞赛平台其实还蛮多的，当然下面只是列举了一部分，你还可以去搜索，比如下面这些：
Kaggle：l...

--- 文档 5 ---
来源：https://juejin.cn/post/6844904084571422734
起始位置：4360
内容：虽然在性能方面比不上 c，c++，java 等语言，但在很大程度上确实大大减少了开发难度。
编程方面，工科生基本都学过一些编程语言的，基本直接上手 python 没什么问题。
python 入门教程如今网络真的是一抓一大把，而如果你本身就有编程基础，基本上不需要再额外学习 python，2 周差不多就能上手了。
3 方向
你学深度学习是要解决什么问题，这里我打个不恰当的比方。你要学哪个方向？
计算...

--- 文档 6 ---
来源：https://juejin.cn/post/6844904084571422734
起始位置：5482
内容：2 动手学深度
李沐，亚马逊首席（principal）科学家，美国卡内基梅隆大学计算机系博士。从 ACM 班、百度到亚马逊，深度学习大牛。
这是深度学习首页简介，《动手学深度》面向中文读者的能运行、可讨论的深度学习教科书，有视频教程，文档，代码，社区，遇到问题都可以讨论。

这里截取一部分课程目录，可以说是相当完整的。

3 斯坦福大学课程
CS231n 近几年一直是计算机视觉领域和深度学习领域最...

==================================================
【批量测试】多个中文问题：

>>> 问题：初学者学习深度学习容易踩哪些坑？
>>> 回答：根据上下文，初学者学习深度学习容易踩的深坑包括：

1. **心态易受学习状态的影响**：过于自信或过于消极，遇到困难容易气馁或放弃。
2. **定位不准，三心二意**：对深度学习概念不清，方向不明确，频繁更换领域，学而不精。
3. **必须把数学知识都学懂才能学算法**：因恐惧数学而不敢学算法，或花费大量时间重新学习数学，导致焦虑和效率低下。
4. **实战不足**：不爱写代码、不跑项目，只停留...

>>> 问题：深度学习和机器学习、人工智能之间是什么关系？
>>> 回答：根据上下文，深度学习是机器学习的分支，而机器学习是人工智能的一个分支。具体来说，深度学习是一种使用多层神经网络进行表征学习的算法，属于机器学习的一部分。...

>>> 问题：为什么 Python 是深度学习的主流语言？
>>> 回答：根据上下文，Python 成为深度学习主流语言的原因主要有两点：

1. **简单易用，用户基础大**：Python 作为解释型语言，大大减少了开发者的工作量，其易用性吸引了庞大的用户群体和繁荣的社区。
2. **丰富的第三方库**：目前机器学习、深度学习的主流库（如 TensorFlow、Keras、scikit-learn 等）都是用 Python 开发的，此外还有 Pandas、NumPy、...
(RAG) PS D:\VSCode\Project\Agentic RAG> 
"""

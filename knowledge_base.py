import os
import chromadb
from chromadb.config import Settings
from config import CHROMA_PATH
from llm_client import call_deepseek

client = chromadb.PersistentClient(
    path=CHROMA_PATH,
    settings=Settings(anonymized_telemetry=False)
)

def get_collection(user_id):
    collection_name = f"user_{user_id}_knowledge"
    try:
        return client.get_collection(collection_name)
    except Exception:
        return client.create_collection(collection_name)

# # 在 knowledge_base.py 中修改
# # pip install sentence_transformers
# from chromadb.utils import embedding_functions

# embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
#     model_name="all-MiniLM-L6-v2",
#     model_kwargs={"device": "cpu"}
# )

# client = chromadb.PersistentClient(
#     path=CHROMA_PATH,
#     settings=Settings(anonymized_telemetry=False)
# )

# def get_collection(user_id):
#     collection_name = f"user_{user_id}_knowledge"
#     try:
#         return client.get_collection(collection_name)
#     except Exception:
#         return client.create_collection(
#             collection_name,
#             embedding_function=embedding_func
#         )

def add_to_knowledge_base(user_id, content, metadata=None):
    collection = get_collection(user_id)
    doc_id = f"doc_{os.urandom(8).hex()}"
    collection.add(
        documents=[content],
        metadatas=[metadata] if metadata else None,
        ids=[doc_id]
    )
    return doc_id

def search_knowledge_base(user_id, query, n_results=5):
    collection = get_collection(user_id)
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    return results

def build_knowledge_graph(user_id):
    collection = get_collection(user_id)
    try:
        all_docs = collection.get()
        if not all_docs['documents']:
            return "知识库为空，请先添加学习内容。"
        
        docs_text = "\n".join(all_docs['documents'][:20])
        prompt = f"""
        根据以下学习笔记，构建一个知识图谱：

        学习笔记：
        {docs_text}

        请按照树状结构组织知识点，例如：
        - 图形推理
          - 数量规律
            - 点数量
            - 线数量
          - 位置规律
            - 平移
            - 旋转
        - 逻辑填空
          - 成语辨析
          - 实词辨析

        请识别出主要的知识模块和子知识点，并指出哪些是薄弱环节（出现错误较多或需要重点关注的）。
        """
        return call_deepseek(prompt)
    except Exception as e:
        return f"构建知识图谱时出错：{str(e)}"

def get_review_suggestions(user_id):
    collection = get_collection(user_id)
    try:
        all_docs = collection.get()
        if not all_docs['documents']:
            return None
        
        docs_text = "\n".join(all_docs['documents'][:10])
        prompt = f"""
        根据以下学习笔记，分析用户的学习情况并给出复习建议：

        学习笔记：
        {docs_text}

        请指出：
        1. 用户掌握较好的知识点
        2. 用户可能需要加强的薄弱环节
        3. 建议的复习计划（按优先级排序）
        """
        return call_deepseek(prompt)
    except Exception as e:
        return None

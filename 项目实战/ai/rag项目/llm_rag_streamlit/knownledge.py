import os
import requests
import json
import streamlit as st

# from langchain.retrievers import BM25Retriever, EnsembleRetriever
from langchain_community.vectorstores import FAISS
from langchain_core.runnables import ConfigurableField


from utils import print_colorful, Fore
from configs import rag_configs
from create_database import get_embeddings


@st.cache_resource
def get_embeddings_wrapper(configs):
    return get_embeddings(configs)

@st.cache_resource
def get_reranker(reranker_cfg: dict):
    """
    返回的实例，必须实现compute_score方法
    compute_score([['query','doc1'], ['query','doc2']])
    """
    if not reranker_cfg:
        return None

    rerankder_model_name = reranker_cfg["model_name_or_path"]
    if "jina" in rerankder_model_name:
        print_colorful(f"正在加载{rerankder_model_name}模型 (jina)")

        class JinaReranker:
            def __init__(self, model_name, api_key) -> None:
                self.model = model_name
                self.api_key = api_key

            def _get_score(self, query, docs, top_n=None):
                url = "https://api.jina.ai/v1/rerank"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}",
                }
                data = {
                    "model": self.model,
                    "query": query,
                    "documents": docs,
                    "top_n": top_n,
                }
                response = requests.post(url, headers=headers, json=data)
                response = sorted(response.json()["results"], key=lambda x: x["index"])
                response = [i["relevance_score"] for i in response]
                return response

            def compute_score(self, docs: list, top_n=None):
                if not docs:
                    return []
                query = docs[0][0]
                docs = [i[1] for i in docs]
                top_n = top_n or len(docs)
                return self._get_score(query=query, docs=docs, top_n=top_n)

        reranker = JinaReranker(rerankder_model_name, reranker_cfg["api_key"])
    elif "bce" in rerankder_model_name:
        print_colorful(f"正在加载{rerankder_model_name}模型 (bce)")
        from BCEmbedding import RerankerModel

        reranker = RerankerModel(
            model_name_or_path=rerankder_model_name, use_fp16=reranker_cfg["use_fp16"]
        )
    elif os.path.exists(rerankder_model_name):
        from FlagEmbedding import FlagReranker

        print_colorful(f"正在加载{rerankder_model_name}模型 (FlagEmbedding)")
        reranker = FlagReranker(rerankder_model_name, use_fp16=reranker_cfg["use_fp16"])
    else:
        print_colorful("reranker模型不存在，请检查文件路径", text_color=Fore.RED)
        reranker = None

    return reranker


def get_retriever(embeddings, database_cfg: dict):
    if embeddings is None:
        return None
    if database_cfg["db_type"] == "faiss":
        print_colorful("正在加载FAISS向量数据库")
        if not os.path.exists(database_cfg["db_vector_path"]):
            print_colorful("数据库不存在，请检查文件路径", text_color=Fore.RED)
            return None
        try:
            faiss_vectorstore = FAISS.load_local(
                folder_path=database_cfg["db_vector_path"],
                embeddings=embeddings,
                index_name=database_cfg["index_name"],
            )
        except ValueError:
            faiss_vectorstore = FAISS.load_local(
                folder_path=database_cfg["db_vector_path"],
                embeddings=embeddings,
                index_name=database_cfg["index_name"],
                allow_dangerous_deserialization=True,
            )
        retriever = faiss_vectorstore.as_retriever(**database_cfg["faiss_params"])
        retriever.configurable_fields(
            search_kwargs=ConfigurableField(
                id="search_kwargs_faiss",
                name="Search Kwargs",
                description="The search kwargs to use",
            )
        )
    else:
        retriever = None
        raise NotImplementedError("没有定义此向量数据的实现")

    # bm25_retriever = BM25Retriever.from_documents(docs_chunks, k=3)
    # bm25_retriever.configurable_fields(
    #     k=ConfigurableField(
    #         id="search_kwargs_bm25",
    #         name="Search Kwargs",
    #         description="The search kwargs to use",
    #     )
    # )
    # retriever = EnsembleRetriever(
    #     retrievers=[bm25_retriever, retriever], weights=[0.5, 0.5]
    # )

    return retriever


def init_models(configs: dict = {}):
    configs = configs or rag_configs

    # embedding model
    embeddings = get_embeddings_wrapper(configs["embedding"])

    # reranker model
    reranker = get_reranker(configs["reranker"])

    # retriever
    Retriever = get_retriever(embeddings, configs["database"])

    return Retriever, reranker


def fetch_relevant_docs(messages, retriever=None, reranker=None, configs: dict = {}):
    """从知识库检索相关性的信息并进行重排序
    Params:
        messages: list, [{'role':'','content':''}]
        retriever: 检索器
        reranker: 重排序模型
        configs: 配置文件
    Return:
        return:list,[('doc', 'metadata'),...]

    """
    if retriever is None:
        return []

    question = messages[-1]["content"]

    # 混合检索
    # retriever_config = {"configurable": {"search_kwargs_faiss": {"k": 1}, "search_kwargs_gm25": 1}}
    retriever_config = configs.get("retriever_config", {})
    docs = retriever.invoke(question, config=retriever_config)
    print_colorful(f"共检索到 {len(docs)} 个docs", text_color=Fore.RED)

    # 重排序
    if reranker is not None:
        docs_content = [d.page_content for d in docs]

        # score排序
        sample_top = configs.get("sample_top", 1)
        scores = reranker.compute_score([[question, kn] for kn in docs_content])
        for d, score in zip(docs, scores):
            d.metadata["score"] = score
        docs = sorted(docs, key=lambda x: x.metadata["score"], reverse=True)
        for idx, d in enumerate(docs, 1):
            print(
                repr(f'{idx}->{d.page_content[:10]}..., score: {d.metadata["score"]}')
            )
        print_colorful(f"提取前topk {sample_top}")
        docs = docs[:sample_top]

        # 相似度过滤
        if sample_threshold := configs.get("sample_threshold"):
            docs = [d for d in docs if d.metadata["score"] >= sample_threshold]
        print_colorful(f"相似度阈值 {sample_threshold}")
        print_colorful(f"过滤后得到 {len(docs)} 个docs")

    return docs


Knownledge_QA_prompt = """
下边是检索到的与问题相关的补充性信息，仅供参考！如果确实与问题相关，则参考其进行回答，否则请忽略。
--------------------
{context}
--------------------
问题：{question}
""".strip()


def create_prompt(QA_prompt, question, docs):
    """得到最后的prompt"""
    info = ""
    for idx, d in enumerate(docs, 1):
        info += f"信息片段 {idx}："
        info += f"```{d.page_content}```"
        info += f" (数据源:{json.dumps(d.metadata['source'])})"
        info += "\n\n"
    info = info.strip() or "<没有检索到补充信息>"

    return QA_prompt.format(context=info, question=question)




def RAG(messages, retriever, reranker, show_info=False, configs={}):
    configs = {
        "sample_top": 5,  # 参考检索的数量 现在是三个，就改这个值
        "sample_threshold": -1000,
        # "retriever_config": {  # 初始化已经配置
        #     "configurable": {
        #         "search_kwargs_faiss": {"search_type": "similarity", "k": 10},
        #         # "search_kwargs_gm25": 2,
        #     }
        # },
        **configs,
    }
    docs = fetch_relevant_docs(
        messages,
        retriever=retriever,
        reranker=reranker,
        configs=configs,
    )
    question = messages[-1]["content"]
    question = create_prompt(Knownledge_QA_prompt, question, docs)

    if show_info:
        print("=" * 20 + "prompt内容构造如下")
        print(repr(question))
        print("=" * 20)

    messages[-1]["content"] = question
    # sources = [i.metadata for i in docs]

    return messages, docs

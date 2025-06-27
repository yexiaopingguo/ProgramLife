#模型下载

from modelscope import snapshot_download
model_dir = snapshot_download('AI-ModelScope/bge-reranker-v2-m3',local_dir='D:\\vscode_python\\llm_rag_streamlit\\reranker_model\\AI-ModelScope\\bge-reranker-v2-m3')
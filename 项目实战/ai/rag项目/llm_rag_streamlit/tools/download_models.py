# 模型下载
import os
from modelscope import snapshot_download

# 模型保存地址
save_dir = "models/"

# ===================embedding模型和reranker模型
# bge-reranker-large
# model_dir = snapshot_download("quietnight/bge-reranker-large", cache_dir=save_dir)
# bge-large-zh-v1.5
model_dir = snapshot_download("AI-ModelScope/bge-large-zh-v1.5", cache_dir=save_dir)
os.rename(
    save_dir + "/AI-ModelScope/bge-large-zh-v1___5",
    save_dir + "/AI-ModelScope/bge-large-zh-v1.5",
)

# m3e embedding model
# model_dir = snapshot_download('AI-ModelScope/m3e-base', cache_dir=save_dir)

# chatglm3-6b
model_dir = snapshot_download("ZhipuAI/chatglm3-6b", cache_dir=save_dir)



#验证SDK token

# from modelscope.hub.api import HubApi
# api = HubApi()
# api.login('xxxxxx')  # bce需要申请

# #bce模型下载
# model_dir = snapshot_download('maidalun/bce-embedding-base_v1', cache_dir="models")
# model_dir = snapshot_download('maidalun/bce-reranker-base_v1', cache_dir="models")

from langchain_community.document_loaders import WebBaseLoader
loader = WebBaseLoader("https://baike.baidu.com/item/%E7%BA%BD%E7%BA%A6/6230")
loader.requests_kwargs = {'verify':False}
data = loader.load()
print(data)

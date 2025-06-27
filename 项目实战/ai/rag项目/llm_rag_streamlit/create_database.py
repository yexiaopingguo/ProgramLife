import os, os.path as osp, json
import glob
import hashlib
from typing import List
from functools import partial
from tqdm import tqdm

from multiprocessing import Pool
from langchain_community.document_loaders import (
    CSVLoader,
    EverNoteLoader,
    PDFMinerLoader,
    TextLoader,
    UnstructuredEmailLoader,
    UnstructuredEPubLoader,
    UnstructuredHTMLLoader,
    UnstructuredMarkdownLoader,
    UnstructuredODTLoader,
    UnstructuredPowerPointLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredExcelLoader,
)
from langchain_community.document_loaders import Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter, TextSplitter

from langchain_community.docstore.document import Document
from langchain_community.vectorstores import FAISS


from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)
from utils import print_colorful, Fore


# Custom document loaders 自定义文档加载
class MyElmLoader(UnstructuredEmailLoader):
    def load(self) -> List[Document]:
        """Wrapper adding fallback for elm without html"""
        try:
            try:
                doc = UnstructuredEmailLoader.load(self)
            except ValueError as e:
                if "text/html content not found in email" in str(e):
                    # Try plain text
                    self.unstructured_kwargs["content_source"] = "text/plain"
                    doc = UnstructuredEmailLoader.load(self)
                else:
                    raise
        except Exception as e:
            # Add file_path to exception message
            raise type(e)(f"{self.file_path}: {e}") from e

        return doc


# Map file extensions to document loaders and their arguments
# GB2312 GB18030  注意更换数据类型
LOADER_MAPPING = {
    ".csv": (CSVLoader, {"encoding": "GB18030"}),
    # ".doc": (UnstructuredWordDocumentLoader, {}),
    # ".docx": (UnstructuredWordDocumentLoader, {}),
    ".doc": (Docx2txtLoader, {}),
    ".docx": (Docx2txtLoader, {}),
    ".enex": (EverNoteLoader, {}),
    ".eml": (MyElmLoader, {}),
    ".epub": (UnstructuredEPubLoader, {}),
    ".html": (UnstructuredHTMLLoader, {}),
    ".md": (UnstructuredMarkdownLoader, {}),
    ".odt": (UnstructuredODTLoader, {}),
    ".pdf": (PDFMinerLoader, {}),
    ".ppt": (UnstructuredPowerPointLoader, {}),
    ".pptx": (UnstructuredPowerPointLoader, {}),
    ".txt": (TextLoader, {"encoding": "utf8"}),
    ".xls": (UnstructuredExcelLoader, {"encoding": "GB18030", "mode": "elements"}),
    ".xlsx": (UnstructuredExcelLoader, {"encoding": "GB18030", "mode": "elements"}),
}


def read_hash_file(path):
    hash_data = {}
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            hash_data = json.load(f)
    return hash_data


def save_hash_file(hash_data, path):

    with open(path, "w", encoding="utf-8") as f:
        json.dump(hash_data, f, ensure_ascii=False)


def get_hash_of_file(path):
    with open(path, "rb") as f:
        readable_hash = hashlib.md5(f.read()).hexdigest()
    return readable_hash


def load_single_document(file_path: str) -> List[Document]:
    ext = "." + file_path.rsplit(".", 1)[-1]
    if ext in LOADER_MAPPING:
        loader_class, loader_args = LOADER_MAPPING[ext]
        try:
            loader = loader_class(file_path, **loader_args)
            docs = loader.load()
        except:
            print_colorful(f"加载{osp.basename(file_path)}失败!", text_color=Fore.RED)
            return file_path, []

        return file_path, docs

    raise ValueError(f"Unsupported file extension '{ext}'")


def load_documents(
    source_dir: str,
    configs: dict,
    ignored_files: List[str] = [],
    force_create: bool = False,
) -> List[Document]:
    """
    Loads all documents from the source documents directory, ignoring specified files
    """
    all_files = []
    for ext in LOADER_MAPPING:
        all_files.extend(
            glob.glob(os.path.join(source_dir, f"**/*{ext}"), recursive=True)
        )
    print_colorful(f"共读取到{len(all_files)}个文件")

    filtered_files = [
        file_path for file_path in all_files if file_path not in ignored_files
    ]

    # hash filter
    hash_data = read_hash_file(configs["hash_file_path"])
    hash_file_list = hash_data.get(configs["index_name"], [])
    if not force_create:
        tmp = []
        for file in filtered_files:
            hash = get_hash_of_file(file)
            if hash not in hash_file_list:
                tmp.append(file)
                hash_file_list.append(hash)
        filtered_files = tmp
    else:
        hash_file_list = []
        for file in filtered_files:
            hash = get_hash_of_file(file)
            hash_file_list.append(hash)
    hash_data[configs["index_name"]] = list(set(hash_file_list))
    save_hash_file(hash_data, configs["hash_file_path"])

    print_colorful(f"将对{len(hash_file_list)}个文件进行embedding")
    print_colorful("正在嵌入文件：", filtered_files)

    # splitter
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=configs["chunk_size"], chunk_overlap=configs["chunk_overlap"]
    )

    # load
    results = []
    faild_files = []
    with Pool(processes=os.cpu_count()) as pool:
        with tqdm(
            total=len(filtered_files), desc="Loading new documents", ncols=80
        ) as pbar:
            for i, docs in enumerate(
                pool.imap_unordered(load_single_document, filtered_files)
            ):
                # 针对不同的文件类型分别进行处理
                file_path, docs = docs
                if not docs:
                    faild_files.append(file_path)
                else:
                    if file_path.endswith((".xlsx", "xls", "csv")):
                        # 表格数据，合并多个行
                        merge_rows = configs["merge_rows"]
                        merge_n = len(docs) // merge_rows + bool(len(docs) % merge_rows)
                        _docs = []
                        for i in range(merge_n):
                            tmp = "\n\n".join(
                                [
                                    d.page_content
                                    for d in docs[i * merge_rows : (i + 1) * merge_rows]
                                ]
                            )
                            _docs.append(
                                Document(tmp, metadata=dict(source=docs[0]["source"]))
                            )
                        results.extend(_docs)
                    else:
                        # 合并一个文件中的所有page_content
                        tmp = [i.page_content for i in docs]
                        docs = Document(
                            "".join(tmp).strip(),
                            metadata={
                                "source": docs[0].metadata["source"],
                                "pages": len(tmp),
                            },
                        )
                        # 进行split
                        docs = splitter.split_documents([docs])
                        results.extend(docs)

                pbar.update()

    return results, faild_files


def process_documents(
    configs: dict, ignored_files: List[str] = [], force_create: bool = False
) -> List[Document]:
    """
    Load documents and split in chunks
    """
    source_directory = osp.join(configs["db_docs_path"], configs["index_name"])
    print(f"Loading documents from {source_directory}")
    documents, faild_files = load_documents(
        source_directory, configs, ignored_files, force_create
    )
    if not documents:
        print("No new documents to load")
        exit(0)
    print(
        f"Loaded {len(documents)} new documents from {source_directory}."
        f"\nSplit into {len(documents)} chunks of text (max. {configs['chunk_size']} tokens each)"
    )
    return documents, faild_files


def get_embeddings(embedding_cfg: dict):
    embeddings_model_name = embedding_cfg["model_name_or_path"]
    if "openai" in embeddings_model_name:
        print_colorful(f"正在加载{embeddings_model_name}模型 (openai)")
        from langchain_openai import OpenAIEmbeddings

        api_key = embedding_cfg["api_key"]
        base_url = embedding_cfg["base_url"]
        model = embedding_cfg["model"]
        embeddings = OpenAIEmbeddings(
            model=model,
            api_key=api_key,
            base_url=base_url,
        )
    elif "bge" in embeddings_model_name:
        print_colorful(f"正在加载{embeddings_model_name}模型 (bge)")
        if not os.path.exists(embeddings_model_name):
            print_colorful("embedding模型不存在，请检查文件路径", text_color=Fore.RED)
            return None
        from langchain_community.embeddings import HuggingFaceBgeEmbeddings

        embeddings = HuggingFaceBgeEmbeddings(
            model_name=embeddings_model_name,
            model_kwargs=embedding_cfg["model_kwargs"],
            encode_kwargs=embedding_cfg["encode_kwargs"],
            query_instruction=embedding_cfg["query_instruction"],
        )
    elif "bce" in embeddings_model_name:
        print_colorful(f"正在加载{embeddings_model_name}模型 (bce)")
        # from BCEmbedding import EmbeddingModel
        # # init embedding model
        # embeddings = EmbeddingModel(
        #     model_name_or_path=embeddings_model_name, use_fp16=embedding_cfg["use_fp16"]
        # )
        from langchain_community.embeddings import HuggingFaceEmbeddings

        embeddings = HuggingFaceEmbeddings(
            model_name=embeddings_model_name,
            model_kwargs=embedding_cfg["model_kwargs"],
            encode_kwargs=embedding_cfg["encode_kwargs"],
        )

    elif "jina" in embeddings_model_name and not os.path.exists(embeddings_model_name):
        # 使用在线的jina embedding 模型
        print_colorful(f"正在加载{embeddings_model_name}模型(jina)")
        from langchain_community.embeddings import JinaEmbeddings

        embeddings = JinaEmbeddings(
            jina_api_key=embedding_cfg["api_key"], model_name=embeddings_model_name
        )
    elif "cohere" in embeddings_model_name:
        # cohere在线模型
        print_colorful(f"正在加载{embeddings_model_name}模型(cohere)")
        from langchain_community.embeddings import CohereEmbeddings

        embeddings = CohereEmbeddings(
            model="embeddings_model_name", cohere_api_key=embedding_cfg["api_key"]
        )
    else:
        # 本地大模型
        # 通用的huggingface embedding 模型
        print_colorful(
            f"正在加载{embeddings_model_name}模型 (SentenceTransformerEmbeddings)"
        )
        if not os.path.exists(embeddings_model_name):
            print(os.getcwd())
            print_colorful("embedding模型不存在，请检查文件路径", text_color=Fore.RED)
            return None
        embeddings = SentenceTransformerEmbeddings(
            model_name=embeddings_model_name,
            model_kwargs=embedding_cfg["model_kwargs"],
            encode_kwargs=embedding_cfg["encode_kwargs"],
        )

    return embeddings


def create_db(rag_configs: dict, force_create: bool = False):
    """
    force_create: 重新创建数据库，覆盖已经存在的
    """
    # Create embeddings
    # print(torch.cuda.is_available())
    # Create and store locally vectorstore
    print("Creating new vectorstore")
    documents, faild_files = process_documents(
        rag_configs["database"], force_create=force_create
    )

    print(f"Loading embeddings. May take some minutes...")
    embeddings = get_embeddings(rag_configs["embedding"])

    print(f"Creating embeddings. May take some minutes...")
    db_configs = rag_configs["database"]
    db_type = db_configs["db_type"]
    output_dir = db_configs["db_vector_path"]
    index_name = db_configs["index_name"]
    if db_type == "chroma":
        from langchain.vectorstores import Chroma

        db = Chroma.from_documents(documents, embeddings, persist_directory=output_dir)
        db.persist()
        db = None
    elif db_type == "faiss":

        print("创建新faiss数据库")
        db = FAISS.from_documents(documents, embeddings)

        # 读取之前的db data(GPU版本的不支持)
        if os.path.exists(output_dir) and not force_create:
            try:
                print("读取旧数据库")
                old_db = FAISS.load_local(
                    folder_path=output_dir, index_name=index_name, embeddings=embeddings
                )

                print("融合新旧数据库")
                db.merge_from(old_db)
            except Exception as e:
                print(e)

        print("保存成功")
        db.save_local(output_dir, index_name)
        db = None
    else:
        raise NotImplementedError(f"未定义数据库 {db_type} 的实现.")

    return faild_files


if __name__ == "__main__":
    # 设置目录和embedding基础变量

    from configs import rag_configs

    create_db(rag_configs=rag_configs, force_create=True)

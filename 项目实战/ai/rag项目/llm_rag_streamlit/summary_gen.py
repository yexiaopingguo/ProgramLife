import os
import glob
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
from typing import List

# Map file extensions to document loaders and their arguments
LOADER_MAPPING = {
    ".csv": CSVLoader,
    ".doc": Docx2txtLoader,
    ".docx": Docx2txtLoader,
    ".enex": EverNoteLoader,
    ".eml": UnstructuredEmailLoader,
    ".epub": UnstructuredEPubLoader,
    ".html": UnstructuredHTMLLoader,
    ".md": UnstructuredMarkdownLoader,
    ".odt": UnstructuredODTLoader,
    ".pdf": PDFMinerLoader,
    ".ppt": UnstructuredPowerPointLoader,
    ".pptx": UnstructuredPowerPointLoader,
    ".txt": TextLoader,
    ".xls": UnstructuredExcelLoader,
    ".xlsx": UnstructuredExcelLoader,
}

def read_document_content(file_path: str) -> str:
    """
    Read the content of a single document based on its file extension
    """
    ext = os.path.splitext(file_path)[1]
    if ext in LOADER_MAPPING:
        loader_class = LOADER_MAPPING[ext]
        try:
            loader = loader_class(file_path)
            docs = loader.load()
            if isinstance(docs, str):
                return docs
            elif isinstance(docs, list):
                # Join all parts into a single string
                return "\n".join(str(doc) for doc in docs)
            else:
                # Handle other types of document loaders as needed
                print(f"Unsupported document format from {file_path}")
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
    else:
        print(f"Unsupported file extension '{ext}'")

    return ""

def read_documents(source_dir: str) -> List[str]:
    """
    Read contents of all documents in a directory
    """
    contents = []
    basename = []
    for ext in LOADER_MAPPING:
        file_paths = glob.glob(os.path.join(source_dir, f"*{ext}"), recursive=True)
        for file_path in file_paths:
            content = read_document_content(file_path)
            if content:
                contents.append(content)
                basename.append(os.path.basename(file_path))
    return contents,basename




Summary_QA_prompt = """
按文章索引为下面输入的多篇文章分别，总结标题，生成摘要，每篇摘要150字左右
--------------------
{context}
--------------------
问题：{question}
""".strip()


# 为摘要生成制作最后的prompt
def summary_prompt(QA_prompt, question, docs,basename):
    """得到最后的prompt"""
    info = ""
    for idx,contend in enumerate(docs):
        info += f"文件{idx+1}：{basename[idx]}"
        info += f"第{idx+1}篇文章内容如下："
        info += f"```{contend}```"
        info += "\n\n"
    info = info.strip()  

    return QA_prompt.format(context=info, question=question)

source_directory = "summary_database\documents\summary_tem"

#摘要生成
def Summary(messages, show_info=False):
    
    docs,basename = read_documents(source_directory)
        
    question = messages[-1]["content"]
    question = summary_prompt(Summary_QA_prompt, question, docs,basename)
    if show_info:
        print("=" * 20 + "prompt内容构造如下")
        print(repr(question))
        print("=" * 20)
    messages[-1]["content"] = question
    # sources = [i.metadata for i in docs]
    print(messages)
    return messages, docs





# Example usage:
if __name__ == "__main__":
    messages = []
    messages.append({"role": "user", "content":''})
    source_directory = "summary_database\documents\summary_tem"
    Summary(messages)

## create_database.py's calling hierarchy


main->create_db

create_db 
-> process_documents
->get_embeddings
-> chroma/faiss vector database from document

process_documents->load_documents

load_documents->load_single_document

load_single_document->many document loaders from the `LOADER_MAPPING`




## knownledge.py's calling hierarchy 
1. RAG
- fetch_relevant_docs
- create_prompt
2. fetch_relevant_docs function calls:
- retriever.invoke
- reranker.compute_score
- create_prompt function is a standalone function that formats the final prompt based on the retrieved documents and the question.
3. init_models function calls:
- get_embeddings_wrapper
- get_reranker
- get_retriever
    get_reranker function conditionally creates instances of different reranker models based on the provided configuration.
6. get_retriever function loads a retriever based on the database configuration.
get_embeddings_wrapper function retrieves embeddings based on the provided configuration.
fetch_relevant_docs function retrieves relevant documents based on the messages, retriever, reranker, and configurations provided.


## the relationship between db_server.py, db_settings.py, and create_database.py

**The main flow**
User interacts with the Streamlit app.
Streamlit app calls functions from create_database.py to manage the database.
FastAPI server uses the embeddings and database created by create_database.py to handle API requests.


db_server.py: FastAPI server for database operations.
create_database.py: Functions for creating and managing the database.
db_setting.py: Streamlit app for user interaction to manage the database.


1. db_server.py:
This file sets up a FastAPI server to handle requests related to the database.
It imports get_embeddings from create_database.py to get the embeddings.
It uses configurations from configs (presumably a module or file named configs.py).

2. create_database.py:
This file contains functions to create and manage the database, including loading documents, processing them, and creating embeddings.
It defines the get_embeddings function, which is used in db_server.py.
It also defines the create_db function, which is used to create the database and is called in db_setting.py.

3. db_setting.py:
This file sets up a Streamlit application for managing the database.
It imports create_db from create_database.py to create or update the database based on user input.
It also imports read_hash_file and save_hash_file from create_database.py for managing hash files.



**Calling Hierarchy**

- db_server.py
  Calls get_embeddings from create_database.py.

- db_setting.py:
  Calls create_db from create_database.py to create or update the database.
  Uses read_hash_file and save_hash_file from create_database.py for hash management.

Summary



## webdemo.py's calling hierarchy

Sure! Here's the calling hierarchy for the [webdemo.py](file:///d%3A/ANewspace/code/llm_rag_streamlit/webdemo.py#1%2C1-1%2C1) file:

1. **[main()](file:///d%3A/ANewspace/code/llm_rag_streamlit/webdemo.py#437%2C5-437%2C5)**
   - **`siderbar_title("智能问答系统")`**
   - **[init_st()](file:///d%3A/ANewspace/code/llm_rag_streamlit/webdemo.py#79%2C5-79%2C5)**
     - Initializes session state parameters.
     - Creates necessary directories for the database.
   - **[option_menu()](file:///d%3A/ANewspace/code/llm_rag_streamlit/webdemo.py#6%2C35-6%2C35)** (within `st.sidebar`)
     - Sets the [selected](file:///d%3A/ANewspace/code/llm_rag_streamlit/webdemo.py#442%2C9-442%2C9) mode.
   - **`siderbar_params(configs)`**
     - **[callback_db_setting()](file:///d%3A/ANewspace/code/llm_rag_streamlit/webdemo.py#122%2C5-122%2C5)** (if button clicked)
     - **[callback_db_setting_finish()](file:///d%3A/ANewspace/code/llm_rag_streamlit/webdemo.py#126%2C5-126%2C5)** (if button clicked)
     - **[callback_session_change()](file:///d%3A/ANewspace/code/llm_rag_streamlit/webdemo.py#107%2C5-107%2C5)** (if session changed)
   - **[db_page()](file:///d%3A/ANewspace/code/llm_rag_streamlit/webdemo.py#15%2C24-15%2C24)** (if `st.session_state["IS_DB_MODE"]` is [True](file:///d%3A/ANewspace/code/llm_rag_streamlit/webdemo.py#43%2C23-43%2C23))
   - **`run_chat(configs)`** (if `st.session_state["IS_DB_MODE"]` is [False](file:///d%3A/ANewspace/code/llm_rag_streamlit/webdemo.py#88%2C20-88%2C20))
     - **[init_chat_history()](file:///d%3A/ANewspace/code/llm_rag_streamlit/webdemo.py#130%2C5-130%2C5)**
     - **`st.chat_input()`** (if user inputs a prompt)
       - **`st.chat_message("user")`**
       - **`st.chat_message("assistant")`**
         - **`init_models(configs=rag_configs)`** (if `cfgs["RAG"]` is [True](file:///d%3A/ANewspace/code/llm_rag_streamlit/webdemo.py#43%2C23-43%2C23))
         - **[RAG()](file:///d%3A/ANewspace/code/llm_rag_streamlit/webdemo.py#7%2C24-7%2C24)** (if `cfgs["RAG"]` is [True](file:///d%3A/ANewspace/code/llm_rag_streamlit/webdemo.py#43%2C23-43%2C23))
         - **`client.chat.completions.create()`** (if `cfgs["stream"]` is [False](file:///d%3A/ANewspace/code/llm_rag_streamlit/webdemo.py#88%2C20-88%2C20))
         - **`client.chat.completions.create()`** (if `cfgs["stream"]` is [True](file:///d%3A/ANewspace/code/llm_rag_streamlit/webdemo.py#43%2C23-43%2C23))
     - **[pills()](file:///d%3A/ANewspace/code/llm_rag_streamlit/webdemo.py#5%2C29-5%2C29)** (if there are more than one message in `st.session_state.messages`)
       - **[clear_chat_history()](file:///d%3A/ANewspace/code/llm_rag_streamlit/webdemo.py#101%2C5-101%2C5)** (if "清空对话" selected)
   - **[siderbar_bottom()](file:///d%3A/ANewspace/code/llm_rag_streamlit/webdemo.py#414%2C5-414%2C5)**

2. **`if __name__ == "__main__": main()`**

**Function Call Details:**

- **`siderbar_title(title)`**: Sets the sidebar title.
- **`init_st()`**: Initializes session state and creates directories.
- **`clear_chat_history()`**: Clears the chat history.
- **`callback_session_change()`**: Handles session change.
- **`callback_db_setting()`**: Sets `IS_DB_MODE` to `True`.
- **`callback_db_setting_finish()`**: Sets `IS_DB_MODE` to `False`.
- **`init_chat_history()`**: Initializes chat history.
- **`run_chat(cfgs)`**: Runs the chat interface.
- **`siderbar_params(configs)`**: Sets sidebar parameters.
- **`siderbar_bottom()`**: Adds download button for chat history.

This hierarchy shows the flow of the program and how different functions are called based on user interactions and session states.



## what does `message` contain?






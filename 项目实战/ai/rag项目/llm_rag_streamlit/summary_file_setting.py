import streamlit as st
import os, os.path as osp
import streamlit_antd_components as sac
from io import BytesIO
from configs import rag_configs,summary_configs
from create_database import create_db, read_hash_file, save_hash_file
from copy import deepcopy
from glob import glob
import pandas as pd
import shutil


def return_from_db_setting():
    print("change 1")
    st.session_state["IS_DB_MODE"] = False


def is_alphabet(char):
    if (char >= "\u0041" and char <= "\u005a") or (
        char >= "\u0061" and char <= "\u007a"
    ):
        return True
    else:
        return False


def is_number(char):
    if char >= "\u0030" and char <= "\u0039":
        return True
    else:
        return False


def is_valid_name(name):
    for char in name:
        if not (char in ["_"] or is_alphabet(char) or is_number(char)):
            return False
    else:
        return True


def gen_docs_to_summary():
    if st.session_state["IS_files_uploaded"] is False:
        st.toast(':red[请先确定]', icon="🌟")
    else:
        st.session_state["IS_summary_MODE"] = True
        st.session_state["IS_SU_MODE"] = False
        

    



def save_docs_to_summary():
    summary_docs_path = summary_configs["summary_database"]["summary_docs_path"]
    # old_names = [i for i in os.listdir(db_docs_path) if not i.endswith("json")]
    db_new_index_name = 'summary_tem'
    up_files = st.session_state.upload_new_summary_docs_key

    for uploaded_file in up_files:

        filename = uploaded_file.name
        save_root = f"{summary_docs_path}/{db_new_index_name}"
        os.makedirs(save_root, exist_ok=True)
        save_path = f"{save_root}/{filename}"
        print("filename:", filename)
        
        if isinstance(uploaded_file, bytes):  # raw bytes
            uploaded_file = BytesIO(uploaded_file)
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getvalue())
        elif hasattr(uploaded_file, "read"):  # a file io like object
            with open(save_path, "wb") as f:
                f.write(uploaded_file.read())
    st.toast(":green[文件上传成功]", icon="🌟")
    st.session_state["IS_files_uploaded"] = True
    # st.session_state["files_uploaded"] = True
    # st.toast(":green[正在进行向量化存储, 稍等...]", icon="🏃")
    # # 保存到向量数据库中

    # rag_configs["database"]["index_name"] = db_new_index_name
    # faild_files = create_db(rag_configs, force_create=True)
    # if not faild_files:
    #     st.toast(":green[成功存储到向量数据库]", icon="👏")
    # else:
    #     _faild_files = [osp.basename(i) for i in faild_files]
    #     _faild_files_str = "\n".join(_faild_files)
    #     st.toast(f":red[以下文件存储失败:\n{_faild_files_str}]", icon="❌")

        # 从数据库中删除
        # for file in faild_files:
        #     os.remove(file)

def summary_page():
    if "ori_summary_cfgs" not in st.session_state:
        st.session_state["ori_summary_cfgs"] = deepcopy(summary_configs)

    else:
        summary_docs_path = summary_configs["summary_database"]["summary_docs_path"]
        # old_names = [i for i in os.listdir(summary_docs_path) if not i.endswith("json")]
       
        files = glob(osp.join(summary_docs_path,'summary_tem', "**.*"), recursive=True)
        st.markdown("### ✨摘要生成功能——文件管理")
        st.markdown('')
        st.markdown('')
        st.markdown("**为以下文件生成摘要：**")
        with st.container(border=True, height=300):
            st.markdown('')
            df = pd.DataFrame({"文件": files})
            st.dataframe(df, use_container_width=True)
        select_ch_items = sac.buttons(
            [
                sac.ButtonsItem("添加文件", color="green"),
                sac.ButtonsItem("删除文件", color="green"),
            ],
            use_container_width=True,
            align="center",
            return_index=True,
        )
        with st.container(border=True):
            # 添加文件
            if select_ch_items == 0:
                st.file_uploader(
                    "🔸添加文件",
                    ["pdf", "csv", "txt", "xls", "xlsx", "doc", "docx", "json", "markdown"],
                    accept_multiple_files=True,
                    key="upload_new_summary_docs_key",
                )
                st.markdown('')
                st.markdown('')
                _in_cols = st.columns([0.33, 0.34, 0.33])
                _in_cols[1].button(
                    "**确定**✅ ",
                    on_click=save_docs_to_summary,
                    key="save_docs_to_summary-key",
                    use_container_width=True,
                )
             # 删除文件
            elif select_ch_items == 1:
                del_files = st.multiselect(
                    "🔸删除所选文件",
                    files,
                    format_func=lambda x: osp.basename(x),
                    help="💡支持多选",
                )
                st.markdown('')
                st.markdown('')
                st.markdown('')
                st.markdown('')
                _in_cols = st.columns([0.33, 0.34, 0.33])
                key_a = _in_cols[1].button(
                    "**确定删除🚫** ",
                    use_container_width=True,
                    help="💡删除文件"
                )
                if key_a:
                    if not del_files:
                        st.toast(f":red[请选择待删除的文件]", icon="❌")
                    else:
                            for file in del_files:
                                os.remove(file)
                            st.toast(":green[删除成功]", icon="✅")
        _01_cols = st.columns([0.2, 0.6, 0.2])
        _01_cols[1].button(
                    "👉 **生成摘要**📝 👈",
                    on_click=gen_docs_to_summary,
                    key="gen_docs_to_summary-key",
                    use_container_width=True,
                )
        
            
     
if __name__ == "__main__":
    st.set_page_config("数据库管理", layout="centered")
    st.markdown(
        """<style>
    .block-container {
        padding: 1rem 4rem 2rem 4rem;
    }

    .st-emotion-cache-16txtl3 {
        padding: 3rem 1.5rem;
    }
    </style>
    # """,
        unsafe_allow_html=True,
    )
    

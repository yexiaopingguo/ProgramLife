import streamlit as st
import os, os.path as osp
import streamlit_antd_components as sac
from io import BytesIO
from configs import rag_configs
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


def save_docs_to_db():

    db_docs_path = rag_configs["database"]["db_docs_path"]
    old_names = [i for i in os.listdir(db_docs_path) if not i.endswith("json")]
    db_new_index_name = st.session_state.db_new_index_name_key
    up_files = st.session_state.upload_new_index_docs_key

    Flag = 0
    if not db_new_index_name:
        Flag = 1
        st.toast(":red[新数据库名 未填写！]", icon="❌")
    elif db_new_index_name in old_names:
        Flag = 1
        st.toast(":red[数据库名重复，请转到修改功能！]", icon="❌")
    elif not is_valid_name(db_new_index_name):
        Flag = 1
        st.toast(":red[数据库名必须是大小写字母、数字和下划线(_)的组合]", icon="❌")
    if not up_files:
        Flag = 1
        st.toast(":red[请选择文件]", icon="❌")
    print(f"|{db_new_index_name}|")
    if Flag:
        return
    # 保存文件到对应的documents
    for uploaded_file in up_files:

        filename = uploaded_file.name
        save_root = f"{db_docs_path}/{db_new_index_name}"
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
    st.toast(":green[文件存储成功]", icon="🌟")
    st.toast(":green[正在进行向量化存储, 稍等...]", icon="🏃")
    # 保存到向量数据库中

    rag_configs["database"]["index_name"] = db_new_index_name
    faild_files = create_db(rag_configs, force_create=True)
    if not faild_files:
        st.toast(":green[成功存储到向量数据库]", icon="👏")
    else:
        _faild_files = [osp.basename(i) for i in faild_files]
        _faild_files_str = "\n".join(_faild_files)
        st.toast(f":red[以下文件存储失败:\n{_faild_files_str}]", icon="❌")

        # 从数据库中删除
        for file in faild_files:
            os.remove(file)


def db_page():
    if "ori_rag_cfgs" not in st.session_state:
        st.session_state["ori_rag_cfgs"] = deepcopy(rag_configs)

    tabls = sac.tabs(
        [
            sac.TabsItem(label="🛠️ 修改数据库"),
            sac.TabsItem(label="🪄 新建数据库"),
        ],
        align="left",
        variant="outline",
        color="red",
        index=0,
        return_index=True,
    )
    # 修改数据库
    if tabls == 0:
        db_docs_path = rag_configs["database"]["db_docs_path"]
        old_names = [i for i in os.listdir(db_docs_path) if not i.endswith("json")]
        select_index_name = st.selectbox("**选择数据库**", tuple(old_names))
        if select_index_name is None:
            st.info(f"没有查找到数据库")

            st.stop()
        files = glob(osp.join(db_docs_path, select_index_name, "**.*"), recursive=True)
        # files = files * 10
        st.markdown("**文件列表**")
        with st.container(border=True, height=200):
            df = pd.DataFrame({"文件": files})
            st.dataframe(df, use_container_width=True)
        select_ch_items = sac.buttons(
            [
                sac.ButtonsItem("添加文件", color="green"),
                sac.ButtonsItem("删除文件", color="green"),
                sac.ButtonsItem("删除数据库"),
            ],
            use_container_width=True,
            align="center",
            return_index=True,
        )
        with st.container(border=True):
            # 添加文件
            if select_ch_items == 0:
                up_files = st.file_uploader(
                    "上传文件",
                    type=[
                        "pdf",
                        "csv",
                        "txt",
                        "xls",
                        "xlsx",
                        "doc",
                        "docx",
                        "json",
                        "markdown",
                    ],
                    accept_multiple_files=True,
                )
                _in_cols = st.columns(2)
                key_a = _in_cols[0].button(
                    "融合模式添加",
                    use_container_width=True,
                    help="💡添加到已经存在的数据库中",
                )
                key_b = _in_cols[1].button(
                    "覆盖模式添加", use_container_width=True, help="💡重新创建数据库"
                )
                if key_a or key_b:
                    if not up_files:
                        st.toast(f":red[请选择文件]", icon="❌")
                    else:
                        # 保存文件到对应的documents
                        for uploaded_file in up_files:
                            filename = uploaded_file.name
                            print("filename:", filename)

                            save_path = f"{db_docs_path}/{select_index_name}/{filename}"
                            if isinstance(uploaded_file, bytes):  # raw bytes
                                uploaded_file = BytesIO(uploaded_file)
                                with open(save_path, "wb") as f:
                                    f.write(uploaded_file.getvalue())
                            elif hasattr(
                                uploaded_file, "read"
                            ):  # a file io like object
                                with open(save_path, "wb") as f:
                                    f.write(uploaded_file.read())
                        st.toast(":green[文件存储成功]", icon="🌟")
                        st.toast(":green[正在进行向量化存储, 稍等...]", icon="🏃")
                        # 保存到向量数据库中

                        rag_configs["database"]["index_name"] = select_index_name
                        faild_files = create_db(rag_configs, force_create=key_b)
                        if not faild_files:
                            st.toast(":green[成功存储到向量数据库]", icon="👏")
                        else:
                            _faild_files = [osp.basename(i) for i in faild_files]
                            _faild_files_str = "\n".join(_faild_files)
                            st.toast(
                                f":red[以下文件存储失败:\n{_faild_files_str}]",
                                icon="❌",
                            )

                            # 从数据库中删除
                            for file in faild_files:
                                os.remove(file)
                        st.rerun()
            # 删除文件
            elif select_ch_items == 1:
                del_files = st.multiselect(
                    "删除所选文件",
                    files,
                    format_func=lambda x: osp.basename(x),
                    help="💡支持多选",
                )
                _in_cols = st.columns([0.3, 0.4, 0.4])
                key_a = _in_cols[1].button(
                    "确认删除所选文件",
                    use_container_width=True,
                    help="💡将重新创建数据库",
                )
                if key_a:
                    if not del_files:
                        st.toast(f":red[请选择待删除的文件]", icon="❌")
                    else:
                        if len(del_files) == len(files):
                            st.toast(":red[请使用删除数据库功能]", icon="❌")
                        else:
                            for file in del_files:
                                os.remove(file)
                            st.toast(":green[删除成功]", icon="✅")
                            st.toast(":green[正在创建向量化存储, 稍等...]", icon="🏃")
                            rag_configs["database"]["index_name"] = select_index_name
                            faild_files = create_db(rag_configs, force_create=True)
                            if not faild_files:
                                st.toast(":green[成功存储到向量数据库]", icon="👏")
                            else:
                                _faild_files = [osp.basename(i) for i in faild_files]
                                _faild_files_str = "\n".join(_faild_files)
                                st.toast(
                                    f":red[以下文件存储失败:\n{_faild_files_str}]",
                                    icon="❌",
                                )

                                # 从数据库中删除
                                for file in faild_files:
                                    os.remove(file)
                            st.rerun()

            # 删除数据库
            else:
                st.warning("将删除此**数据库**及对应的**向量数据库**！:red[无法恢复！]")
                _in_cols = st.columns(3)
                key_a = _in_cols[1].button("确认删除", use_container_width=True)
                if key_a:
                    # 删除docs
                    docs_path = osp.join(db_docs_path, select_index_name)
                    shutil.rmtree(docs_path, ignore_errors=True)
                    # 删除vector
                    db_vector_path = rag_configs["database"]["db_vector_path"]
                    for ext in [".faiss", ".pkl"]:
                        _path = osp.join(db_vector_path, select_index_name + ext)
                        if osp.exists(_path):
                            os.remove(_path)
                    # 删除hash
                    hash_file_path = rag_configs["database"]["hash_file_path"]
                    hash_data = read_hash_file(hash_file_path)
                    if select_index_name in hash_data:
                        del hash_data[select_index_name]
                        save_hash_file(hash_data, hash_file_path)
                    st.toast(":green[删除成功]", icon="✅")
                    st.rerun()
        # st.divider()
        # st.button(
        #     "🔴 退出",
        #     use_container_width=True,
        #     on_click=return_from_db_setting,
        #     key="return_add_db_key",
        # )

    # 新建数据库
    else:
        st.markdown("##### 上传文件")
        st.text_input(
            "🔸新数据库名",
            placeholder="必须是大小写字母、数字和下划线(_)的组合",
            key="db_new_index_name_key",
        )
        st.file_uploader(
            "🔸添加文件",
            ["pdf", "csv", "txt", "xls", "xlsx", "doc", "docx", "json", "markdown"],
            accept_multiple_files=True,
            key="upload_new_index_docs_key",
        )

        st.markdown("##### 参数设置")
        ori_db_cfgs = st.session_state["ori_rag_cfgs"]["database"]
        _in_cols = st.columns(3)
        rag_configs["database"]["chunk_size"] = _in_cols[0].number_input(
            "ChunkSize",
            value=ori_db_cfgs["chunk_size"],
            min_value=16,
            step=1,
            help="💡切分文本块的大小",
        )
        overlap = _in_cols[1].number_input(
            "OverlapSize",
            value=ori_db_cfgs["chunk_overlap"],
            min_value=0,
            step=1,
            help="💡相邻文本块重合大小",
        )
        rag_configs["database"]["chunk_overlap"] = min(
            rag_configs["database"]["chunk_size"], overlap
        )
        rag_configs["database"]["merge_rows"] = _in_cols[2].number_input(
            "MergeRows",
            value=ori_db_cfgs["merge_rows"],
            min_value=1,
            step=1,
            help="💡CSV,XLS等一个文本块包含多少行数据",
        )
        
        st.markdown('')
        st.markdown('')
        _in_cols = st.columns([0.2, 0.6, 0.2])
        _in_cols[1].button(
            "👉 **保存到数据库**📑 👈",
            on_click=save_docs_to_db,
            key="save_docs_to_db-key",
            use_container_width=True,
        )
        # st.divider()
        # _in_cols = st.columns(2)
        # _in_cols[0].button(
        #     "✅ 保存到数据库",
        #     use_container_width=True,
        #     on_click=save_docs_to_db,
        #     key="save_docs_to_db-key",
        # )
        # _in_cols[1].button(
        #     "🔴 退出",
        #     use_container_width=True,
        #     on_click=return_from_db_setting,
        #     key="return_save_db_key",
        # )

     
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
    db_page()

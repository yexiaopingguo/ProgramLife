import time, json, os, os.path as osp, base64
from openai import OpenAI
from copy import deepcopy
import streamlit as st
from streamlit_pills import pills
from streamlit_option_menu import option_menu
from knownledge import RAG, init_models
from utils import print_colorful, Fore, random_icon
import streamlit_antd_components as sac
from summary_gen import read_document_content,read_documents,Summary
import re
import os


st.set_page_config(page_title="小Ai同学", page_icon="🐧", layout="wide")

from configs import llm_configs, rag_configs, SYSTEM_PROMPTS, ROBOT_AVATAR,summary_configs
from db_setting import db_page
from summary_file_setting import summary_page

# # 登录/注册
# from login import login_container
# if st.session_state.get("LOGIN_STATUS_FLAG") != "login":
#     login_container()
# if st.session_state.get("LOGIN_STATUS_FLAG") != "login":
#     st.stop()

# 修改top padding
st.markdown(
    """<style>
.stDeployButton {
            visibility: hidden;
        }
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

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


# main_bg = "assets/water-picture.jpg"  # stApp
# main_bg_ext = main_bg.split('.')[-1]
# st.markdown(
#     f"""
#         <style>
#         .stApp {{
#             background: url(data:image/{main_bg_ext};base64,{base64.b64encode(open(main_bg, "rb").read()).decode()});
#             background-size:cover;
#         }}

#         [data-testid="stBottomBlockContainer"] {{
#             background-color: gainsboro !important;
#             padding-bottom: 30px;
#         }}
#         </style>
#         """,
#     unsafe_allow_html=True,
# )


def siderbar_title(title: str):
    with st.sidebar:
        st.markdown(
            f"<div align='center'><strong><font size=6>{title}</font></div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div align='center'><font size=2></font></div>",
            unsafe_allow_html=True,
        )


def init_st():
    params = dict(
        # 当前会话的所有对话数据
        messages=[],
        # dialogue_history
        dialogue_history=[[]],
        # 初始化
        session_last_change_key=0,
        # 处于数据库处理流程
        IS_DB_MODE=False,
        IS_SU_MODE=False,
        IS_files_uploaded = False,
        IS_summary_MODE = False,
        # 当前对话检索到的doc
        now_search_docs=[],
    )
    for k, v in params.items():
        if k not in st.session_state:
            st.session_state[k] = v

    # 创建数据库
    os.makedirs(rag_configs["database"]["db_docs_path"], exist_ok=True)
    os.makedirs(rag_configs["database"]["db_vector_path"], exist_ok=True)


def clear_chat_history():
    st.toast("我们再聊聊吧🌿~", icon=ROBOT_AVATAR)
    if "messages" in st.session_state:
        del st.session_state.messages


def callback_session_change():
    """切换对话"""
    dialogue_history = st.session_state.dialogue_history
    change_key = st.session_state.session_change_key
    last_change_key = st.session_state.session_last_change_key
    if last_change_key == 0 and change_key != 0:
        st.session_state.dialogue_history[0] = {
            "messages": st.session_state.messages,
            "time": time.strftime("%y-%m-%d %H%M%S"),
            "configs": {},
        }
    st.session_state.messages = dialogue_history[change_key]["messages"]
    st.session_state.session_last_change_key = change_key

# rag数据库
def callback_db_setting():
    st.session_state["IS_DB_MODE"] = True
def callback_db_setting_finish():
    st.session_state["IS_DB_MODE"] = False
# 摘要生成数据库
def callback_summary_setting():
    st.session_state["IS_SU_MODE"] = True
def callback_summary_setting_finish():
    st.session_state["IS_SU_MODE"] = False
# 摘要生成模式开关
def callback_gen_summary_setting():
    st.session_state["IS_summary_MODE"] = True
def callback_gen_summary_setting_finish():
    st.session_state["IS_summary_MODE"] = False


def init_chat_history():
    with st.chat_message("assistant", avatar="assets/app-indicator.svg"):
        st.markdown("我是你的小助手，快开始跟我对话吧💭💭", unsafe_allow_html=True)
    if "messages" in st.session_state:
        for message in st.session_state.messages:
            if (
                message["role"] not in ["system", "tool"]
                and "tool_calls" not in message
            ):
                avatar = "🧑‍💻" if message["role"] == "user" else ROBOT_AVATAR
                with st.chat_message(message["role"], avatar=avatar):
                    st.markdown(message["content"], unsafe_allow_html=True)
    else:
        st.session_state.messages = []

    return st.session_state.messages


def run_chat(cfgs):
    messages = init_chat_history()
    client = OpenAI(
        api_key=cfgs["api_key"],
        base_url=cfgs["base_url"],
    )
    
   
 
   
    #chat和rag模式，手动输入prompt
    if  not st.session_state["IS_summary_MODE"]:
        if prompt := st.chat_input("Shift + Enter 换行, Enter 发送", key="chat_input_key") :
            with st.chat_message("user", avatar="🧑‍💻"):
                st.markdown(prompt, unsafe_allow_html=True)
            messages.append({"role": "user", "content": prompt})
            print_colorful(f"[user] {prompt}")

            with st.chat_message("assistant", avatar=ROBOT_AVATAR):
                placeholder = st.empty()

                # RAG 检索相关性信息
                ori_question = messages[-1]["content"]
                if cfgs["RAG"]:
                    print_colorful(
                        f'使用的知识库名{cfgs["index_name"]}', text_color=Fore.RED
                    )
                    rag_configs["database"]["index_name"] = cfgs["index_name"]
                    ensemble_retriever, reranker = init_models(configs=rag_configs)
                    with placeholder.status("正在检索知识库..."):
                        configs = {
                            "sample_top": cfgs["rag_topk"],
                            "sample_threshold": cfgs.get("rag_threshold", -100),
                        }
                        messages, related_docs = RAG(
                            messages,
                            ensemble_retriever,
                            reranker,
                            configs=configs,
                            show_info=True,
                        )
                    placeholder.empty()
            
                if not cfgs.get("stream", True):
                    with placeholder.status(
                        "让我思考一下吧🙇...", expanded=False
                    ) as status:
                        completion = client.chat.completions.create(
                            model=cfgs["model_name"],
                            messages=messages,
                            temperature=cfgs["temperature"],
                            stream=False,
                        )
                        # parser
                        response = completion.choices[0].message.content
                    placeholder.markdown(response, unsafe_allow_html=True)
                    print_colorful(f"[assistant] {response}")

                else:
                    msgs = []
                    for chunk_message in client.chat.completions.create(
                        model=cfgs["model_name"],
                        messages=messages,
                        temperature=cfgs["temperature"],
                        stream=True,
                    ):
                        tmp = chunk_message.choices[0].delta.content
                        if not tmp:
                            continue
                        msgs.append(tmp)
                        placeholder.markdown("".join(msgs), unsafe_allow_html=True)
                    response = "".join(msgs)
                    print_colorful(f"[assistant] {response}")

                # 知识库索引
                if cfgs["RAG"]:
                    # 只显示信息源
                    # if not st.session_state.now_search_docs:
                    #     _tr = lambda x: x[:6] + "..." + x[-6:] if len(x) > 12 else x
                    #     sources = [i.metadata for i in related_docs]
                    #     sources = list(
                    #         set([_tr(os.path.basename(i["source"])) for i in sources])
                    #     )
                    #     sources = [f"{idx}.{s}" for idx, s in enumerate(sources, 1)]
                    #     st.session_state.now_search_docs = sources
                    # else:
                    #     sources = st.session_state.now_search_docs

                    # st.markdown(f"")
                    # sac.tags(sources, size="sm", color="blue")

                    # 显示相关的文本和得分
                    cols = st.columns([0.9, 0.1])
                    with cols[0].expander("🔻知识库索引", expanded=False):
                        for doc in related_docs:
                            score = doc.metadata.get("score", None)
                            score = f'{score:.3f}' if score else ''
                            s = f':green[**{os.path.basename(doc.metadata["source"])}**] `{score}`\n'  #
                            d = re.sub(r"\s+", "\n>", doc.page_content.strip())
                            s += f"> {d}"
                            st.markdown(s)

            messages[-1]["content"] = ori_question
            messages.append({"role": "assistant", "content": response})
    #摘要生成模式，prompt固定 
    else:
        st.session_state["IS_summary_MODE"] = False
        prompt = " "
        if prompt:
            with st.chat_message("user", avatar="🧑‍💻"):
                st.markdown(prompt, unsafe_allow_html=True)
            messages.append({"role": "user", "content": prompt})
            print_colorful(f"[user] {prompt}")
            
            with st.chat_message("assistant", avatar=ROBOT_AVATAR):
                placeholder = st.empty()
                ori_question = messages[-1]["content"]
                if cfgs["summary"]:
                    with placeholder.status("正在生成摘要..."):
                        messages,docs = Summary(messages)
                    placeholder.empty()
            
            
                if not cfgs.get("stream", True):
                    with placeholder.status(
                        "让我思考一下吧🙇...", expanded=False
                    ) as status:
                        completion = client.chat.completions.create(
                            model=cfgs["model_name"],
                            messages=messages,
                            temperature=cfgs["temperature"],
                            stream=False,
                        )
                        # parser
                        response = completion.choices[0].message.content
                    placeholder.markdown(response, unsafe_allow_html=True)
                    print_colorful(f"[assistant] {response}")

                else:
                    msgs = []
                    for chunk_message in client.chat.completions.create(
                        model=cfgs["model_name"],
                        messages=messages,
                        temperature=cfgs["temperature"],
                        stream=True,
                    ):
                        tmp = chunk_message.choices[0].delta.content
                        if not tmp:
                            continue
                        msgs.append(tmp)
                        placeholder.markdown("".join(msgs), unsafe_allow_html=True)
                    response = "".join(msgs)
                    print_colorful(f"[assistant] {response}")

                # 知识库索引
                if cfgs["RAG"]:
                    # 只显示信息源
                    # if not st.session_state.now_search_docs:
                    #     _tr = lambda x: x[:6] + "..." + x[-6:] if len(x) > 12 else x
                    #     sources = [i.metadata for i in related_docs]
                    #     sources = list(
                    #         set([_tr(os.path.basename(i["source"])) for i in sources])
                    #     )
                    #     sources = [f"{idx}.{s}" for idx, s in enumerate(sources, 1)]
                    #     st.session_state.now_search_docs = sources
                    # else:
                    #     sources = st.session_state.now_search_docs

                    # st.markdown(f"")
                    # sac.tags(sources, size="sm", color="blue")

                    # 显示相关的文本和得分
                    cols = st.columns([0.9, 0.1])
                    with cols[0].expander("🔻知识库索引", expanded=False):
                        for doc in related_docs:
                            score = doc.metadata.get("score", None)
                            score = f'{score:.3f}' if score else ''
                            s = f':green[**{os.path.basename(doc.metadata["source"])}**] `{score}`\n'  #
                            d = re.sub(r"\s+", "\n>", doc.page_content.strip())
                            s += f"> {d}"
                            st.markdown(s)

            messages[-1]["content"] = ori_question
            messages.append({"role": "assistant", "content": response})

        if len(st.session_state.messages) > 1:
            # 优化去掉背景和label占位 anaconda3\Lib\site-packages\streamlit_pills\frontend\build
            # 设置：body background-color: rgba(240, 242, 246, 0) !important;
            # 设置：label min-height: 0rem;
            select_m = pills(
                label="",
                label_visibility="hidden",
                options=["请输入..", "清空对话", "新建对话"],
                index=0,
                icons=["🔅", "♻️", "🪄"],  #
                clearable=True,
            )
            if select_m == "新建对话":
                st.session_state.dialogue_history.append(
                    {
                        "messages": deepcopy(st.session_state.messages),
                        "time": time.strftime("%y-%m-%d %H%M%S"),
                        "configs": cfgs,
                    }
                )
                clear_chat_history()
                st.rerun()
            elif select_m == "清空对话":
                clear_chat_history()
                st.rerun()

            # _incols = st.columns(2)
            # _incols[0].button('请输入', key='sfsa')
            # _incols[1].button('清空对话', key='sfw')


def siderbar_params(configs):
    
    with st.sidebar:
        with st.expander("⚙️ **知识库配置**", expanded=True):
            if configs["RAG"]:
                if not st.session_state["IS_DB_MODE"]:
                    st.button(
                        "🧩 数据库管理",
                        help="✅ 点击打开数据库管理界面",
                        on_click=callback_db_setting,
                        key="into_db_setting_key1",
                        use_container_width=True,
                    )
                else:
                    cols = st.columns([0.6, 0.4])
                    cols[0].button(
                        "数据库管理",
                        help="✅ 点击打开数据库管理",
                        on_click=callback_db_setting,
                        key="into_db_setting_key2",
                        use_container_width=True,
                    )
                    cols[1].button(
                        "✅完成",
                        help="✅ 点击关闭数据库管理",
                        on_click=callback_db_setting_finish,
                        key="into_db_setting_return_key",
                        use_container_width=True,
                    )

                index_names = [
                    i
                    for i in os.listdir(rag_configs["database"]["db_docs_path"])
                    if not i.endswith("json")
                ]
                configs["index_name"] = st.selectbox("选择数据库", tuple(index_names))
                cols = st.columns(2)
                configs["rag_topk"] = cols[0].slider(
                    "检索数量", value=3, min_value=1, max_value=10, step=1
                )
                configs["rag_threshold"] = cols[1].slider(
                    "相似度阈值", value=0.0, min_value=0.0, max_value=3.0, step=0.01
                )
        with st.expander("⚙️ **摘要生成文件管理**", expanded=True):
                # 摘要生成模式
            if configs['summary']:
                if not st.session_state["IS_SU_MODE"]:
                    st.button(
                        "🖥️ 文件管理",
                        help="✅ 点击上传文件",
                        on_click=callback_summary_setting,
                        key="into_summary_setting_key1",
                        use_container_width=True,
                    )
                if  st.session_state["IS_SU_MODE"]:
                    cols = st.columns([0.6, 0.4])
                    cols[0].button(
                        "打开文件管理",
                        help="✅ 点击打开文件管理页面",
                        on_click=callback_summary_setting,
                        key="into_summary_setting_key2",
                        use_container_width=True,
                    )
                    cols[1].button(
                        "↩️返回",
                        help="✅ 点击关闭数据库管理",
                        on_click=callback_summary_setting_finish,
                        key="into_summary_setting_return_key",
                        use_container_width=True,
                    )

                
                
                

        # 对话历史
        dialogue_history = st.session_state.dialogue_history
        if dialogue_history:
            st.selectbox(
                f"📇 **历史对话**",
                tuple(range(len(dialogue_history))),
                index=0,  # len(dialogue_history) - 1
                on_change=callback_session_change,
                format_func=lambda x: (
                    f"{random_icon(x)}" + f" 历史对话 {x}" if x else "👉 当前对话"
                ),
                key="session_change_key",
                help="对话历史记录",
            )
        # model 选择
        model_name = st.selectbox(
            "🧸 **LLM-Model**",
            tuple(llm_configs),
            index=(
                list(llm_configs).index(configs["model_name"])
                if configs.get("model_name")
                else 0
            ),
            help="查看configs文件进行修改",
        )
        configs["model_name"] = model_name
        if "[" in model_name:
            configs["model_name"] = model_name[: model_name.rfind("[")]
        print_colorful(f"[model] {model_name}")

        # key
        api_key = st.text_input(
            "🗝️ **API_KEY**",
            value=llm_configs[model_name]["api_key"],
            help="支持openai格式的key",
            type="password",
        )
        base_url = st.text_input(
            "🔑 **BASE_URL**", value=llm_configs[model_name]["base_url"], help=""
        )
        configs["api_key"] = api_key
        configs["base_url"] = base_url

        # temperature
        temperature = st.slider(
            "⚖️ **temperature**", value=0.1, min_value=0.01, max_value=0.99, step=0.01
        )
        configs["temperature"] = temperature

        # stream
        # stream = pills(
        #     label="➿ 流式对话",
        #     options=["True", "False"],
        #     index=0,
        # )
        # configs["stream"] = stream == "True"
        stream = sac.buttons(
            [
                sac.ButtonsItem("打开", icon="fast-forward", color="green"),
                sac.ButtonsItem("关闭", icon="x-square"),
            ],
            label="➿ 流式对话",
            use_container_width=True,
            size="xs",
            variant="link",
            align="center",
        )
        configs["stream"] = stream == "打开"

        # -- 添加系统提示词 --
        system_prompts = SYSTEM_PROMPTS
        system_prompt_name = st.selectbox(
            "🔖 **系统提示词**",
            tuple(system_prompts),
            index=0,
            help="让大模型跟随指令进行回答",
        )
        system_prompt = st.text_area(
            "🧹 **编辑**", system_prompts[system_prompt_name], help="编辑系统提示词"
        )
        if "messages" in st.session_state:
            if (
                st.session_state.messages
                and st.session_state.messages[0]["role"] == "system"
            ):
                st.session_state.messages[0]["content"] = system_prompt
            else:
                st.session_state.messages.insert(
                    0, {"role": "system", "content": system_prompt}
                )
        else:
            st.session_state.messages = [{"role": "system", "content": system_prompt}]


def siderbar_bottom():
    with st.sidebar:
        # st.divider()
        text_contents = "\n".join(
            [
                "\n" * (m["role"] == "user") + f'<{m["role"]}>\t: {m["content"]}'
                for m in st.session_state.messages
            ]
        )
        name = time.strftime("%y-%m-%d %H%M%S")
        st.download_button(
            "🌝保存对话信息🐾",
            text_contents,
            file_name=f"messages {name}.txt",
            use_container_width=True,
        )

        # st.divider()
        # with st.expander("History", expanded=False):
        #     st.markdown("##### 对话列表")
        #     st.write(st.session_state.messages)


def main():
    siderbar_title("⭐智能问答系统")
    with st.sidebar:
        st.markdown('')
        st.markdown(
            f"<div align='left'><strong><font size=3>{'🛠️功能导航'}</font></div>",
            unsafe_allow_html=True,
        )
        
    
   
    init_st()

    with st.sidebar:
        selected = option_menu(
            None,
            ["对话模式", "知识库问答","摘要生成"],  # , "文件问答"
            icons=["activity", "database"],  # ,"file-earmark-medical"
            menu_icon="cast",
            default_index=0,
        )
    configs = {
        "RAG": (selected == "知识库问答" or st.session_state["IS_DB_MODE"]),
        "summary":(selected == '摘要生成' or  st.session_state["IS_SU_MODE"]),
        "SELECTED_MODE": selected,
    }

    siderbar_params(configs)

    if st.session_state["IS_DB_MODE"]:
        db_page()
        if selected == "对话模式":
            st.toast(":green[点击>✅完成< 退出数据库管理]", icon="🤗")
    elif st.session_state["IS_SU_MODE"]:
        summary_page()
        if selected == "对话模式":
            st.toast(":green[点击>↩️返回< 退出摘要生成文件管理]", icon="🤗")
    else:
        run_chat(configs)



    siderbar_bottom()


if __name__ == "__main__":
    main()

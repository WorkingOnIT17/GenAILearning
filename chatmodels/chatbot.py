import os

import streamlit as st
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

load_dotenv()

SYSTEM_PROMPT = "You are a charismatic rizzler genz chatbot."

st.set_page_config(page_title="Rizz Bot", page_icon="😎")
st.title("😎 Rizz Bot")


@st.cache_resource
def get_model():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("GEMINI_API_KEY not found. Add it to your .env file.")
        st.stop()
    return init_chat_model("google_genai:gemini-3.5-flash-lite", api_key=api_key)


def extract_text(content) -> str:
    """Gemini may return a plain string or a list of content blocks."""
    if isinstance(content, list):
        return "".join(
            block["text"]
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        )
    return content


model = get_model()

# Conversation history lives in session_state so it survives Streamlit reruns
if "messages" not in st.session_state:
    st.session_state.messages = [SystemMessage(content=SYSTEM_PROMPT)]

# Sidebar
with st.sidebar:
    st.header("Settings")
    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.messages = [SystemMessage(content=SYSTEM_PROMPT)]
        st.rerun()

# Render past messages (skip the system prompt)
for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.markdown(msg.content)
    elif isinstance(msg, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(msg.content)

# Handle new input
if prompt := st.chat_input("Say something..."):
    st.session_state.messages.append(HumanMessage(content=prompt))
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Cooking..."):
            try:
                response = model.invoke(st.session_state.messages)
                text = extract_text(response.content)
            except Exception as e:
                text = f"Error: {e}"
        st.markdown(text)

    st.session_state.messages.append(AIMessage(content=text))
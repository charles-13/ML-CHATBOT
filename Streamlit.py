import streamlit as st
import requests
import os
import shelve
from dotenv import load_dotenv

load_dotenv()

st.title("KNCMAP-TECHNOLOGIES")

USER_AVATAR = "👤"
BOT_AVATAR = "🤖"
API_KEY = os.getenv("KNCMAP_API_KEY")
MODEL_NAME = "mistralai/mistral-7b-instruct"

def load_chat_history():
    with shelve.open("chat_history") as db:
        return db.get("messages", [])

def save_chat_history(messages):
    with shelve.open("chat_history") as db:
        db["messages"] = messages

if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history()

with st.sidebar:
    if st.button("Delete Chat History"):
        st.session_state.messages = []
        save_chat_history([])

for message in st.session_state.messages:
    avatar = USER_AVATAR if message["role"] == "user" else BOT_AVATAR
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

if prompt := st.chat_input("How can I help?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(prompt)

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": MODEL_NAME,
        "messages": st.session_state.messages
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=body
        )
        result = response.json()
        answer = result['choices'][0]['message']['content']

        with st.chat_message("assistant", avatar=BOT_AVATAR):
            st.markdown(answer)

        st.session_state.messages.append({"role": "assistant", "content": answer})
        save_chat_history(st.session_state.messages)

    except Exception as e:
        with st.chat_message("assistant", avatar=BOT_AVATAR):
            st.markdown(f"❌ Error: {str(e)}")
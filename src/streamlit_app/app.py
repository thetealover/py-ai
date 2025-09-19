import os
import uuid
import requests
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
import logging

logger = logging.getLogger(__name__)

# --- App Configuration ---
st.set_page_config(page_title="AI Chat Agent", page_icon="🤖", layout="wide")

# --- Backend API URLs ---
BASE_API_URL = os.environ.get("API_URL", "http://localhost:8000")
STREAM_API_URL = f"{BASE_API_URL}/chat/stream"
HISTORY_API_URL = f"{BASE_API_URL}/chat/history"
USER_CHATS_API_URL = f"{BASE_API_URL}/chat/user"

# --- Session State Initialization ---
if "username" not in st.session_state:
    st.session_state.username = None
if "user_conversations" not in st.session_state:
    st.session_state.user_conversations = []
if "current_conversation_id" not in st.session_state:
    st.session_state.current_conversation_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []


# --- Helper Functions ---
def login(username):
    """Logs the user in and fetches their conversation history."""
    if username:
        st.session_state.username = username
        try:
            response = requests.get(f"{USER_CHATS_API_URL}/{username}")
            response.raise_for_status()
            st.session_state.user_conversations = response.json()
        except requests.RequestException as e:
            st.error(f"Could not load chat history: {e}")
            st.session_state.user_conversations = []
        st.rerun()


def logout():
    """Logs the user out and clears session state."""
    st.session_state.username = None
    st.session_state.user_conversations = []
    st.session_state.current_conversation_id = None
    st.session_state.messages = []
    st.rerun()


def start_new_chat():
    """Creates a new chat session ID based on the logged-in user."""
    new_id = f"{st.session_state.username}-{uuid.uuid4()}"
    st.session_state.current_conversation_id = new_id
    st.session_state.messages = []
    st.session_state.user_conversations.insert(
        0, {"conversation_id": new_id, "title": "New Chat"}
    )
    st.rerun()


def select_chat(conversation_id: str):
    """Fetches a chat's history and makes it active."""
    try:
        response = requests.get(f"{HISTORY_API_URL}/{conversation_id}")
        response.raise_for_status()
        messages_data = response.json()

        reloaded_history = []
        for msg_data in messages_data:
            if msg_data.get("type") == "human":
                reloaded_history.append(HumanMessage(**msg_data))
            elif msg_data.get("type") == "ai":
                reloaded_history.append(AIMessage(**msg_data))

        st.session_state.messages = reloaded_history
        st.session_state.current_conversation_id = conversation_id
        st.rerun()
    except requests.RequestException as e:
        st.error(f"Failed to load chat history: {e}")


# --- Main App Logic ---

if not st.session_state.username:
    st.title("Welcome to the AI Chat Agent 🤖")
    st.write("Please enter a username to begin or resume your sessions.")
    username_input = st.text_input("Username", key="username_input")
    if st.button("Login", type="primary"):
        login(username_input)
    st.stop()

st.title(f"🤖 AI Chat Agent")

with st.sidebar:
    st.header(f"Welcome, {st.session_state.username}!")
    if st.button("➕ New Chat", use_container_width=True):
        start_new_chat()

    st.divider()
    st.subheader("Your Conversations")

    if not st.session_state.user_conversations:
        st.write("No chats yet.")
    else:
        for conv in st.session_state.user_conversations:
            title = conv["title"][:30] + ("..." if len(conv["title"]) > 30 else "")
            if st.button(title, key=conv["conversation_id"], use_container_width=True):
                select_chat(conv["conversation_id"])

    st.divider()
    if st.button("Logout", use_container_width=True):
        logout()

if not st.session_state.current_conversation_id:
    st.info("Start a new chat or select one from your history.")
    st.stop()

for message in st.session_state.messages:
    with st.chat_message(message.type):
        st.write(message.content)

user_query = st.chat_input("Type your message here...")
if user_query:
    st.session_state.messages.append(HumanMessage(content=user_query))
    with st.chat_message("Human"):
        st.write(user_query)

    with st.chat_message("AI"):
        ai_response_placeholder = st.empty()
        full_response = ""

        try:
            with requests.post(
                STREAM_API_URL,
                json={
                    "message": user_query,
                    "session_id": st.session_state.current_conversation_id,
                },
                stream=True,
            ) as response:
                response.raise_for_status()
                for chunk in response.iter_content(chunk_size=None):
                    if chunk:
                        lines = chunk.decode("utf-8").split("\n\n")
                        for line in lines:
                            if line.startswith("data:"):
                                import json

                                data_str = line[len("data:") :].strip()
                                if data_str:
                                    try:
                                        data = json.loads(data_str)
                                        if data["type"] == "chunk":
                                            full_response += data["data"]
                                            ai_response_placeholder.markdown(
                                                full_response + "▌"
                                            )
                                        elif data["type"] == "tool_start":
                                            st.info(data["data"], icon="🛠️")
                                    except json.JSONDecodeError:
                                        logger.warning(
                                            f"Failed to decode JSON: {data_str}"
                                        )

                ai_response_placeholder.markdown(full_response)

            st.session_state.messages.append(AIMessage(content=full_response))

        except requests.exceptions.RequestException as e:
            st.error(f"Failed to connect to the AI service: {e}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

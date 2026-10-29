import streamlit as st
from src.chat_bot import chatBot

# Initialize chatbot once
@st.cache_resource
def load_bot():
    return chatBot()

bot = load_bot()

st.set_page_config(
    page_title="Samael",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 AI Assistant")

# Persona selection
persona = st.sidebar.selectbox(
    "Persona",
    ["assistant", "samael", "lucifer", "council"],
    index=3
)

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
if prompt := st.chat_input("Ask anything..."):

    # Show user message
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    # Stream assistant response
    with st.chat_message("assistant"):
        response = st.write_stream(bot.ask(prompt, persona))

    st.session_state.messages.append(
        {"role": "assistant", "content": response}
    )

if st.sidebar.button("Clear Chat"):
    st.session_state.messages = []
    bot.clear()           # Also clear the chatbot's internal history
    st.rerun()
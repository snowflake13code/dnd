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

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = bot.ask(prompt, persona)

        st.markdown(response)

    st.session_state.messages.append(
        {"role": "assistant", "content": response}
    )

if st.sidebar.button("Clear Chat"):
    st.session_state.messages = []
    st.rerun()
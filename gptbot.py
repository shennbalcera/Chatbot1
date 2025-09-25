import streamlit as st
from openai import OpenAI

# Initialize OpenAI client (make sure to set your API key)
client = OpenAI(api_key="YOUR_OPENAI_API_KEY")

# Streamlit UI setup
st.set_page_config(page_title="GPT-3.5 Chatbot", page_icon="🤖")

st.title("🤖 Chatbot with OpenAI GPT-3.5")
st.write("Ask me anything, and I'll respond using GPT-3.5.")

# Keep conversation history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "You are a helpful assistant."}]

# Display past messages
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"**🧑 You:** {msg['content']}")
    elif msg["role"] == "assistant":
        st.markdown(f"**🤖 Bot:** {msg['content']}")

# User input
user_input = st.text_input("Type your message:", "")

if st.button("Send"):
    if user_input:
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Get GPT-3.5 response
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=st.session_state.messages
        )

        reply = response.choices[0].message.content

        # Add bot response to history
        st.session_state.messages.append({"role": "assistant", "content": reply})

        # Refresh UI
        st.rerun()

# Reset button
if st.button("🔄 Reset Chat"):
    st.session_state.messages = [{"role": "system", "content": "You are a helpful assistant."}]
    st.rerun()

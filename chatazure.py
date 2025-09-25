import streamlit as st
import openai
import time

# --------------------------
# Azure OpenAI Configuration
# --------------------------

openai.api_type = "azure"
openai.api_base = "https://jvtay-mff428jo-eastus2.openai.azure.com/"
openai.api_version = "2025-01-01-preview"
openai.api_key = " "

DEPLOYMENT_NAME = "gpt-35-turbo"

# --------------------------
# Streamlit Page Config
# --------------------------
st.set_page_config(page_title="Copilot-Style Chatbot", page_icon="🤖", layout="wide")

# --------------------------
# Sidebar Information
# --------------------------
with st.sidebar:
    st.title("ℹ️ About this Chatbot")
    st.write("This AI chatbot is powered by **Azure OpenAI (GPT-35 Turbo)** and works like a personal Copilot.")
    st.markdown("""
    ✅ Summarize text  
    ✅ Explain technical concepts  
    ✅ Generate code snippets  
    ✅ Draft professional emails  
    ✅ Share motivational quotes  
    """)
    st.info("💡 Use quick action buttons for faster queries!")

# --------------------------
# Preset Quick Actions
# --------------------------
preset_options = [
    "Summarize this text.",
    "Explain a technical concept in simple terms.",
    "Generate a code snippet in Python.",
    "Draft an email to a client.",
    "Provide a motivational quote."
]

# --------------------------
# Conversation History
# --------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful AI assistant, like Microsoft Copilot. Always provide clear, concise, and actionable responses."}
    ]

# --------------------------
# Display Chat Messages (Styled Bubbles)
# --------------------------
st.markdown("<h1 style='text-align: center; color: #0078D7;'>🤖 Copilot-Style AI Chatbot</h1>", unsafe_allow_html=True)

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(
            f"<div style='background-color:#DCF8C6; padding:10px; border-radius:15px; margin:5px; text-align:right;'>"
            f"🧑 <b>You:</b> {msg['content']}</div>",
            unsafe_allow_html=True,
        )
    elif msg["role"] == "assistant":
        st.markdown(
            f"<div style='background-color:#E6E6FA; padding:10px; border-radius:15px; margin:5px; text-align:left;'>"
            f"🤖 <b>Bot:</b> {msg['content']}</div>",
            unsafe_allow_html=True,
        )

# --------------------------
# Quick Action Buttons
# --------------------------
st.markdown("### ⚡ Quick Actions")
cols = st.columns(len(preset_options))
for i, option in enumerate(preset_options):
    if cols[i].button(option):
        user_input = option
        st.session_state.messages.append({"role": "user", "content": user_input})

        try:
            with st.spinner("🤖 Bot is typing..."):
                time.sleep(1.2)
                response = openai.ChatCompletion.create(
                    deployment_id=DEPLOYMENT_NAME,
                    messages=st.session_state.messages,
                    temperature=0.7,
                    max_tokens=500
                )
            reply = response.choices[0].message["content"].strip()
        except Exception as e:
            reply = f"⚠️ Error: {e}"

        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

# --------------------------
# User Input Section
# --------------------------
st.markdown("### ✍️ Ask your own question")
user_input = st.text_input("Type your question here:")

if st.button("🚀 Send") and user_input.strip():
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        with st.spinner("🤖 Bot is typing..."):
            time.sleep(1.2)
            response = openai.ChatCompletion.create(
                deployment_id=DEPLOYMENT_NAME,
                messages=st.session_state.messages,
                temperature=0.7,
                max_tokens=500
            )
        reply = response.choices[0].message["content"].strip()
    except Exception as e:
        reply = f"⚠️ Error: {e}"

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()

# --------------------------
# Reset Chat Button
# --------------------------
if st.button("🔄 Reset Chat"):
    with st.spinner("Clearing chat..."):
        time.sleep(1)
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful AI assistant, like Microsoft Copilot. Always provide clear, concise, and actionable responses."}
    ]
    st.rerun()

# --------------------------
# Optional Stats Section
# --------------------------
st.markdown("---")
st.subheader("📊 Chat Stats")
st.metric("Total Messages", len(st.session_state.messages) - 1)
if len(st.session_state.messages) > 1:
    st.caption(f"🕒 Last interaction: {st.session_state.messages[-1]['role'].title()}")

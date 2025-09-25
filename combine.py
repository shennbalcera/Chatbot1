import streamlit as st
import openai
import time

# --------------------------
# Azure OpenAI Configuration (for AI chatbot)
# --------------------------
openai.api_type = "azure"
openai.api_base = "https://jvtay-mff428jo-eastus2.openai.azure.com/"
openai.api_version = "2025-01-01-preview"
openai.api_key = "MyKey"

DEPLOYMENT_NAME = "gpt-35-turbo"

# --------------------------
# Rule-Based Chatbot Function
# --------------------------
def rule_based_response(user_message):
    user_message = user_message.lower().strip()

    if user_message in ["hi", "hello", "hey", "start"]:
        return "👋 Hello! How can I help you today?"

    elif "create account" in user_message or user_message == "1":
        return "📝 You can create an account here: [TESDA Signup](https://e-tesda.gov.ph/login/signup.php)"

    elif "courses" in user_message or user_message == "2":
        return "📦 Sure! Explore the available courses here: [TESDA Courses](https://e-tesda.gov.ph/course)"

    elif "talk to agent" in user_message or user_message == "3":
        return "📞 Okay, I’m connecting you to our human support staff."

    else:
        return "❓ Sorry, I didn’t understand that. Please choose an option below."

# --------------------------
# Streamlit Page Config
# --------------------------
st.set_page_config(page_title="Combined Chatbot", page_icon="🤖", layout="wide")

# --------------------------
# Sidebar: Mode Selection
# --------------------------
with st.sidebar:
    st.title("🤖 Chatbot Settings")
    chatbot_mode = st.radio("Choose Chatbot Mode:", ["AI-Powered (Azure OpenAI)", "Rule-Based"])
    st.markdown("---")

    st.title("ℹ️ About")
    if chatbot_mode == "AI-Powered (Azure OpenAI)":
        st.write("This chatbot uses **Azure OpenAI GPT-35 Turbo**. It can:")
        st.markdown("""
        - ✅ Summarize text  
        - ✅ Explain technical concepts  
        - ✅ Generate code snippets  
        - ✅ Draft professional emails  
        - ✅ Share motivational quotes  
        """)
    else:
        st.write("This is a **Rule-Based Chatbot** with fixed responses. You can:")
        st.markdown("""
        - 👋 Greet the bot  
        - 📝 Create an account  
        - 📦 View courses  
        - 📞 Talk to a human agent  
        """)

# --------------------------
# Initialize Conversation History
# --------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# --------------------------
# Reset Chat Button
# --------------------------
if st.button("🔄 Reset Chat"):
    with st.spinner("Clearing chat..."):
        time.sleep(1)
    st.session_state.messages = []
    st.rerun()

# --------------------------
# Title
# --------------------------
st.markdown("<h1 style='text-align: center; color: #0078D7;'>🤖 Combined Chatbot</h1>", unsafe_allow_html=True)
st.write(f"You are chatting with: **{chatbot_mode}**")

# --------------------------
# Display Chat Bubbles
# --------------------------
for role, msg in st.session_state.messages:
    if role == "You":
        st.markdown(
            f"<div style='background-color:#DCF8C6; padding:10px; border-radius:15px; margin:5px; text-align:right;'>"
            f"🧑 <b>{role}:</b> {msg}</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"<div style='background-color:#E6E6FA; padding:10px; border-radius:15px; margin:5px; text-align:left;'>"
            f"🤖 <b>{role}:</b> {msg}</div>",
            unsafe_allow_html=True,
        )

# --------------------------
# Input Section
# --------------------------
st.markdown("### ✍️ Type your message or use quick actions:")
user_input = st.text_input("Type your message here:", "")

# Quick Actions (different per mode)
if chatbot_mode == "AI-Powered (Azure OpenAI)":
    preset_options = [
        "Summarize this text.",
        "Explain a technical concept in simple terms.",
        "Generate a code snippet in Python.",
        "Draft an email to a client.",
        "Provide a motivational quote."
    ]
    cols = st.columns(len(preset_options))
    for i, option in enumerate(preset_options):
        if cols[i].button(option):
            user_input = option
else:
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📝 Create Account"):
            user_input = "create account"
    with col2:
        if st.button("📦 Courses"):
            user_input = "courses"
    with col3:
        if st.button("📞 Talk to Agent"):
            user_input = "talk to agent"

# --------------------------
# Process User Input
# --------------------------
if user_input:
    st.session_state.messages.append(("You", user_input))

    with st.spinner("🤖 Bot is typing..."):
        time.sleep(1.2)

    if chatbot_mode == "AI-Powered (Azure OpenAI)":
        try:
            response = openai.ChatCompletion.create(
                deployment_id=DEPLOYMENT_NAME,
                messages=[{"role": "user", "content": user_input}],
                temperature=0.7,
                max_tokens=500
            )
            bot_reply = response.choices[0].message["content"].strip()
        except Exception as e:
            bot_reply = f"⚠️ Error: {e}"
    else:
        bot_reply = rule_based_response(user_input)

    st.session_state.messages.append(("Bot", bot_reply))
    st.rerun()

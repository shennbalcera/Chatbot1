import streamlit as st
import time

# --------------------------
# Rule-based chatbot function
# --------------------------
def chatbot_response(user_message):
    user_message = user_message.lower().strip()

    if user_message in ["hi", "hello", "hey", "start"]:
        return "👋 Hello! How can I help you today?"

    elif "create account" in user_message or user_message == "1":
        return "📝 You can create an account here: [TESDA Signup](https://e-tesda.gov.ph/login/signup.php)"

    elif "courses" in user_message or user_message == "2":
        return "📦 Sure! Explore the available courses here: [TESDA Courses](https://e-tesda.gov.ph/course)"

    elif "talk to agent" in user_message or user_message == "3":
        return "📞 Okay, I’m connecting you to our human support staff."

    elif "help" in user_message or "options" in user_message:
        return "🛠️ You can: \n1️⃣ Create an account \n2️⃣ Browse courses \n3️⃣ Talk to an agent"

    else:
        return "❓ Sorry, I didn’t understand that. Please try again or type 'help'."

# --------------------------
# Streamlit Page Config
# --------------------------
st.set_page_config(page_title="Simple Rule-Based Chatbot", page_icon="🤖", layout="wide")

# --------------------------
# Sidebar
# --------------------------
with st.sidebar:
    st.title("ℹ️ About this Chatbot")
    st.write("This is a simple **rule-based chatbot** built with Streamlit. You can:")
    st.markdown("""
    - 👋 Greet the bot  
    - 📝 Create an account  
    - 📦 View courses  
    - 📞 Talk to a human agent  
    """)
    st.success("💡 Tip: Try typing 'help' to see available options!")

# --------------------------
# Session State for Messages
# --------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [("Bot", "👋 Hi! Welcome to TESDA Chatbot. Type 'help' to see options.")]

# --------------------------
# Chat Input (auto-clearing)
# --------------------------
user_input = st.chat_input("Type your message here...")

if user_input:
    # Store user input immediately
    st.session_state.messages.append(("You", user_input))

    # Generate bot reply instantly (no need for st.rerun here)
    with st.spinner("Bot is typing..."):
        time.sleep(1.0)
    bot_reply = chatbot_response(user_input)
    st.session_state.messages.append(("Bot", bot_reply))

# --------------------------
# Display Conversation
# --------------------------
for role, msg in st.session_state.messages:
    if role == "You":
        st.markdown(
            f"<div style='background-color:#DCF8C6; padding:10px; border-radius:15px; "
            f"margin:5px; text-align:right;'>"
            f"🧑 <b>{role}:</b> {msg}</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"<div style='background-color:#E6E6FA; padding:10px; border-radius:15px; "
            f"margin:5px; text-align:left;'>"
            f"🤖 <b>{role}:</b> {msg}</div>",
            unsafe_allow_html=True,
        )

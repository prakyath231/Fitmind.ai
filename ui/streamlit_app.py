import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

st.set_page_config(
    page_title="FitMind",
    page_icon="💪",
    layout="centered"
)

# Custom CSS
st.markdown("""
<style>
.stApp { background-color: #0e0e10; color: #f2f0eb; }
.stChatMessage { background: #1a1a1a !important; border-radius: 12px !important; }
div[data-testid="stChatInput"] textarea { background: #1a1a1a !important; color: #f2f0eb !important; }
.stButton button { background: #b8f724 !important; color: #000 !important; border-radius: 20px !important; font-weight: 700 !important; border: none !important; }
h1, h2, h3 { color: #f2f0eb !important; }
.stCaption { color: #6b6b7a !important; }
</style>
""", unsafe_allow_html=True)

st.title("💪 FitMind")
st.caption("AI Fitness Trainer — powered by LangGraph + RAG + Mistral")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": """Hey Prakyath! I am your personal AI fitness coach. I know your complete training history and I am here to guide you.

**Try asking me:**
- Pull day today, planning lat pulldown, rows, bicep curls
- Had chicken rice bowl for lunch
- How am I doing this week?
- Plan my workouts for next week
- When did I last train chest?"""
    })

# Quick action buttons
st.markdown("**Quick actions:**")
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("💪 Session"):
        st.session_state.quick = "Pull day today, planning lat pulldown, seated row, face pulls, bicep curls"
with col2:
    if st.button("🥗 Nutrition"):
        st.session_state.quick = "Had chicken rice bowl for lunch"
with col3:
    if st.button("📅 Plan Week"):
        st.session_state.quick = "Plan my workouts for next week"
with col4:
    if st.button("📈 Progress"):
        st.session_state.quick = "How am I doing this week?"

st.divider()

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handle quick action button clicks
if "quick" in st.session_state:
    prompt = st.session_state.pop("quick")
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            from agents.graph import chat
            response = chat(prompt)
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

# Chat input
if prompt := st.chat_input("Message your coach..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            from agents.graph import chat
            response = chat(prompt)
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

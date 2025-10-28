import streamlit as st
from ai_agent import LocalAIAgent
from datetime import datetime
import json

st.set_page_config(page_title="JARVIS Desktop", page_icon="🤖", layout="wide")

@st.cache_resource
def get_agent():
    return LocalAIAgent()

agent = get_agent()

# Sidebar
st.sidebar.title("⚙️ Settings")
model = st.sidebar.selectbox("Model", options=[agent.default_model] + [m for m in agent.available_models if m != agent.default_model])
user_profile = st.sidebar.text_input("User (optional)", value="guest")
show_stats = st.sidebar.checkbox("Show stats", value=True)

st.sidebar.markdown("---")
st.sidebar.markdown("**Ollama Host:** `%s`" % (agent.ollama_url.rsplit('/api/',1)[0]))
st.sidebar.markdown("**Available Models:** ")
st.sidebar.code("\n".join(agent.available_models) or "-", language="text")

# Header
st.title("🤖 JARVIS Desktop App")
st.caption("Local AI with internet tools and logging")

# Chat area
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.container(border=True):
    for msg in st.session_state.messages:
        role = "🧑‍💻 You" if msg["role"] == "user" else f"🤖 AI ({msg.get('model','')})"
        st.markdown(f"**{role}:**\n\n{msg['content']}")
        if msg.get("internet_data"):
            with st.expander("🌐 Internet data"):
                st.json(msg["internet_data"])

with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_area("พิมพ์ข้อความของคุณ", height=120)
    submitted = st.form_submit_button("ส่ง", use_container_width=True)

if submitted and user_input.strip():
    st.session_state.messages.append({"role": "user", "content": user_input.strip()})
    with st.spinner("กำลังประมวลผล..."):
        result = agent.process_request(user_input.strip(), preferred_model=(model if model!=agent.default_model else None))
    st.session_state.messages.append({
        "role": "assistant",
        "content": result["ai_response"],
        "model": result.get("model_used"),
        "internet_data": result.get("internet_data")
    })
    st.rerun()

# Stats
if show_stats:
    st.markdown("---")
    st.subheader("📊 สถิติการทำงาน (จาก SQLite)")
    try:
        stats = agent.get_statistics()
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Requests", stats['overall']['total_requests'])
        col2.metric("Avg Response Time (s)", stats['overall']['avg_response_time'])
        col3.metric("Success Rate (%)", stats['overall']['success_rate'])
        st.json(stats)
    except Exception as e:
        st.warning(f"Stats error: {e}")

st.markdown("---")
st.caption("Tip: Run with: streamlit run desktop_app_streamlit.py")

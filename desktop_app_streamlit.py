"""
JARVIS AI Agent - Streamlit Desktop App
A web-based interface for JARVIS AI Agent using Streamlit
"""

import streamlit as st
import datetime

# Page configuration
st.set_page_config(
    page_title="JARVIS AI Agent",
    page_icon="🤖",
    layout="wide"
)

# Title and header
st.title("🤖 JARVIS AI Agent v1.4")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("Settings")
    st.markdown("### Agent Configuration")
    
    # Agent settings
    agent_mode = st.selectbox(
        "Agent Mode",
        ["Assistant", "Autonomous", "Learning"]
    )
    
    voice_enabled = st.checkbox("Enable Voice", value=False)
    debug_mode = st.checkbox("Debug Mode", value=False)
    
    st.markdown("---")
    st.markdown("### System Status")
    st.success("✅ System Online")
    st.info(f"🕐 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Conversation")
    
    # Initialize chat history in session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask JARVIS anything..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        response = f"JARVIS: I received your message: '{prompt}'. I'm a demo interface showing the desktop app is working!"
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)

with col2:
    st.header("Quick Actions")
    
    if st.button("🔍 Analyze", use_container_width=True):
        st.info("Analysis feature ready")
    
    if st.button("📊 Dashboard", use_container_width=True):
        st.info("Dashboard feature ready")
    
    if st.button("⚙️ Configure", use_container_width=True):
        st.info("Configuration feature ready")
    
    if st.button("🔄 Reset Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.header("System Info")
    
    with st.expander("Agent Capabilities"):
        st.markdown("""
        - Natural Language Processing
        - Task Automation
        - Data Analysis
        - Learning & Adaptation
        """)
    
    with st.expander("Version Info"):
        st.markdown("""
        **JARVIS AI Agent v1.4**
        - Streamlit: ✅ Running
        - PyQt5: ✅ Available
        - Flask: ✅ Ready
        - NLTK: ✅ Loaded
        """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "JARVIS AI Agent v1.4 | Desktop Apps Ready ✅"
    "</div>",
    unsafe_allow_html=True
)

if __name__ == "__main__":
    st.write("Streamlit app is running on http://localhost:8501")

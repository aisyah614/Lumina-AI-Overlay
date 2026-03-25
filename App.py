import streamlit as st
import streamlit.components.v1 as components
from streamlit_webrtc import webrtc_streamer
import time

# --- 1. THE 3-STATE EMOTION MAPPING ---
EMOTIONS = ["Neutral", "Happy", "Frustrated"]

# --- 2. SCREEN SHARE JAVASCRIPT (THE "OVERLAY" HOOK) ---
# This opens the native Chrome/Edge screen picker
st.markdown("""
    <script>
    async function startCapture() {
        try {
            const screenStream = await navigator.mediaDevices.getDisplayMedia({ video: true });
            const videoElement = document.getElementById('screen-preview');
            videoElement.srcObject = screenStream;
        } catch (err) {
            console.error("Error: " + err);
        }
    }
    </script>
""", unsafe_allow_html=True)

# --- 3. UI LAYOUT ---
st.set_page_config(page_title="Lumina AI: Perception Loop", layout="wide")

if 'start_time' not in st.session_state: st.session_state.start_time = None
if 'state' not in st.session_state: st.session_state.state = "Neutral"

st.title("🤖 Lumina AI: Empathetic Perception Loop")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Student Monitor")
    # REAL-TIME WEBCAM (Watching the 'Furrowed Brow')
    webrtc_streamer(key="lumina-face")
    
    # AUTHENTICATION & LAUNCH
    if st.button("🔐 Launch Perception Session", type="primary", use_container_width=True):
        st.session_state.active = True
        # Trigger the browser screen picker
        components.html("<script>startCapture();</script>", height=0)

    st.divider()
    st.info(f"**Current State:** {st.session_state.state}")

with col2:
    st.subheader("Shared Screen Analysis")
    # This is where the student's actual screen (Google/PDF) will appear
    st.markdown("""
        <video id="screen-preview" autoplay playsinline style="width:100%; border: 2px solid #4A90E2; border-radius: 10px;"></video>
    """, unsafe_allow_html=True)

    # --- THE 5-SECOND TEMPORAL LOGIC ---
    # (Simulated for your Demo)
    current_emo = "Frustrated" # This will come from your Keras model_logic.py
    
    if current_emo == "Frustrated":
        if st.session_state.start_time is None:
            st.session_state.start_time = time.time()
        
        elapsed = time.time() - st.session_state.start_time
        
        if elapsed >= 5:
            st.error("⚠️ 5-SECOND TRIGGER: Furrowed brow detected. Initiating Scaffolding...")
            st.markdown("### 💡 Lumina: I've simplified this screen for you!")
        else:
            st.warning(f"🔍 Analyzing brow contraction... ({int(elapsed)}s)")
    else:
        st.session_state.start_time = None
        st.success("🟢 Monitoring session...")

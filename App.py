import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import streamlit.components.v1 as components
from model_predict import VideoProcessor
import time

# --- 1. THEMES & CSS INJECTION ---
st.set_page_config(page_title="Lumina AI | Inclusive Education", layout="wide", page_icon="🤖")

def local_css():
    st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        color: #ffffff;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: rgba(48, 43, 99, 0.7) !important;
        border-right: 2px solid #ff00ff;
    }

    /* Buttons & Interactions */
    .stButton>button {
        background: linear-gradient(45deg, #ff00ff, #7000ff);
        color: white;
        border: none;
        border-radius: 20px;
        padding: 10px 25px;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 15px #ff00ff;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 10px 10px 0 0;
        color: #ff00ff !important;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ff00ff !important;
        color: white !important;
    }

    /* Scaffolding Card */
    .scaffold-card {
        background: rgba(255, 255, 255, 0.05);
        border-left: 5px solid #ff00ff;
        padding: 25px;
        border-radius: 15px;
        backdrop-filter: blur(10px);
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

local_css()

# --- 2. GLOBAL CONFIG & STATE ---
RTC_CONFIG = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})

if 'emo' not in st.session_state: st.session_state['emo'] = "Neutral"
if 'page' not in st.session_state: st.session_state['page'] = "Home"

# --- 3. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("💠 Lumina AI")
    st.write("---")
    if st.button("🏠 Project Home", use_container_width=True):
        st.session_state.page = "Home"
    if st.button("🚀 Start Study Session", use_container_width=True):
        st.session_state.page = "Session"
    st.write("---")
    st.caption("Researcher: Puteri Aisyah Sofia")
    st.caption("Supervisor: AP Dr. Ibrahim Venkat")

# --- 4. PAGE: HOME (Research Overview) ---
if st.session_state.page == "Home":
    st.title("✨ Enhancing Inclusive Education through Empathetic Assistive Technology")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
        ### 🎯 Research Objectives
        1. **Real-time Affective Monitoring:** Detecting cognitive barriers (frustration) using FER.
        2. **Adaptive Scaffolding:** Providing automated text simplification to reduce cognitive load.
        3. **Inclusive Design:** Supporting diverse learners, specifically in IGCSE Science subjects.
        """)
    with col_b:
        st.info("💡 **Methodology:** Using a Custom CNN trained on Neutral, Happy, and Frustrated classes to trigger just-in-time pedagogical support.")
    
    st.image("https://img.freepik.com/free-vector/ai-technology-brain-background-digital-transformation-concept_53876-117769.jpg", use_column_width=True)

# --- 5. PAGE: STUDY SESSION ---
elif st.session_state.page == "Session":
    st.header("🚀 Lumina Live Dashboard")
    
    col_cam, col_main = st.columns([1.2, 2])

    with col_cam:
        st.subheader("👤 Perception Engine")
        ctx = webrtc_streamer(
            key="lumina-perception-v3",
            mode=WebRtcMode.SENDRECV,
            video_processor_factory=VideoProcessor,
            rtc_configuration=RTC_CONFIG,
            media_stream_constraints={"video": True, "audio": False}
        )
        
        if ctx.video_processor:
            st.session_state['emo'] = ctx.video_processor.last_emotion
        
        status = st.session_state['emo']
        
        # Dynamic Status Display
        if status == "Frustrated":
            st.markdown(f'<h2 style="color:#ff00ff; text-shadow: 0 0 10px #ff00ff;">🚨 {status}</h2>', unsafe_allow_html=True)
            st.toast("Lumina: Scaffolding Triggered", icon="🔔")
        elif status == "Happy":
            st.markdown(f'<h2 style="color:#00ffff;">✨ {status}</h2>', unsafe_allow_html=True)
        else:
            st.markdown(f'<h2 style="color:#ffffff; opacity:0.6;">🌑 {status}</h2>', unsafe_allow_html=True)

    with col_main:
        t1, t2 = st.tabs(["🖥️ Desktop Share", "📖 Adaptive Scaffolding"])
        
        with t1:
            st.write("Share your IGCSE study materials here:")
            js_share = """
            <div style="background: #1a1a2e; padding: 10px; border-radius: 10px; border: 1px solid #ff00ff;">
                <button id="s" style="background:#ff00ff; color:white; border:none; padding:10px; border-radius:5px; width:100%; cursor:pointer;">🌐 Start Desktop Sharing</button>
                <video id="v" autoplay playsinline style="width:100%; margin-top:10px; border-radius:5px;"></video>
            </div>
            <script>
            const btn = document.getElementById('s'); const video = document.getElementById('v');
            btn.onclick = async () => {
                const stream = await navigator.mediaDevices.getDisplayMedia({video: true});
                video.srcObject = stream;
            };
            </script>
            """
            components.html(js_share, height=400)

        with t2:
            if status == "Frustrated":
                st.markdown("""
                <div class="scaffold-card">
                    <h3>🤖 Lumina Simplified Guide: Photosynthesis</h3>
                    <p><b>1. Simple Definition:</b> Plants make food using sunlight.</p>
                    <p><b>2. Key Ingredient:</b> Chlorophyll (The green stuff).</p>
                    <p><b>3. The Test:</b> Starch turns <b>Iodine Blue/Black</b>.</p>
                    <hr style="border-color:#ff00ff;">
                    <p><small>Scaffolding level: High (Simplified for cognitive ease)</small></p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("System is monitoring. Scaffolding will generate here if you need help.")

# --- 6. FOOTER ---
st.write("---")
st.caption("Lumina AI Framework | UTP Applied Computing | Doha, Qatar")

import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import streamlit.components.v1 as components
from model_predict import VideoProcessor
import time

# --- 1. RESEARCH & THEME CONFIGURATION ---
EMOTION_LABELS = {0: 'Neutral', 1: 'Happy', 2: 'Frustrated'}
RTC_CONFIG = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})

st.set_page_config(page_title="Lumina AI | Adaptive Support", layout="wide", page_icon="🤖")

# --- CUSTOM CSS: PURPLE NIGHT & WHITE BORDERS ---
def apply_custom_theme():
    st.markdown("""
    <style>
    /* 1. Purplish-Blue Night Background */
    .stApp {
        background: linear-gradient(135deg, #1a0a2e, #110e1a, #0d001a);
        color: #ffffff;
    }
    
    /* 2. Crisp White Borders for UI Blocks */
    [data-testid="stVerticalBlock"] > div:has(div.stMarkdown) {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 30px;
        border: 2px solid #ffffff; /* Explicit White Border */
        box-shadow: 0 10px 40px rgba(255, 255, 255, 0.05);
    }

    /* 3. Pop-out Pink Buttons */
    .stButton>button {
        background: linear-gradient(45deg, #FF1493, #D02090);
        color: white;
        border: 2px solid #ffffff;
        border-radius: 50px;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 20px #FF1493;
    }

    /* Tabs Styling (Lavender to Pink) */
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 10px 10px 0 0;
        color: #e6e6fa !important;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #D02090 !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

apply_custom_theme()

# --- 2. GLOBAL STATE ---
if 'emo' not in st.session_state: st.session_state['emo'] = "Neutral"

# --- 3. UI LAYOUT ---
# Removed: The researcher text is gone, only the title remains.
st.title("🤖 Lumina AI: Auto-Adaptive Inclusive Education")

left_panel, right_panel = st.columns([1.2, 2])

with left_panel:
    st.subheader("👤 Student tracker")
    
    ctx = webrtc_streamer(
        key="lumina-perception-v2",
        mode=WebRtcMode.SENDRECV,
        video_processor_factory=VideoProcessor,
        rtc_configuration=RTC_CONFIG,
        media_stream_constraints={"video": True, "audio": False}
    )
    
    # Secure state update from processor
    if ctx.video_processor:
        st.session_state['emo'] = ctx.video_processor.last_emotion
    
    status = st.session_state['emo']
    st.write("---")
    
    # DYNAMIC MASCOT: Changes face based on detected state
    # If Frustrated, Lumina looks worried (Red robot icon)
    # If Happy, Lumina looks happy (Green robot icon)
    # If Neutral, Lumina looks friendly (Blue robot icon)
    mascot_code = "4712027" if status == "Frustrated" else ("4712035" if status == "Happy" else "4712010")
    st.image(f"https://cdn-icons-png.flaticon.com/512/4712/{mascot_code}.png", width=120)

    if status == "Frustrated":
        st.error(f"Status: {status} (Cognitive Barrier detected)")
    elif status == "Happy":
        st.success(f"Status: {status}")
    else:
        st.info(f"Status: {status}")

with right_panel:
    tab_label = "💡 Simplified Notes" if status == "Frustrated" else "Lumina Notes"
    t1, t2 = st.tabs(["🖥️ Desktop View", tab_label])
    
    with t1:
        st.write("Share your complex study materials here for monitoring:")
        # Integrated JS Desktop Sharing (from previous versions)
        js_code = """
        <div style="background: rgba(0,0,0,0.3); padding: 15px; border-radius: 12px; border: 1px solid #ffffff;">
            <div style="display: flex; gap: 10px; margin-bottom: 10px;">
                <button id="s" style="background: #27ae60; border: none; padding: 10px; border-radius: 5px; color: white; cursor: pointer; flex: 1; font-weight: bold;">🌐 Share Desktop</button>
                <button id="stop" style="background: #c0392b; border: none; padding: 10px; border-radius: 5px; color: white; cursor: pointer; flex: 1; font-weight: bold; display: none;">🛑 Stop</button>
            </div>
            <video id="v" autoplay playsinline style="width: 100%; height: 320px; border-radius: 8px; background: #000;"></video>
        </div>
        <script>
        const btnS = document.getElementById('s'); const btnE = document.getElementById('stop');
        const video = document.getElementById('v'); let stream = null;
        btnS.onclick = async () => {
            stream = await navigator.mediaDevices.getDisplayMedia({video: true});
            video.srcObject = stream; btnS.style.display='none'; btnE.style.display='block';
        };
        btnE.onclick = () => {
            if(stream) stream.getTracks().forEach(t => t.stop());
            video.srcObject = null; btnS.style.display='block'; btnE.style.display='none';
        };
        </script>
        """
        components.html(js_code, height=450)

    with t2:
        if status == "Frustrated":
            st.warning("🤖 Lumina: I've processed the complex information for you!")
            st.markdown("""
            ### 📖 Simplified Notes: Photosynthesis
            * **Concept:** Plants turn sunlight into "Energy Food".
            * **Key Component:** They use Green pigment (Chlorophyll) to capture light.
            * **Stored Energy:** The energy is stored as starch (Test with Iodine!).
            """)
        else:
            st.info("Desktop content will be automatically simplified here if you look confused while studying.")

st.sidebar.caption("Puteri Aisyah Sofia | ID: 25014776 | MSc Applied Computing | UTP")

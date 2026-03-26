import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import streamlit.components.v1 as components
from model_predict import VideoProcessor

# --- 1. AESTHETIC CONFIGURATION ---
st.set_page_config(page_title="Lumina AI | Study Sanctuary", layout="wide")

def apply_custom_styles():
    # Link to your Anime Classroom background
    bg_url = "https://raw.githubusercontent.com/AisyahSofia/Lumina-AI/main/classroom_bg.jpg"
    
    st.markdown(f"""
    <style>
    /* Background setup */
    .stApp {{
        background-image: linear-gradient(rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.1)), url("{bg_url}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    /* Glass Container Effect */
    [data-testid="stVerticalBlock"] > div:has(div.stMarkdown) {{
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(12px);
        border-radius: 25px;
        padding: 30px;
        border: 1px solid rgba(255, 255, 255, 0.4);
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
    }}

    /* Pretty Pink Buttons */
    .stButton>button {{
        background: linear-gradient(90deg, #FF69B4, #DA70D6) !important;
        color: white !important;
        border: none !important;
        border-radius: 20px !important;
        padding: 12px 30px !important;
        font-weight: bold !important;
        transition: 0.3s ease;
    }}
    .stButton>button:hover {{
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(255, 105, 180, 0.4);
    }}

    /* Titles */
    h1, h2, h3 {{
        color: #4B0082 !important;
        font-family: 'Helvetica Neue', sans-serif;
        text-shadow: 1px 1px 2px rgba(255,255,255,0.8);
    }}
    </style>
    """, unsafe_allow_html=True)

apply_custom_styles()

# --- 2. FIXED RTC CONFIG ---
RTC_CONFIG = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})

if 'emo' not in st.session_state: 
    st.session_state['emo'] = "Neutral"

# --- 3. UI LAYOUT ---
st.title("☀️ Lumina AI: Your Learning Sanctuary")
st.caption("Researcher: Puteri Aisyah Sofia | MSc Applied Computing | UTP")

col_cam, col_main = st.columns([1, 2.2])

with col_cam:
    st.subheader("📸 Focus Tracker")
    # Fixed the constraints and RTC config braces here:
    ctx = webrtc_streamer(
        key="lumina-v16-final",
        mode=WebRtcMode.SENDRECV,
        video_processor_factory=VideoProcessor,
        rtc_configuration=RTC_CONFIG,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True
    )
    
    if ctx.video_processor:
        st.session_state['emo'] = ctx.video_processor.last_emotion
    
    status = st.session_state['emo']
    
    # Dynamic Status Pill
    status_color = "#FFB6C1" if status == "Frustrated" else "#E0FFFF"
    st.markdown(f"""
        <div style="background:{status_color}; padding:15px; border-radius:15px; text-align:center; font-weight:bold; color:#4B0082;">
            Current State: {status}
        </div>
    """, unsafe_allow_html=True)

with col_main:
    tab1, tab2 = st.tabs(["🖥️ Study Desktop", "💡 Lumina Notes"])
    
    with tab1:
        # Desktop Share with Working STOP button
        share_js = """
        <div style="background: rgba(255,255,255,0.7); padding: 20px; border-radius: 20px; border: 3px dashed #DA70D6;">
            <div style="display: flex; gap: 10px; margin-bottom: 20px;">
                <button id="s" style="flex: 2; padding: 15px; background: #9370DB; color: white; border: none; border-radius: 12px; cursor: pointer; font-weight: bold;">🌐 Share Desktop</button>
                <button id="e" style="flex: 1; padding: 15px; background: #FF4500; color: white; border: none; border-radius: 12px; cursor: pointer; font-weight: bold; display: none;">🛑 Stop</button>
            </div>
            <video id="v" autoplay playsinline style="width: 100%; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);"></video>
        </div>
        <script>
        const btnS = document.getElementById('s'); const btnE = document.getElementById('e');
        const v = document.getElementById('v'); let stream = null;
        btnS.onclick = async () => {
            stream = await navigator.mediaDevices.getDisplayMedia({video: true});
            v.srcObject = stream;
            btnS.style.display='none'; btnE.style.display='inline';
            stream.getVideoTracks()[0].onended = () => stop();
        };
        const stop = () => {
            if(stream) stream.getTracks().forEach(t => t.stop());
            v.srcObject = null; btnS.style.display='inline'; btnE.style.display='none';
        }
        btnE.onclick = stop;
        </script>
        """
        components.html(share_js, height=480)

    with tab2:
        if status == "Frustrated":
            st.markdown("""
            <div style="background: white; padding: 25px; border-radius: 20px; border-left: 10px solid #FF1493; box-shadow: 0 5px 15px rgba(0,0,0,0.05);">
                <h3 style="margin-top:0; color:#C71585;">🌸 Lumina's Sunbeam Help</h3>
                <p style="font-size:1.1rem;">It's okay to feel stuck! Let's simplify this concept:</p>
                <ul>
                    <li><b>Photosynthesis:</b> Plants turn sunlight into "Energy Food".</li>
                    <li><b>Chlorophyll:</b> The green chef inside the leaf. chef!</li>
                    <li><b>Starch:</b> The food that is stored (Test with Iodine!).</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("The system is monitoring your study session. Scaffolding notes will appear here if you get frustrated!")

st.sidebar.markdown("---")
st.sidebar.caption("Lumina AI Framework | UTP | 2026")

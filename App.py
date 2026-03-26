import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import streamlit.components.v1 as components
from model_predict import VideoProcessor

st.set_page_config(page_title="Lumina AI | Study Sanctuary", layout="wide")

# --- ANIME CLASSROOM STYLING ---
def apply_classroom_theme():
    # Replace the URL below with your actual background image link if you host it elsewhere
    bg_image = "https://raw.githubusercontent.com/AisyahSofia/Lumina-AI/main/classroom_bg.jpg" 
    
    st.markdown(f"""
    <style>
    /* Background Image with Overlay */
    .stApp {{
        background-image: linear-gradient(rgba(255, 255, 255, 0.2), rgba(255, 255, 255, 0.2)), url("{bg_image}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    
    /* Glassmorphism Cards */
    [data-testid="stVerticalBlock"] > div:has(div.stMarkdown) {{
        background: rgba(255, 255, 255, 0.75);
        backdrop-filter: blur(8px);
        border-radius: 20px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
    }}

    /* Pop-out Pink Buttons */
    .stButton>button {{
        background: linear-gradient(45deg, #FF69B4, #DA70D6) !important;
        color: white !important;
        border: none !important;
        border-radius: 15px !important;
        padding: 12px 24px !important;
        font-weight: bold !important;
        box-shadow: 0 4px 15px rgba(218, 112, 214, 0.4);
    }}

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {{ background-color: transparent; }}
    .stTabs [data-baseweb="tab"] {{
        background-color: rgba(255, 255, 255, 0.5);
        border-radius: 10px 10px 0 0;
        margin-right: 5px;
        color: #8A2BE2 !important;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: #DA70D6 !important;
        color: white !important;
    }}

    h1, h2 {{ color: #4B0082 !important; text-shadow: 1px 1px 2px white; }}
    </style>
    """, unsafe_allow_html=True)

apply_classroom_theme()

# --- APP LOGIC ---
RTC_CONFIG = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})
if 'emo' not in st.session_state: st.session_state['emo'] = "Neutral"

st.title("☀️ Lumina AI: Your Learning Sanctuary")

l_col, r_col = st.columns([1, 2.2])

with l_col:
    st.subheader("📸 Focus Tracker")
    # Camera Stream
    ctx = webrtc_streamer(
        key="anime-study-cam",
        mode=WebRtcMode.SENDRECV,
        video_processor_factory=VideoProcessor,
        rtc_configuration=RTC_CONFIG,
        media_stream_constraints={{"video": True, "audio": False}},
        async_processing=True
    )
    
    if ctx.video_processor:
        st.session_state['emo'] = ctx.video_processor.last_emotion
    
    status = st.session_state['emo']
    
    # Status Indicator Card
    if status == "Frustrated":
        st.markdown(f'<div style="background:#FFB6C1; padding:10px; border-radius:15px; text-align:center; color:#8B0000; font-weight:bold;">Status: {status} (Help is on the way!)</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="background:#E6E6FA; padding:10px; border-radius:15px; text-align:center; color:#4B0082;">Status: {status}</div>', unsafe_allow_html=True)

with r_col:
    tab1, tab2 = st.tabs(["🖥️ Study Desktop", "💡 Lumina Notes"])
    
    with tab1:
        # FIXED DESKTOP SHARE WITH STOP BUTTON
        share_js = """
        <div style="background: rgba(255,255,255,0.6); padding: 15px; border-radius: 15px;">
            <div style="display: flex; gap: 10px; margin-bottom: 15px;">
                <button id="s" style="flex: 1; padding: 12px; background: #9370DB; color: white; border: none; border-radius: 10px; cursor: pointer;">🌐 Share Screen</button>
                <button id="e" style="flex: 1; padding: 12px; background: #FF6347; color: white; border: none; border-radius: 10px; cursor: pointer; display: none;">🛑 Stop</button>
            </div>
            <video id="v" autoplay playsinline style="width: 100%; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);"></video>
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
        components.html(share_js, height=450)

    with tab2:
        if status == "Frustrated":
            st.markdown("""
            <div style="background: white; padding: 20px; border-radius: 15px; border-left: 10px solid #FF69B4;">
                <h3 style="margin-top:0;">🌸 Lumina's Quick Guide</h3>
                <p><b>Photosynthesis Simplified:</b></p>
                <ul>
                    <li>Plants need <b>Light</b> + <b>Water</b>.</li>
                    <li>They use <b>Chlorophyll</b> to catch energy.</li>
                    <li><b>Result:</b> They make starch (plant food).</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.write("You're doing great! Keep focusing on your notes.")

st.sidebar.markdown("---")
st.sidebar.caption("Puteri Aisyah Sofia | ID: 25014776")

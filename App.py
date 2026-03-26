import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import streamlit.components.v1 as components
from model_predict import VideoProcessor

st.set_page_config(page_title="Lumina AI | Happy Learning", layout="wide")

# --- CUSTOM "HAPPY" STYLING ---
def apply_happy_theme():
    st.markdown("""
    <style>
    /* Vibrant Sunny Gradient Background */
    .stApp {
        background: linear-gradient(to bottom, #87CEEB 0%, #FFB6C1 50%, #FFFACD 100%);
        background-attachment: fixed;
    }
    
    /* Pop-out Scaffolding Card */
    .scaffold-card {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 20px;
        padding: 25px;
        border-bottom: 8px solid #FF69B4;
        box-shadow: 0 10px 30px rgba(255, 20, 147, 0.2);
        color: #333;
    }

    /* Buttons that Pop */
    .stButton>button {
        background: #FF1493 !important;
        color: white !important;
        border-radius: 50px !important;
        border: 4px solid #FFF !important;
        font-size: 20px !important;
        font-weight: bold !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.4) !important;
        backdrop-filter: blur(10px);
    }
    
    h1, h2, h3 { color: #D02090 !important; font-family: 'Comic Sans MS', cursive; }
    </style>
    """, unsafe_allow_html=True)

apply_happy_theme()

# --- APP LOGIC ---
RTC_CONFIG = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})

if 'emo' not in st.session_state: st.session_state['emo'] = "Neutral"

st.title("☀️ Lumina AI: Your Study Buddy")
st.markdown("### Creating a brighter future for every student!")

l_col, r_col = st.columns([1, 2.2])

with l_col:
    st.subheader("📸 Your Smile Tracker")
    # Camera Fix: Specific key and SENDRECV mode
    ctx = webrtc_streamer(
        key="lumina-active-cam",
        mode=WebRtcMode.SENDRECV,
        video_processor_factory=VideoProcessor,
        rtc_configuration=RTC_CONFIG,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True
    )
    
    if ctx.video_processor:
        st.session_state['emo'] = ctx.video_processor.last_emotion
    
    emo = st.session_state['emo']
    st.markdown(f"<h1 style='text-align:center;'>{ '😊' if emo=='Happy' else ('🤔' if emo=='Frustrated' else '😐') }</h1>", unsafe_allow_html=True)

with r_col:
    tab1, tab2 = st.tabs(["🖥️ Desktop Share", "🌈 Learning Support"])
    
    with tab1:
        # FIXED: Desktop Share with Share and Stop buttons
        share_js = """
        <div style="background: white; padding: 20px; border-radius: 20px; border: 4px dashed #FF69B4;">
            <div style="display: flex; gap: 10px; margin-bottom: 10px;">
                <button id="startBtn" style="flex: 1; padding: 15px; background: #32CD32; color: white; border: none; border-radius: 10px; cursor: pointer; font-weight: bold;">🌐 Share Desktop</button>
                <button id="stopBtn" style="flex: 1; padding: 15px; background: #FF4500; color: white; border: none; border-radius: 10px; cursor: pointer; font-weight: bold; display: none;">🛑 Stop</button>
            </div>
            <video id="v" autoplay playsinline style="width: 100%; border-radius: 10px; background: #eee;"></video>
        </div>
        <script>
        const sBtn = document.getElementById('startBtn');
        const eBtn = document.getElementById('stopBtn');
        const v = document.getElementById('v');
        let stream = null;

        sBtn.onclick = async () => {
            stream = await navigator.mediaDevices.getDisplayMedia({video: true});
            v.srcObject = stream;
            sBtn.style.display='none'; eBtn.style.display='inline';
            stream.getVideoTracks()[0].onended = () => stopStream();
        };

        function stopStream() {
            if(stream) stream.getTracks().forEach(t => t.stop());
            v.srcObject = null;
            sBtn.style.display='inline'; eBtn.style.display='none';
        }
        eBtn.onclick = stopStream;
        </script>
        """
        components.html(share_js, height=450)

    with tab2:
        if emo == "Frustrated":
            st.markdown(f"""
            <div class="scaffold-card">
                <h2 style="margin-top:0;">🌻 Lumina's Sunbeam Help:</h2>
                <p style="font-size: 1.2rem;">Don't worry, Puteri! Let's make this easier:</p>
                <ul>
                    <li><b>Main Idea:</b> Plants drink sunlight to make energy.</li>
                    <li><b>Key Part:</b> The Green pigment (Chlorophyll) is the chef!</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align:center; margin-top:50px; opacity:0.6;">
                <h3>Everything looks great! Keep up the good work! 🌟</h3>
            </div>
            """, unsafe_allow_html=True)

st.divider()
st.caption("Lumina AI Framework | Puteri Aisyah Sofia | Doha, Qatar")

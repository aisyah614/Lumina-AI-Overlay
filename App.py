import numpy as np
import cv2
import streamlit as st
import streamlit.components.v1 as components
import os
import av
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration

# --- 1. RESEARCH CONFIGURATION ---
EMOTION_LABELS = {0: 'Frustrated', 1: 'Happy', 2: 'Neutral'}
RTC_CONFIG = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})

st.set_page_config(page_title="Lumina AI: Remote Assist", layout="wide", page_icon="🤖")

# --- 2. MODEL LOADING ---
@st.cache_resource
def load_lumina_model():
    try:
        import tensorflow as tf
        if os.path.exists('model.h5'):
            return tf.keras.models.load_model('model.h5', compile=False)
    except:
        return None
    return None

model = load_lumina_model()

# --- 3. PERCEPTION MODULE ---
class LuminaPerception:
    def __init__(self):
        self.history = []
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

        detected = "Neutral"
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (74, 144, 226), 2)
            if model:
                roi = cv2.resize(gray[y:y+h, x:x+w], (48, 48)) / 255.0
                roi = roi.reshape(1, 48, 48, 1)
                preds = model.predict(roi, verbose=0)[0]
                detected = EMOTION_LABELS[np.argmax(preds)]

            self.history.append(detected)
            if len(self.history) > 15: self.history.pop(0)
            st.session_state['emotion'] = max(set(self.history), key=self.history.count)
            
        return av.VideoFrame.from_ndarray(img, format="bgr24")

# --- 4. REMOTE CONTROL COMPONENT (With Stop Button) ---
def remote_control_interface():
    js_code = """
    <div style="background: #121212; padding: 15px; border-radius: 12px; color: #fff; font-family: sans-serif;">
        <div style="display: flex; gap: 10px; margin-bottom: 10px;">
            <button id="share" style="background: #27ae60; border: none; padding: 8px 15px; border-radius: 5px; color: white; cursor: pointer; font-weight: bold;">🌐 Start Sharing</button>
            <button id="stop" style="background: #c0392b; border: none; padding: 8px 15px; border-radius: 5px; color: white; cursor: pointer; font-weight: bold; display: none;">🛑 Stop Sharing</button>
            <span id="status" style="font-size: 12px; color: #bdc3c7; margin-top: 8px;">Status: Standby</span>
        </div>
        <div id="container" style="position: relative; width: 100%; height: 420px; background: #000; border: 2px solid #333; border-radius: 8px; overflow: hidden;">
            <video id="remoteVideo" autoplay playsinline style="width: 100%; height: 100%; object-fit: contain;"></video>
            <div id="overlay" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; cursor: crosshair;"></div>
        </div>
    </div>

    <script>
    const shareBtn = document.getElementById('share');
    const stopBtn = document.getElementById('stop');
    const status = document.getElementById('status');
    const video = document.getElementById('remoteVideo');
    let currentStream = null;

    shareBtn.addEventListener('click', async () => {
        try {
            currentStream = await navigator.mediaDevices.getDisplayMedia({ video: true });
            video.srcObject = currentStream;
            
            // UI Toggle
            shareBtn.style.display = 'none';
            stopBtn.style.display = 'inline-block';
            status.innerText = "Status: Transmitting...";
            status.style.color = "#2ecc71";

            // Handle browser-native "Stop Sharing" bar
            currentStream.getVideoTracks()[0].onended = stopScreenShare;

        } catch (err) {
            console.error("Error: " + err);
        }
    });

    function stopScreenShare() {
        if (currentStream) {
            currentStream.getTracks().forEach(track => track.stop());
            video.srcObject = null;
            currentStream = null;
        }
        
        // Reset UI
        shareBtn.style.display = 'inline-block';
        stopBtn.style.display = 'none';
        status.innerText = "Status: Standby";
        status.style.color = "#bdc3c7";
    }

    stopBtn.addEventListener('click', stopScreenShare);
    </script>
    """
    components.html(js_code, height=520)

# --- 5. MAIN UI ---
def run():
    st.title("🤖 Lumina AI: Advanced Collaborative Learning")

    if 'emotion' not in st.session_state: st.session_state['emotion'] = "Neutral"

    col1, col2 = st.columns([1, 1.8])

    with col1:
        st.subheader("👤 Student Feed")
        webrtc_streamer(
            key="cam",
            mode=WebRtcMode.SENDRECV,
            video_processor_factory=LuminaPerception,
            rtc_configuration=RTC_CONFIG,
            media_stream_constraints={"video": True, "audio": False}
        )
        
        st.divider()
        emo = st.session_state['emotion']
        if emo == "Frustrated":
            st.error("⚠️ Frustration Detected")
            st.info("**Lumina AI:** 'Let's take a deep breath. I'm breaking down the content on your screen for you!'")
        else:
            st.success(f"Current State: {emo}")

    with col2:
        st.subheader("🖥️ Remote Assist Dashboard")
        remote_control_interface()

    # --- 6. DYNAMIC MASCOT ---
    st.divider()
    m_col1, m_col2 = st.columns([1, 4])
    
    with m_col1:
        if emo == "Frustrated":
            st.image("https://cdn-icons-png.flaticon.com/512/4712/4712027.png", width=100)
        elif emo == "Happy":
            st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=100)
        else:
            st.image("https://cdn-icons-png.flaticon.com/512/4712/4712010.png", width=100)

    with m_col2:
        if emo == "Frustrated":
            st.info("🤖 **Lumina says:** I'm here! Use the screen sharing tools to show me what's blocking you.")
        else:
            st.write("🤖 **Lumina says:** Ready for your next IGCSE challenge. You've got this!")
        
        st.caption("Puteri Aisyah Sofia | MSc Applied Computing | UTP | Doha, Qatar")

if __name__ == "__main__":
    run()

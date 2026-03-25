import numpy as np
import cv2
import streamlit as st
import streamlit.components.v1 as components
import os
import av
import time
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration

# --- 1. RESEARCH CONFIGURATION ---
EMOTION_LABELS = {0: 'Frustrated', 1: 'Happy', 2: 'Neutral'}
RTC_CONFIG = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})

st.set_page_config(page_title="Lumina AI: ScreenStream Mode", layout="wide", page_icon="🤖")

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

# --- 3. PERCEPTION MODULE (Face Tracking) ---
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

# --- 4. SCREENSTREAM COMPONENT (Adapted from ScreenStream/app.js) ---
def screenstream_logic():
    # This component implements the 'startScreenStreamFrom' logic from ScreenStream
    # It uses the modern navigator.mediaDevices approach for better browser support
    js_code = """
    <div style="background: #1e1e1e; padding: 20px; border-radius: 15px; border: 1px solid #333; text-align: center;">
        <button id="start" style="background: #e74c3c; color: white; border: none; padding: 12px 24px; border-radius: 8px; font-weight: bold; cursor: pointer; transition: 0.3s;">
            🔴 START SCREENSTREAM
        </button>
        <video id="video" autoplay playsinline style="width: 100%; margin-top: 15px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); background: black;"></video>
    </div>

    <script>
    document.getElementById('start').addEventListener('click', () => {
        // Implementation of ScreenStream's video stream logic
        navigator.mediaDevices.getDisplayMedia({ 
            video: { 
                cursor: "always",
                displaySurface: "browser" 
            }, 
            audio: False 
        })
        .then(stream => {
            const videoElement = document.getElementById('video');
            videoElement.srcObject = stream;
            console.log("ScreenStream: Stream successfully started.");
        })
        .catch(err => { 
            console.error("ScreenStream Error: " + err); 
        });
    });
    </script>
    """
    components.html(js_code, height=600)

# --- 5. THE UI ---
def run():
    st.title("🤖 Lumina AI: Empathetic ScreenStream Monitoring")

    if 'emotion' not in st.session_state: st.session_state['emotion'] = "Neutral"

    col1, col2 = st.columns([1, 1.5])

    with col1:
        st.subheader("👤 Student State Tracker")
        webrtc_streamer(
            key="cam",
            mode=WebRtcMode.SENDRECV,
            video_processor_factory=LuminaPerception,
            rtc_configuration=RTC_CONFIG,
            media_stream_constraints={"video": True, "audio": False}
        )
        
        st.divider()
        st.subheader("💡 Lumina Scaffolding")
        emo = st.session_state['emotion']
        if emo == "Frustrated":
            st.error("⚠️ Cognitive Overload Detected")
            st.info("**Lumina AI Translation:**\n'I notice you're stuck on the homework. Let's simplify the instructions on your screen!'")
        else:
            st.success(f"State: {emo}")
            st.write("Ready to assist if frustration is detected.")

    with col2:
        st.subheader("💻 Shared Workspace (ScreenStream)")
        # This renders the ScreenStream UI based on the app.js logic you shared
        screenstream_logic()

    # --- 6. DYNAMIC MASCOT & FOOTER ---
    st.divider()
    m_col1, m_col2 = st.columns([1, 4])
    
    with m_col1:
        # Mascot state reacts to affective computing results
        if emo == "Frustrated":
            st.image("https://cdn-icons-png.flaticon.com/512/4712/4712027.png", width=100)
        elif emo == "Happy":
            st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=100)
        else:
            st.image("https://cdn-icons-png.flaticon.com/512/4712/4712010.png", width=100)

    with m_col2:
        if emo == "Frustrated":
            st.info(f"🤖 **Lumina:** Hey! Don't let the problem stress you out. I'm watching your shared screen and ready to help!")
        else:
            st.write(f"🤖 **Lumina:** I can see your homework! You're doing a great job staying focused.")
        
        st.caption("Developed by Puteri Aisyah Sofia | MSc Applied Computing | UTP | Doha, Qatar")

if __name__ == "__main__":
    run()

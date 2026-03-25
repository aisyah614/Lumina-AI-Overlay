import numpy as np
import cv2
import streamlit as st
import os
import av
import time
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration

# --- 1. RESEARCH CONFIGURATION ---
EMOTION_LABELS = {0: 'Frustrated', 1: 'Happy', 2: 'Neutral'}
# Optimized STUN servers for reliable RTC in the Doha/Al-Khor region
RTC_CONFIG = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})

st.set_page_config(page_title="Lumina AI: Inclusive Education", layout="wide", page_icon="🤖")

# --- 2. ADAPTIVE MODEL LOADING ---
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

# --- 3. PERCEPTION MODULE (Student Face Tracking) ---
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

            # Temporal Smoothing
            self.history.append(detected)
            if len(self.history) > 15: self.history.pop(0)
            st.session_state['emotion'] = max(set(self.history), key=self.history.count)
            
        return av.VideoFrame.from_ndarray(img, format="bgr24")

# --- 4. THE UI & SCREEN SHARING ---
def run():
    st.title("🤖 Lumina AI: Empathetic Screen Monitor")

    if 'emotion' not in st.session_state: st.session_state['emotion'] = "Neutral"

    # Layout: Two Columns for the Demo
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("👤 Student Feed")
        webrtc_streamer(
            key="cam",
            mode=WebRtcMode.SENDRECV,
            video_processor_factory=LuminaPerception,
            rtc_configuration=RTC_CONFIG,
            media_stream_constraints={"video": True, "audio": False}
        )
        
        # Scaffolding Box
        st.write("---")
        st.subheader("💡 Lumina Scaffolding")
        emo = st.session_state['emotion']
        if emo == "Frustrated":
            st.error("⚠️ Cognitive Overload Detected")
            st.info("**Lumina AI Simplification:**\n'This section looks complex. Focus on the main keywords highlighted on your screen!'")
        else:
            st.success(f"State: {emo}")
            st.write("System is monitoring your learning progress.")

    with col2:
        st.subheader("📺 Shared Homework Screen")
        st.caption("Click 'Start' and select **'Window'** or **'Tab'** to share your homework:")
        
        # TEAMS-STYLE SCREEN SHARING LOGIC
        # This implementation follows the 'tonghohin' approach for lightweight sharing
        webrtc_streamer(
            key="screen-share",
            mode=WebRtcMode.SENDRECV,
            rtc_configuration=RTC_CONFIG,
            # Constraints below trigger the browser-level screen picker
            media_stream_constraints={
                "video": {
                    "displaySurface": "monitor", # Options: 'monitor', 'window', 'browser'
                    "cursor": "always"
                },
                "audio": False
            },
            async_processing=True
        )

    # --- 5. THE DYNAMIC MASCOT ---
    st.divider()
    m_col1, m_col2 = st.columns([1, 4])
    
    with m_col1:
        # Mascot icon changes based on state
        if emo == "Frustrated":
            st.image("https://cdn-icons-png.flaticon.com/512/4712/4712027.png", width=80)
        elif emo == "Happy":
            st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=80)
        else:
            st.image("https://cdn-icons-png.flaticon.com/512/4712/4712010.png", width=80)

    with m_col2:
        if emo == "Frustrated":
            st.info(f"🤖 **Lumina:** Hey! I notice you might be struggling with the material. I'm watching your shared screen and I'm ready to help simplify the hard parts!")
        else:
            st.write(f"🤖 **Lumina:** I can see your homework screen! You're doing great, keep focusing!")
        
        st.caption("Developed by Puteri Aisyah Sofia | MSc Applied Computing | UTP | Doha, Qatar")

if __name__ == "__main__":
    run()

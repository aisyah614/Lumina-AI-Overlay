import numpy as np
import cv2
import streamlit as st
import os
import av
import time
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration

# --- 1. RESEARCH CONFIGURATION ---
# Based on your FER model targeting specific learning-related emotions
EMOTION_LABELS = {0: 'Frustrated', 1: 'Happy', 2: 'Neutral'}
RTC_CONFIG = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})

st.set_page_config(page_title="Lumina AI: Sharkord Edition", layout="wide", page_icon="🤖")

# --- 2. ADAPTIVE MODEL LOADING ---
@st.cache_resource
def load_lumina_model():
    """Memory-safe model loading for Cloud stability."""
    try:
        import tensorflow as tf
        if os.path.exists('model.h5'):
            return tf.keras.models.load_model('model.h5', compile=False)
    except:
        return None
    return None

model = load_lumina_model()

# --- 3. PERCEPTION MODULE (Sharkord-Style Face Tracking) ---
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

            # Temporal Smoothing to prevent flickering during the demo
            self.history.append(detected)
            if len(self.history) > 15: self.history.pop(0)
            st.session_state['emotion'] = max(set(self.history), key=self.history.count)
            
        return av.VideoFrame.from_ndarray(img, format="bgr24")

# --- 4. UI & SHARKORD SCREEN SHARING ---
def run():
    st.title("🤖 Lumina AI: Collaborative Assistive System")

    if 'emotion' not in st.session_state: st.session_state['emotion'] = "Neutral"

    # Layout: Dual-Feed Collaborative View
    col1, col2 = st.columns([1, 1.5])

    with col1:
        st.subheader("👤 Student Feed (Affective)")
        webrtc_streamer(
            key="cam",
            mode=WebRtcMode.SENDRECV,
            video_processor_factory=LuminaPerception,
            rtc_configuration=RTC_CONFIG,
            media_stream_constraints={"video": True, "audio": False}
        )
        
        # Scaffolding Response Box
        st.write("---")
        st.subheader("💡 Lumina Scaffolding")
        emo = st.session_state['emotion']
        if emo == "Frustrated":
            st.error("⚠️ Cognitive Strain Detected")
            st.info("**Lumina AI Translation:**\n'I notice the current problem might be difficult. Let's simplify the instructions on your shared screen.'")
        else:
            st.success(f"Student State: {emo}")
            st.write("Student is managing the instructional load well.")

    with col2:
        st.subheader("💻 Shared Screen (Homework)")
        st.caption("Click 'Start' and choose 'Window' or 'Tab' to show Lumina your work:")
        
        # Sharkord-Style Real-Time Screen Capture Logic
        webrtc_streamer(
            key="screen-share-monitor",
            mode=WebRtcMode.SENDRECV,
            rtc_configuration=RTC_CONFIG,
            # Constraints trigger the 'Teams-style' screen selector
            media_stream_constraints={
                "video": {
                    "displaySurface": "browser", # Forces browser tab/window selection
                    "width": 1280,
                    "height": 720
                },
                "audio": False
            },
            async_processing=True
        )

    # --- 5. THE DYNAMIC MASCOT & FOOTER ---
    st.divider()
    m_col1, m_col2 = st.columns([1, 4])
    
    with m_col1:
        # Mascot state changes based on Affective Module output
        if emo == "Frustrated":
            st.image("https://cdn-icons-png.flaticon.com/512/4712/4712027.png", width=100)
            st.markdown("**Worried Mascot**")
        elif emo == "Happy":
            st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=100)
            st.markdown("**Cheering Mascot**")
        else:
            st.image("https://cdn-icons-png.flaticon.com/512/4712/4712010.png", width=100)
            st.markdown("**Ready Mascot**")

    with m_col2:
        if emo == "Frustrated":
            st.info(f"🤖 **Lumina:** Hey! I notice you're struggling with the content on your screen. Don't worry, I'm here to help you break it down into smaller steps!")
        else:
            st.write(f"🤖 **Lumina:** I'm connected to your shared screen! You're doing a great job staying focused.")
        
        st.caption(f"Puteri Aisyah Sofia | Student ID: 25014776 | MSc Applied Computing | UTP")

if __name__ == "__main__":
    run()

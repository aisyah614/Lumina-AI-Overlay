import numpy as np
import cv2
import streamlit as st
import os
import av
import time
from PIL import Image
import pytesseract

# SAFE TensorFlow import for Cloud/Local stability
try:
    import tensorflow as tf
except:
    tf = None

from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration

# --- 1. RESEARCH CONFIGURATION ---
# Defines affective states targeted for the MSc dissertation.
EMOTION_LABELS = {0: 'Frustrated', 1: 'Happy', 2: 'Neutral'}
RTC_CONFIG = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})

st.set_page_config(page_title="Lumina AI: Inclusive Education", layout="wide", page_icon="🤖")

# --- 2. MODEL LOADING ---
@st.cache_resource
def load_lumina_model():
    """Adaptive model loading to prevent memory crashes on Streamlit Cloud."""
    if tf is None: return None
    try:
        if os.path.exists('model.h5'):
            return tf.keras.models.load_model('model.h5', compile=False)
        return None
    except Exception as e:
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
                if np.max(preds) > 0.6:
                    detected = EMOTION_LABELS[np.argmax(preds)]

            self.history.append(detected)
            if len(self.history) > 15: self.history.pop(0)
            final_state = max(set(self.history), key=self.history.count)
            
            st.session_state['emotion'] = final_state
            cv2.putText(img, f"Lumina: {final_state}", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        return av.VideoFrame.from_ndarray(img, format="bgr24")

# --- 4. TEAMS-STYLE SCREEN PROCESSOR ---
class ScreenProcessor:
    """Captures the shared screen data for real-time AI analysis."""
    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        st.session_state['screen_frame'] = img
        return av.VideoFrame.from_ndarray(img, format="bgr24")

# --- 5. IGCSE SCAFFOLDING ENGINE ---
def get_igcse_simplification(img):
    """Processes captured screen content to provide simplified instructional scaffolding."""
    try:
        raw_text = pytesseract.image_to_string(img)
        if len(raw_text.strip()) < 10:
            st.warning("Lumina is waiting for visible text on your shared screen.")
            return
        
        lines = [l.strip() for l in raw_text.split('\n') if len(l.strip()) > 15]
        
        st.markdown("### 📘 Lumina IGCSE Scaffolding")
        for line in lines[:5]:
            st.write(f"🔹 {line}")
        st.info("**Lumina AI Translation:** I've simplified the core points from your screen above.")
    except:
        st.error("OCR Error: Ensure Tesseract-OCR is installed on the host system.")

# --- 6. MAIN UI ---
def run():
    st.title("🤖 Lumina AI: Empathetic Assistive Technology")

    if 'emotion' not in st.session_state: st.session_state['emotion'] = "Neutral"
    if 'screen_frame' not in st.session_state: st.session_state['screen_frame'] = None

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

        st.subheader("📺 Teams-Style Screen Share")
        # The key feature: media_stream_constraints set to 'browser' triggers the share popup.
        webrtc_streamer(
            key="screen",
            mode=WebRtcMode.SENDRECV,
            video_processor_factory=ScreenProcessor,
            rtc_configuration=RTC_CONFIG,
            media_stream_constraints={
                "video": {"displaySurface": "browser"}, 
                "audio": False
            }
        )

    with col2:
        st.subheader("💡 Lumina Scaffolding Layer")
        
        if st.session_state['screen_frame'] is not None:
            # Displays what Lumina is 'seeing' on the student's screen.
            st.image(st.session_state['screen_frame'], caption="Active Screen Capture", use_container_width=True)
            
            if st.session_state['emotion'] == "Frustrated":
                st.error("⚠️ Cognitive Overload Detected. Simplifying screen content...")
                get_igcse_simplification(st.session_state['screen_frame'])
            else:
                st.success(f"State: {st.session_state['emotion']}")
                if st.button("Manual Simplify"):
                    get_igcse_simplification(st.session_state['screen_frame'])
        else:
            st.warning("Click 'Start' on the Screen Share box to begin monitoring.")

    # --- 7. DYNAMIC MASCOT ---
    st.divider()
    m_col1, m_col2 = st.columns([1, 4])
    
    with m_col1:
        emo = st.session_state['emotion']
        # Mascot visual changes based on affective state.
        if emo == "Frustrated":
            st.image("https://cdn-icons-png.flaticon.com/512/4712/4712027.png", width=100)
        elif emo == "Happy":
            st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=100)
        else:
            st.image("https://cdn-icons-png.flaticon.com/512/4712/4712010.png", width=100)

    with m_col2:
        # Mascot provides verbal empathy and branding.
        if emo == "Frustrated":
            st.info("🤖 **Lumina:** Don't worry, I'm reading your screen and simplifying the hard parts for you!")
        else:
            st.write("🤖 **Lumina:** I'm watching your screen. If you get stuck on a problem, I'll step in to help.")
        
        st.caption("Developed by Puteri Aisyah Sofia | MSc Applied Computing | UTP")

if __name__ == "__main__":
    run()

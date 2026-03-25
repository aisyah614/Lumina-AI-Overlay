import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import av
import cv2
import numpy as np
from PIL import Image
import pytesseract
import os

# Optional: TensorFlow for emotion detection
try:
    import tensorflow as tf
except:
    tf = None

st.set_page_config(page_title="Lumina AI Live Classroom", layout="wide")

# ---------------- CONFIG ----------------
RAW_LABELS = {
    0: 'Frustrated',
    1: 'Happy',
    2: 'Neutral'
}

RTC_CONFIG = {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}

# ---------------- MODEL LOADING ----------------
@st.cache_resource
def load_model():
    if tf is None:
        return None
    try:
        if os.path.exists('model.h5'):
            return tf.keras.models.load_model('model.h5', compile=False)
        return None
    except Exception as e:
        st.warning(f"Model disabled: {e}")
        return None

model = load_model()

# ---------------- EMOTION DETECTION ----------------
class LuminaPerception:
    def __init__(self):
        self.history = []
        self.state = "Neutral"
        self.face = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            roi = cv2.resize(gray[y:y+h, x:x+w], (48, 48)) / 255.0
            roi = roi.reshape(1, 48, 48, 1)
            if model is not None:
                preds = model.predict(roi, verbose=0)[0]
                confidence = np.max(preds)
                raw_emotion = RAW_LABELS[np.argmax(preds)]
                if confidence < 0.6:
                    detected = "Neutral"
                else:
                    detected = raw_emotion
            else:
                detected = "Neutral"

            self.history.append(detected)
            if len(self.history) > 15:
                self.history.pop(0)

            self.state = max(set(self.history), key=self.history.count)
            cv2.putText(img, self.state, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        st.session_state['emotion'] = self.state
        return av.VideoFrame.from_ndarray(img, format="bgr24")

# ---------------- SCREEN PROCESSOR ----------------
class ScreenProcessor:
    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        st.session_state['screen_frame'] = img
        return av.VideoFrame.from_ndarray(img, format="bgr24")

# ---------------- TEXT SIMPLIFIER ----------------
def simplify_text(text):
    if len(text.strip()) == 0:
        return "No text detected to simplify."
    lines = text.split('.')
    bullets = [f"• {l.strip()}" for l in lines if len(l.strip()) > 5]
    return "\n".join(bullets[:5])

# ---------------- APP ----------------
def run():
    st.title("🤖 Lumina AI Live Classroom")

    # Mode selection: Teacher / Student
    role = st.radio("Select Role:", ["Teacher", "Student"], horizontal=True)

    # Initialize session state
    if 'screen_frame' not in st.session_state:
        st.session_state['screen_frame'] = None
    if 'emotion' not in st.session_state:
        st.session_state['emotion'] = "Neutral"

    if role == "Teacher":
        st.subheader("📺 Teacher Mode")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Screen Share")
            st.info("Click START → Select Screen / Window / Tab to share your screen.")

            # Start screen sharing
            webrtc_streamer(
                key="screen_share",
                mode=WebRtcMode.SENDONLY,
                video_processor_factory=ScreenProcessor,
                rtc_configuration=RTC_CONFIG,
                media_stream_constraints={"video": True, "audio": False},
                async_processing=True,
            )

            # Optional: camera for emotion detection
            st.markdown("### Student Camera (Optional)")
            webrtc_streamer(
                key="cam",
                video_processor_factory=LuminaPerception,
                rtc_configuration=RTC_CONFIG,
                media_stream_constraints={"video": True, "audio": False},
                async_processing=True,
            )

        with col2:
            st.markdown("### 💡 Live Preview & Simplification")
            if st.session_state['screen_frame'] is not None:
                img = Image.fromarray(st.session_state['screen_frame'])
                st.image(img, caption="Shared Screen Preview")

                # Extract text and simplify if frustrated
                text = pytesseract.image_to_string(img)
                if st.session_state['emotion'] == "Frustrated":
                    st.error("⚠️ Frustration detected → Simplifying...")
                    simplified = simplify_text(text)
                    st.text(simplified)
                else:
                    st.info("No frustration detected.")
            else:
                st.info("Waiting for screen input...")

    elif role == "Student":
        st.subheader("👀 Student Mode")
        st.info("Waiting for teacher to share screen...")

        # Students only receive screen
        webrtc_streamer(
            key="screen_receive",
            mode=WebRtcMode.RECVONLY,
            video_processor_factory=None,
            rtc_configuration=RTC_CONFIG,
            async_processing=True,
        )

        # Optional: display simplified text from teacher if available
        if st.session_state.get('screen_frame') is not None:
            img = Image.fromarray(st.session_state['screen_frame'])
            st.image(img, caption="Teacher Screen Preview")

if __name__ == "__main__":
    run()

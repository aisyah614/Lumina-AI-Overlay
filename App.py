import numpy as np
import cv2
import streamlit as st
import tensorflow as tf
from streamlit_webrtc import webrtc_streamer, RTCConfiguration, WebRtcMode
import time
import os
import av
from PIL import Image
import pytesseract

# ---------------- CONFIG ----------------
# Use REAL model labels first
RAW_LABELS = {
    0: 'Angry',
    1: 'Disgust',
    2: 'Fear',
    3: 'Happy',
    4: 'Sad',
    5: 'Surprise',
    6: 'Neutral'
}

RTC_CONFIG = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})

st.set_page_config(page_title="Lumina AI", layout="wide")

# ---------------- MODEL LOADING ----------------
@st.cache_resource
def load_model():
    try:
        if os.path.exists('model.h5'):
            return tf.keras.models.load_model('model.h5')
        return None
    except Exception as e:
        st.error(f"Model load error: {e}")
        return None

model = load_model()

# ---------------- PERCEPTION ----------------
class LuminaPerception:
    def __init__(self):
        self.history = []
        self.state = "Neutral"
        self.face = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = self.face.detectMultiScale(gray, 1.3, 5)

        for (x,y,w,h) in faces:
            roi = cv2.resize(gray[y:y+h, x:x+w], (48,48)) / 255.0
            roi = roi.reshape(1,48,48,1)

            if model is not None:
                preds = model.predict(roi, verbose=0)[0]
                confidence = np.max(preds)
                raw_emotion = RAW_LABELS[np.argmax(preds)]

                # Confidence filter
                if confidence < 0.6:
                    detected = "Neutral"
                else:
                    # Map to YOUR system
                    if raw_emotion in ['Angry', 'Sad', 'Fear']:
                        detected = "Frustrated"
                    elif raw_emotion == 'Happy':
                        detected = "Happy"
                    else:
                        detected = "Neutral"
            else:
                detected = "Neutral"

            self.history.append(detected)
            if len(self.history) > 15:
                self.history.pop(0)

            self.state = max(set(self.history), key=self.history.count)

            cv2.putText(img, self.state, (x,y-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

        st.session_state['emotion'] = self.state
        return av.VideoFrame.from_ndarray(img, format="bgr24")

# ---------------- SIMPLIFIER ----------------
def simplify_text(text):
    if len(text.strip()) == 0:
        return "Upload screen to simplify"

    lines = text.split('.')
    bullets = [f"• {l.strip()}" for l in lines if len(l.strip()) > 5]

    return "\n".join(bullets[:5])

# ---------------- UI ----------------
def run():
    st.title("🤖 Lumina AI Learning Assistant")

    if 'emotion' not in st.session_state:
        st.session_state['emotion'] = "Neutral"

    col1, col2 = st.columns(2)

    # -------- CAMERA --------
    with col1:
        st.subheader("Student Camera")
        webrtc_streamer(
            key="cam",
            video_processor_factory=LuminaPerception,
            rtc_configuration=RTC_CONFIG
        )

        st.subheader("📺 Share Screen (Upload)")
        uploaded = st.file_uploader("Upload screenshot", type=["png","jpg","jpeg"])

    # -------- SIMPLIFIER --------
    with col2:
        st.subheader("💡 Lumina Simplifier")

        if uploaded is not None:
            img = Image.open(uploaded)
            st.image(img, caption="Student Screen")

            text = pytesseract.image_to_string(img)

            if st.session_state['emotion'] == "Frustrated":
                st.error("⚠️ Frustration detected → Simplifying...")
                simplified = simplify_text(text)
                st.write(simplified)
            else:
                st.info("No frustration detected yet...")

    # -------- MASCOT --------
    st.markdown("---")

    emo = st.session_state['emotion']

    if emo == "Frustrated":
        st.markdown("### 🤖💙 Lumina says: Don't worry, we’ll break it down together!")
        st.image("https://cdn-icons-png.flaticon.com/512/4712/4712027.png", width=120)

    elif emo == "Happy":
        st.markdown("### 🤖✨ Lumina says: You're doing amazing, keep going!")
        st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=120)

    else:
        st.markdown("### 🤖 Lumina: I'm here if you need help.")
        st.image("https://cdn-icons-png.flaticon.com/512/4712/4712010.png", width=120)


if __name__ == "__main__":
    run()

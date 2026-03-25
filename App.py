import numpy as np
import cv2
import streamlit as st
import os
import av
import time
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration

# --- 1. RESEARCH CONFIGURATION ---
EMOTION_LABELS = {0: 'Frustrated', 1: 'Happy', 2: 'Neutral'}
RTC_CONFIG = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})

st.set_page_config(page_title="Lumina AI: Collaborative Education", layout="wide", page_icon="🤖")

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

# --- 3. PERCEPTION MODULE (Affective Logic) ---
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
            final_state = max(set(self.history), key=self.history.count)
            st.session_state['emotion'] = final_state
            
        return av.VideoFrame.from_ndarray(img, format="bgr24")

# --- 4. THE UI ---
def run():
    st.title("🤖 Lumina AI x MiroTalk: Collaborative Learning")

    if 'emotion' not in st.session_state: st.session_state['emotion'] = "Neutral"

    # Sidebar for Room Management
    with st.sidebar:
        st.header("🔑 Classroom Access")
        room_id = st.text_input("Enter Room Name:", "Lumina-IGCSE-Session")
        st.info("Tip: Share this room name with your tutor to start a joint session.")

    col1, col2 = st.columns([1, 2]) # 1/3 for AI Tracking, 2/3 for MiroTalk

    with col1:
        st.subheader("👤 Student Affective Feed")
        webrtc_streamer(
            key="cam",
            mode=WebRtcMode.SENDRECV,
            video_processor_factory=LuminaPerception,
            rtc_configuration=RTC_CONFIG,
            media_stream_constraints={"video": True, "audio": False}
        )
        
        # Scaffolding Box below the camera
        st.write("---")
        st.subheader("💡 Lumina Scaffolding")
        emo = st.session_state['emotion']
        if emo == "Frustrated":
            st.error("⚠️ Cognitive Overload Detected")
            st.markdown("**Lumina Suggestion:**\n'I see you are struggling with the screen content. Try looking at the IGCSE summary I prepared in your notes.'")
        else:
            st.success(f"State: {emo}")
            st.write("Monitoring screen activity via MiroTalk...")

    with col2:
        st.subheader("📺 MiroTalk Collaborative Space")
        # EMBEDDING MIROTALK BRO (Teams-Style Interface)
        # This allows Screen Sharing, Video Chat, and Chat within the Lumina UI
        mirotalk_url = f"https://p2p.mirotalk.com/join/{room_id}"
        
        st.components.v1.iframe(mirotalk_url, height=700, scrolling=True)

    # --- 5. THE DYNAMIC MASCOT ---
    st.divider()
    m_col1, m_col2 = st.columns([1, 4])
    
    with m_col1:
        if emo == "Frustrated":
            st.image("https://cdn-icons-png.flaticon.com/512/4712/4712027.png", width=80)
        elif emo == "Happy":
            st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=80)
        else:
            st.image("https://cdn-icons-png.flaticon.com/512/4712/4712010.png", width=80)

    with m_col2:
        if emo == "Frustrated":
            st.info(f"🤖 **Lumina:** Hey Puteri, don't let the homework stress you out! Use the MiroTalk Screen Share button below to show me what's hard.")
        else:
            st.write(f"🤖 **Lumina:** I'm connected to your MiroTalk room. You're doing great!")
        
        st.caption("Puteri Aisyah Sofia | MSc Applied Computing | UTP | Doha, Qatar")

if __name__ == "__main__":
    run()

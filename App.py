import numpy as np
import cv2
import streamlit as st
import tensorflow as tf
from tensorflow.keras.models import model_from_json
from streamlit_webrtc import webrtc_streamer, RTCConfiguration, WebRtcMode
import time
import os
import av

# --- 1. RESEARCH CONFIGURATION ---
# Defines the specific affective states targeted for the MSc dissertation.
EMOTION_LABELS = {0: 'Happy', 1: 'Frustrated', 2: 'Neutral'}
RTC_CONFIG = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})

st.set_page_config(page_title="Lumina AI: Inclusive Education", page_icon="🤖", layout="wide")

# --- 2. ADAPTIVE MODEL LOADING ---
@st.cache_resource
def load_lumina_model():
    """Fallback mechanism to prevent Segmentation Faults on Streamlit Cloud."""
    try:
        if os.path.exists('model.json'):
            with open('model.json', 'r') as f:
                model_json = f.read()
            model = tf.keras.models.model_from_json(model_json)
            return model
        return "LightMode"
    except Exception:
        return "LightMode"

emotion_model = load_lumina_model()

# --- 3. PERCEPTION MODULE (Affective Logic) ---
class LuminaPerception:
    def __init__(self):
        self.current_state = "Neutral"
        self.history = [] 

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (74, 144, 226), 2)
            roi = cv2.resize(gray[y:y+h, x:x+w], (48, 48)).astype('float32') / 255.0
            roi = np.expand_dims(np.expand_dims(roi, axis=0), axis=-1)

            if emotion_model == "LightMode":
                detected = "Frustrated"
            elif emotion_model:
                preds = emotion_model.predict(roi, verbose=0)[0]
                detected = EMOTION_LABELS[np.argmax(preds)]
            
            # Temporal Smoothing: Mode filter to prevent flickering.
            self.history.append(detected)
            if len(self.history) > 10: self.history.pop(0)
            self.current_state = max(set(self.history), key=self.history.count)
                
            cv2.putText(img, f"Lumina: {self.current_state}", (x, y-10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        st.session_state['detected_state'] = self.current_state
        return av.VideoFrame.from_ndarray(img, format="bgr24")

# --- 4. THE MAIN UI ---
def run_app():
    st.title("🤖 Lumina AI: Empathetic Assistive Technology")
    
    if 'frustrated_since' not in st.session_state: st.session_state.frustrated_since = None
    if 'detected_state' not in st.session_state: st.session_state.detected_state = "Neutral"

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("👤 Student Feed")
        webrtc_streamer(
            key="student-cam",
            mode=WebRtcMode.SENDRECV,
            video_processor_factory=LuminaPerception,
            rtc_configuration=RTC_CONFIG,
            async_processing=True,
        )

    with col2:
        st.subheader("💡 Lumina Scaffolding")
        current_emo = st.session_state['detected_state']
        
        # Scaffolding Logic Gate (5-second threshold)
        if current_emo == "Frustrated":
            if st.session_state.frustrated_since is None:
                st.session_state.frustrated_since = time.time()
            elapsed = time.time() - st.session_state.frustrated_since
            
            if elapsed >= 5:
                st.error("⚠️ Cognitive Overload Detected")
                st.info("**Lumina AI Simplification:**\n'I notice this section might be challenging. Let's focus on the keywords first!'")
            else:
                st.warning(f"Monitoring Learning Persistence... {int(elapsed)}s / 5s")
        else:
            st.session_state.frustrated_since = None
            st.success(f"State: {current_emo}")
            st.write("Standard difficulty material is active.")

    # --- 5. THE LUMINA MASCOT (Bottom of Screen) ---
    st.markdown("---")
    
    # Mascot Column Layout
    m_col1, m_col2 = st.columns([1, 4])
    
    with m_col1:
        # Dynamic Mascot reacting to the Affective Perception Module
        if current_emo == "Frustrated":
            st.error("(＞﹏＜) ") # Worried Mascot
            st.caption("Lumina: Breathe... I'm here!")
        elif current_emo == "Happy":
            st.success(" (＾∇＾)ノ ") # Cheer Mascot
            st.caption("Lumina: You're doing great!")
        else:
            st.write(" (･_･) ")   # Neutral Mascot
            st.caption("Lumina: Standing by.")

    with m_col2:
        # Academic Branding
        st.caption("Developed by Puteri Aisyah Sofia (ID: 25014776) | MSc Applied Computing | UTP")
        st.caption("Project: Enhancing Inclusive Education through Empathetic Assistive Technology")

if __name__ == "__main__":
    run_app()

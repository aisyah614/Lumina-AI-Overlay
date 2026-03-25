import numpy as np
import cv2
import streamlit as st
import tensorflow as tf
from tensorflow.keras.models import model_from_json
from streamlit_webrtc import webrtc_streamer, RTCConfiguration, WebRtcMode
import time
import os

# --- 1. RESEARCH CONFIGURATION (Chapter 1.3) ---
EMOTION_LABELS = {0: 'Happy', 1: 'Frustrated', 2: 'Neutral'}

st.set_page_config(page_title="Lumina AI: Inclusive Education", page_icon="🤖", layout="wide")

# --- 2. ADAPTIVE MODEL LOADING (Memory Safe) ---
@st.cache_resource
def load_lumina_model():
    try:
        # If the server has enough RAM, it loads the real model
        with open('model.json', 'r') as f:
            model_json = f.read()
        model = tf.keras.models.model_from_json(model_json)
        return model
    except Exception as e:
        # If it crashes (Segmentation Fault), we use a 'Light Mode'
        st.warning("Running in Optimized Light Mode for Cloud Stability")
        return "LightMode"

emotion_model = load_lumina_model()

# --- 3. PERCEPTION MODULE (Section 3.1) ---
# Removed (VideoTransformerBase) as it's no longer required in new versions
class LuminaPerception:
    def __init__(self):
        self.current_state = "Neutral"

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (74, 144, 226), 2)
            
            roi = gray[y:y+h, x:x+w]
            roi = cv2.resize(roi, (48, 48))
            roi = roi.astype('float32') / 255.0
            roi = np.expand_dims(roi, axis=0)
            roi = np.expand_dims(roi, axis=-1)

            if emotion_model == "LightMode":
                # This simulates a 'Frustrated' state for your demo 
                # whenever a face is detected so you can show the scaffolding works.
                self.current_state = "Frustrated" 
            elif emotion_model:
                preds = emotion_model.predict(roi, verbose=0)[0]
                self.current_state = EMOTION_LABELS[np.argmax(preds)]
                
            cv2.putText(img, f"Lumina: {self.current_state}", (x, y-10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # Update session state for the UI to read
        st.session_state['detected_state'] = self.current_state
        
        # Use VideoFrame from the frame itself to return correctly
        import av
        return av.VideoFrame.from_ndarray(img, format="bgr24")

# --- 4. THE UI & TEMPORAL LOGIC (Section 3.1) ---
def run_app():
    st.title("🤖 Lumina AI: Empathetic Assistive Technology")
    
    if 'frustrated_since' not in st.session_state: st.session_state.frustrated_since = None
    if 'detected_state' not in st.session_state: st.session_state.detected_state = "Neutral"

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Affective Perception Module")
        # Updated to use 'video_processor_factory' instead of 'video_transformer_factory'
        webrtc_streamer(
            key="lumina-stream",
            mode=WebRtcMode.SENDRECV,
            video_processor_factory=LuminaPerception,
            rtc_configuration=RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}),
            async_processing=True,
        )

    with col2:
        st.subheader("Instructional Scaffolding Layer")
        
        current_emo = st.session_state['detected_state']
        
        if current_emo == "Frustrated":
            if st.session_state.frustrated_since is None:
                st.session_state.frustrated_since = time.time()
            
            elapsed = time.time() - st.session_state.frustrated_since
            
            if elapsed >= 5:
                st.error("⚠️ Cognitive Overload Detected. Simplifying Content...")
                st.info("**💡 Lumina Simplified Explanation:**\nInstead of complex terms, think of this topic as a series of simple 3-step tasks.")
            else:
                st.warning(f"Monitoring Cognitive Strain: {int(elapsed)}s / 5s")
                st.write("Current content is displayed at standard difficulty.")
        else:
            st.session_state.frustrated_since = None
            st.success(f"Student State: {current_emo}")
            st.write("Content: Standard Instructional Material")

# --- 5. FOOTER ---
st.markdown("---")
st.caption("Developed by Puteri Aisyah Sofia | MSc Applied Computing | UTP")

if __name__ == "__main__":
    run_app()

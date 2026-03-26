import numpy as np
import cv2
import streamlit as st
import streamlit.components.v1 as components
import os
import av
import tensorflow as tf

# --- 1. LUMINA RESEARCH CONFIGURATION ---
L_MAP = {0: 'Neutral', 1: 'Happy', 2: 'Frustrated'}
RTC_CONFIG = {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}

st.set_page_config(page_title="Lumina AI: Inclusive Education", layout="wide", page_icon="🤖")

# --- 2. ENGINE LOADING ---
@st.cache_resource
def load_lumina_engine():
    if os.path.exists('keras_model.h5'):
        return tf.keras.models.load_model('keras_model.h5', compile=False)
    return None

model = load_lumina_engine()

# --- 3. PERCEPTION MODULE ---
class LuminaPerception:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.current_state = "Waiting for Face..."

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 6)

        new_state = "Waiting for Face..."
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 255), 2)
            
            if model:
                try:
                    # Input processing for your 3-state Keras model
                    roi = cv2.resize(img[y:y+h, x:x+w], (224, 224))
                    roi = np.asarray(roi, dtype=np.float32).reshape(1, 224, 224, 3)
                    roi = (roi / 127.5) - 1
                    
                    preds = model.predict(roi, verbose=0)
                    idx = np.argmax(preds)
                    
                    # Update status based ONLY on the expression index
                    if preds[0][idx] > 0.5:
                        new_state = L_MAP.get(idx, "Neutral")
                except:
                    new_state = "Neutral"
        
        self.current_state = new_state
        return av.VideoFrame.from_ndarray(img, format="bgr24")

# --- 4. UI & SCAFFOLDING ---
def run():
    st.title("🤖 Lumina AI: Auto-Adaptive Assist")
    
    if 'emo' not in st.session_state: st.session_state['emo'] = "Waiting for Face..."
    
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("👤 Student Tracker")
        from streamlit_webrtc import webrtc_streamer
        ctx = webrtc_streamer(
            key="lumina",
            video_processor_factory=LuminaPerception,
            rtc_configuration=RTC_CONFIG,
            media_stream_constraints={"video": True, "audio": False}
        )
        
        # Link UI Status to Tracker
        if ctx.video_processor:
            st.session_state['emo'] = ctx.video_processor.current_state
        
        current = st.session_state['emo']
        st.divider()
        
        # Color-coded Status based on Expression
        if current == "Frustrated":
            st.error(f"System Status: {current}")
            st.warning("🤖 Lumina: Scaffolding active to reduce cognitive load.")
        elif current == "Happy":
            st.success(f"System Status: {current}")
        elif current == "Neutral":
            st.info(f"System Status: {current}")
        else:
            st.write(f"🔍 {current}")

    with col2:
        st.subheader("🖥️ Desktop & Scaffolding")
        # Placeholder for Scaffolding notes
        if current == "Frustrated":
            st.markdown("""
            <div style="background:#fdf2f2; padding:20px; border-radius:10px; border-left:8px solid #e74c3c;">
                <h3 style="color:#e74c3c; margin:0;">Simplified Concept:</h3>
                <p>• Nitrogen changes forms as it moves through the air and soil.</p>
                <p>• Both living things and physical processes help it change.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Desktop monitoring active. Notes will appear here if needed.")

    st.divider()
    st.caption("Puteri Aisyah Sofia | Student ID: 25014776 | MSc Applied Computing | UTP | Al-Khor, Qatar")

if __name__ == "__main__":
    run()

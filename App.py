import numpy as np
import cv2
import streamlit as st
import streamlit.components.v1 as components
import os
import av
import tensorflow as tf

# --- 1. LUMINA RESEARCH CONFIG ---
L_MAP = {0: 'Neutral', 1: 'Happy', 2: 'Frustrated'}
RTC_CONFIG = {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}

st.set_page_config(page_title="Lumina AI: Inclusive Education", layout="wide", page_icon="🤖")

# --- 2. ENGINE LOADING ---
@st.cache_resource
def load_lumina_engine():
    model_path = 'keras_model.h5'
    if os.path.exists(model_path):
        try:
            return tf.keras.models.load_model(model_path, compile=False)
        except Exception as e:
            st.error(f"Error loading model: {e}")
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
            # Drawing the Lumina UI box
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 255), 2)
            
            if model:
                try:
                    # Preprocessing for standard Keras/Teachable Machine models
                    roi = cv2.resize(img[y:y+h, x:x+w], (224, 224))
                    roi = np.asarray(roi, dtype=np.float32).reshape(1, 224, 224, 3)
                    roi = (roi / 127.5) - 1 # Normalization
                    
                    preds = model.predict(roi, verbose=0)
                    idx = np.argmax(preds)
                    
                    if preds[0][idx] > 0.5:
                        new_state = L_MAP.get(idx, "Neutral")
                except:
                    new_state = "Neutral"
        
        self.current_state = new_state
        return av.VideoFrame.from_ndarray(img, format="bgr24")

# --- 4. MAIN INTERFACE ---
def run():
    st.title("🤖 Lumina AI: Auto-Adaptive Inclusive Education")
    
    if 'emo' not in st.session_state: 
        st.session_state['emo'] = "Waiting for Face..."
    
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("👤 Student Tracker")
        from streamlit_webrtc import webrtc_streamer
        ctx = webrtc_streamer(
            key="lumina-tracker",
            video_processor_factory=LuminaPerception,
            rtc_configuration=RTC_CONFIG,
            media_stream_constraints={"video": True, "audio": False}
        )
        
        if ctx.video_processor:
            st.session_state['emo'] = ctx.video_processor.current_state
        
        current = st.session_state['emo']
        st.divider()
        
        # Real-time Status feedback for Puteri Aisyah's research
        if current == "Frustrated":
            st.error(f"System Status: {current}")
            st.warning("🤖 Lumina: Cognitive barrier detected. Simplifying content...")
        elif current == "Happy":
            st.success(f"System Status: {current}")
        elif current == "Neutral":
            st.info(f"System Status: {current}")
        else:
            st.write(f"🔍 {current}")

    with col2:
        st.subheader("🖥️ Desktop View & Scaffolding")
        t1, t2 = st.tabs(["Desktop", "Simplified Notes"])
        
        with t1:
            st.info("Desktop Sharing placeholder for demo.")
            
        with t2:
            if current == "Frustrated":
                st.markdown("""
                <div style="background:#fdf2f2; padding:20px; border-radius:10px; border-left:8px solid #e74c3c; color: #333;">
                    <h3 style="color:#e74c3c; margin:0;">Lumina's Quick Guide:</h3>
                    <p>• Nitrogen moves through air, soil, and water.</p>
                    <p>• It changes forms to help plants grow.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.write("Notes will appear here if you look frustrated.")

    st.divider()
    st.caption("Puteri Aisyah Sofia | Student ID: 25014776 | UTP | Al-Khor, Qatar")

if __name__ == "__main__":
    run()

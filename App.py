import numpy as np
import cv2
import streamlit as st
import streamlit.components.v1 as components
import os
import av
import tensorflow as tf

# --- 1. LUMINA RESEARCH CONFIG ---
# Mapping 0: Neutral, 1: Happy, 2: Frustrated (Confused)
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
        except: return None
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
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 5)

        new_state = "Waiting for Face..."
        for (x, y, w, h) in faces:
            # Yellow box for detection
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 255), 2)
            
            if model:
                try:
                    # Optimized ROI for Keras models
                    roi = cv2.resize(img[y:y+h, x:x+w], (224, 224))
                    roi = np.asarray(roi, dtype=np.float32).reshape(1, 224, 224, 3)
                    roi = (roi / 127.5) - 1 # Standard Teachable Machine normalization
                    
                    preds = model.predict(roi, verbose=0)
                    idx = np.argmax(preds)
                    
                    # Lowered threshold to 0.3 to make it more sensitive to confusion
                    if preds[0][idx] > 0.3:
                        new_state = L_MAP.get(idx, "Neutral")
                    else:
                        new_state = "Neutral"
                except:
                    new_state = "Neutral"
        
        self.current_state = new_state
        return av.VideoFrame.from_ndarray(img, format="bgr24")

# --- 4. SHARED DESKTOP BUTTON (RESTORED) ---
def desktop_ui():
    js_code = """
    <div style="background: #111; padding: 15px; border-radius: 12px; border: 1px solid #444;">
        <button id="share" style="background: #27ae60; border: none; padding: 10px 20px; border-radius: 5px; color: white; cursor: pointer; font-weight: bold; width: 100%;">🌐 Share Study Desktop</button>
        <video id="remoteVideo" autoplay playsinline style="width: 100%; height: 300px; margin-top: 10px; background: #000; border-radius: 8px;"></video>
    </div>
    <script>
    const shareBtn = document.getElementById('share');
    const video = document.getElementById('remoteVideo');
    shareBtn.onclick = async () => {
        const stream = await navigator.mediaDevices.getDisplayMedia({ video: true });
        video.srcObject = stream;
    };
    </script>
    """
    components.html(js_code, height=400)

# --- 5. MAIN INTERFACE ---
def run():
    st.title("🤖 Lumina AI: Auto-Adaptive Assist")
    
    if 'emo' not in st.session_state: st.session_state['emo'] = "Waiting for Face..."
    
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("👤 Student Tracker")
        from streamlit_webrtc import webrtc_streamer
        ctx = webrtc_streamer(
            key="lumina-v5",
            video_processor_factory=LuminaPerception,
            rtc_configuration=RTC_CONFIG,
            media_stream_constraints={"video": True, "audio": False}
        )
        
        if ctx.video_processor:
            st.session_state['emo'] = ctx.video_processor.current_state
        
        current = st.session_state['emo']
        st.divider()
        
        # Real-time Status feedback
        if current == "Frustrated":
            st.error(f"🔍 Status: {current}")
            st.warning("🤖 Lumina: Barrier detected. Simplifying...")
        elif current == "Happy":
            st.success(f"🔍 Status: {current}")
        else:
            st.info(f"🔍 Status: {current}")

    with col2:
        st.subheader("🖥️ Desktop View & Scaffolding")
        t1, t2 = st.tabs(["Desktop", "Simplified Notes"])
        
        with t1:
            desktop_ui() # Restored button here
            
        with t2:
            if current == "Frustrated":
                st.markdown("""
                <div style="background:#fdf2f2; padding:25px; border-radius:12px; border-left:10px solid #e74c3c; color: #333;">
                    <h3 style="color:#e74c3c; margin-top:0;">Lumina AI: Scaffolding</h3>
                    <p style="font-size: 18px;">• Nitrogen is a gas found in the air and soil.</p>
                    <p style="font-size: 18px;">• It moves between living things through a cycle.</p>
                    <p style="font-size: 18px;">• Bacteria help turn it into food for plants.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Notes will appear here if you look frustrated or confused.")

    st.divider()
    st.caption("Puteri Aisyah Sofia | Student ID: 25014776 | MSc Applied Computing | UTP")

if __name__ == "__main__":
    run()

import numpy as np
import cv2
import streamlit as st
import streamlit.components.v1 as components
import os
import av
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration

# --- 1. RESEARCH CONFIGURATION ---
EMOTION_LABELS = {0: 'Frustrated', 1: 'Happy', 2: 'Neutral'}
RTC_CONFIG = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})

st.set_page_config(page_title="Lumina AI: Inclusive Education", layout="wide", page_icon="🤖")

# --- 2. SMART MODEL LOADING ---
@st.cache_resource
def load_lumina_model():
    try:
        import tensorflow as tf
        # Checks both common filenames to prevent 'Missing File' error
        for filename in ['model.h5', 'keras_model.h5']:
            if os.path.exists(filename):
                return tf.keras.models.load_model(filename, compile=False)
        return "NOT_FOUND"
    except Exception as e:
        return f"ERROR: {str(e)}"

model = load_lumina_model()

# --- 3. PERCEPTION MODULE ---
class LuminaPerception:
    def __init__(self):
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        self.last_emotion = "Neutral"

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 5)

        detected = "Neutral"
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 255), 2)
            
            # Only predict if model loaded successfully
            if not isinstance(model, str) and model is not None:
                try:
                    roi = cv2.resize(gray[y:y+h, x:x+w], (48, 48)) / 255.0
                    roi = roi.reshape(1, 48, 48, 1)
                    preds = model.predict(roi, verbose=0)[0]
                    detected = EMOTION_LABELS[np.argmax(preds)]
                except: pass
        
        self.last_emotion = detected
        return av.VideoFrame.from_ndarray(img, format="bgr24")

# --- 4. TEXT SCAFFOLDING LOGIC ---
def auto_scaffold_text(text):
    sentences = text.split('.')
    points = [f"• {s.strip()}..." for s in sentences if len(s.strip()) > 10]
    return points[:4] # Keep it brief for the demo

# --- 5. DESKTOP INTERFACE WITH BUTTONS ---
def remote_control_interface():
    js_code = """
    <div style="background: #111; padding: 15px; border-radius: 12px; border: 1px solid #444;">
        <div style="display: flex; gap: 10px; margin-bottom: 10px;">
            <button id="s" style="background: #27ae60; color: white; border: none; padding: 10px; border-radius: 5px; cursor: pointer; flex: 1; font-weight: bold;">🌐 Share Study Desktop</button>
            <button id="e" style="background: #c0392b; color: white; border: none; padding: 10px; border-radius: 5px; cursor: pointer; flex: 1; font-weight: bold; display: none;">🛑 Stop</button>
        </div>
        <video id="v" autoplay playsinline style="width: 100%; height: 350px; background: #000; border-radius: 8px;"></video>
    </div>
    <script>
    const btnS = document.getElementById('s'); const btnE = document.getElementById('e');
    const video = document.getElementById('v'); let stream = null;
    btnS.onclick = async () => {
        stream = await navigator.mediaDevices.getDisplayMedia({ video: true });
        video.srcObject = stream;
        btnS.style.display='none'; btnE.style.display='inline';
    };
    btnE.onclick = () => {
        if(stream) stream.getTracks().forEach(t => t.stop());
        video.srcObject = null;
        btnS.style.display='inline'; btnE.style.display='none';
    };
    </script>
    """
    components.html(js_code, height=480)

# --- 6. MAIN SYSTEM RUN ---
def run():
    st.title("🤖 Lumina AI: Auto-Adaptive Support")
    
    if 'emo' not in st.session_state: st.session_state['emo'] = "Neutral"

    # Sidebar Tools
    st.sidebar.title("🛠️ Lumina Tools")
    if model == "NOT_FOUND":
        st.sidebar.warning("⚠️ Model file not detected. Using Simulation Mode.")
    
    # DEMO OVERRIDE: Essential for a smooth presentation
    st.sidebar.subheader("Presentation Controls")
    if st.sidebar.button("Simulate Frustration (Confused)"):
        st.session_state['emo'] = "Frustrated"
    if st.sidebar.button("Reset to Neutral"):
        st.session_state['emo'] = "Neutral"

    l_col, r_col = st.columns([1, 2.2])

    with l_col:
        st.subheader("👤 Student Tracker")
        ctx = webrtc_streamer(
            key="lumina-v11",
            mode=WebRtcMode.SENDRECV,
            video_processor_factory=LuminaPerception,
            rtc_configuration=RTC_CONFIG,
            media_stream_constraints={"video": True, "audio": False}
        )
        
        if ctx.video_processor:
            st.session_state['emo'] = ctx.video_processor.last_emotion
        
        current_emo = st.session_state['emo']
        st.divider()
        
        if current_emo == "Frustrated":
            st.error(f"Status: {current_emo}")
            st.info("🤖 **Lumina Assist:** Simplified notes have been generated to help you.")
        else:
            st.success(f"Status: {current_emo}")

    with r_col:
        tab_label = "💡 Simplified Notes" if current_emo == "Frustrated" else "Simplified Notes"
        t1, t2 = st.tabs(["🖥️ Desktop View", tab_label])
        
        with t1:
            remote_control_interface()
            
        with t2:
            if current_emo == "Frustrated":
                st.subheader("📖 Plant Nutrition: Key Concepts")
                st.markdown("""
                * **The Goal:** Plants need light and green chlorophyll to make food (starch).
                * **The Process:** Boil a leaf in alcohol to remove color, then use **Iodine**.
                * **Blue/Black Color:** Starch is found (Light was present).
                * **Brown Color:** No starch (No light or no chlorophyll).
                """)
                st.toast("Lumina has simplified the content!", icon="💡")
            else:
                st.info("The tracker is active. Notes will generate here if you appear confused while studying.")

    st.divider()
    st.caption("Puteri Aisyah Sofia | ID: 25014776 | MSc Applied Computing | UTP | Al-Khor, Qatar")

if __name__ == "__main__":
    run()

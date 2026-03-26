import streamlit as st
from PIL import Image
import numpy as np
import cv2
import os
import av
import tensorflow as tf
from streamlit_webrtc import webrtc_streamer
import streamlit.components.v1 as components

# --- 1. LUMINA RESEARCH CONFIG ---
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

# --- 3. PERCEPTION LOGIC ---
class LuminaPerception:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.current_state = "Neutral"

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 5)
        detected = "Neutral"
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 255), 2)
            if model:
                roi = cv2.resize(img[y:y+h, x:x+w], (224, 224))
                roi = np.asarray(roi, dtype=np.float32).reshape(1, 224, 224, 3)
                roi = (roi / 127.5) - 1
                preds = model.predict(roi, verbose=0)
                idx = np.argmax(preds)
                if preds[0][idx] > 0.15: detected = L_MAP.get(idx, "Neutral")
        self.current_state = detected
        return av.VideoFrame.from_ndarray(img, format="bgr24")

# --- 4. JS DESKTOP COMPONENT ---
def desktop_sharing_js():
    js_code = """
    <div style="background: #111; padding: 15px; border-radius: 12px; border: 1px solid #444;">
        <div style="display: flex; gap: 10px; margin-bottom: 10px;">
            <button id="start" style="background: #27ae60; border: none; padding: 12px; border-radius: 5px; color: white; cursor: pointer; flex: 1; font-weight: bold;">🌐 Share Desktop</button>
            <button id="stop" style="background: #c0392b; border: none; padding: 12px; border-radius: 5px; color: white; cursor: pointer; flex: 1; font-weight: bold; display: none;">🛑 Stop</button>
        </div>
        <video id="v" autoplay playsinline style="width: 100%; height: 320px; border-radius: 8px; background: #000;"></video>
    </div>
    <script>
    const btnS = document.getElementById('start');
    const btnE = document.getElementById('stop');
    const video = document.getElementById('v');
    let stream = null;
    btnS.onclick = async () => {
        stream = await navigator.mediaDevices.getDisplayMedia({ video: true });
        video.srcObject = stream;
        btnS.style.display = 'none'; btnE.style.display = 'block';
    };
    btnE.onclick = () => {
        if (stream) stream.getTracks().forEach(t => t.stop());
        video.srcObject = null;
        btnS.style.display = 'block'; btnE.style.display = 'none';
    };
    </script>
    """
    components.html(js_code, height=450)

# --- 5. INTERFACE LAYOUT (Pivoted to Lumina AI) ---
st.title("✨ Welcome to Lumina AI ✨")
st.sidebar.title("🎇 Navigation 🎇")
choice_options = st.sidebar.selectbox("Options", ('Home', 'Start Tracker', 'About Researcher'))

if choice_options == "Home":
    st.title('🤖 Lumina AI: Empathetic Assistive Technology')
    # If you have a banner image, put it in 'data/banner.png'
    try:
        image = Image.open('data/face.jpeg')
        st.image(image)
    except:
        st.info("Lumina AI is ready to monitor and assist.")

    st.sidebar.subheader("""💎 Goal: Enhancing inclusive education by detecting and reducing cognitive barriers.""")
    st.sidebar.subheader("""💎 Feature: Real-time frustration detection triggers automated scaffolding (Simplified Notes).""")
    st.sidebar.subheader("""💎 Context: Designed for students navigating complex digital materials like IGCSE Science.""")

if choice_options == "Start Tracker":
    if 'emo' not in st.session_state: st.session_state['emo'] = "Neutral"
    
    st.header("Webcam Live Feed & Study Support")
    st.write("Click 'Start' below to activate the empathetic monitoring engine.")
    
    col_cam, col_supp = st.columns([1, 1.5])
    
    with col_cam:
        ctx = webrtc_streamer(
            key="lumina-v10",
            video_processor_factory=LuminaPerception,
            rtc_configuration=RTC_CONFIG,
            media_stream_constraints={"video": True, "audio": False}
        )
        if ctx.video_processor:
            st.session_state['emo'] = ctx.video_processor.current_state
        
        status = st.session_state['emo']
        if status == "Frustrated":
            st.error(f"Status: {status} (Scaffolding Triggered)")
        else:
            st.success(f"Status: {status}")

    with col_supp:
        # Dynamic Tab Label (The "Ting" notification)
        tab_label = "🔔 Simplified Notes" if status == "Frustrated" else "Simplified Notes"
        t1, t2 = st.tabs(["Desktop View", tab_label])
        with t1:
            desktop_sharing_js()
        with t2:
            if status == "Frustrated":
                st.subheader("🤖 Lumina Simplification: Plant Nutrition")
                st.markdown("""
                * **Chlorophyll:** Green pigment needed for food.
                * **The Test:** Boil leaf in alcohol, then add Iodine.
                * **Result:** Blue/Black = Starch is present.
                """)
                st.toast("Notes simplified for you!", icon="💡")
            else:
                st.info("Start tracking to see simplified notes when confused.")

if choice_options == "About":
    st.title('Project Lead')
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Puteri Aisyah Sofia")
        # Ensure you have your profile pic in data/profile.png
        try:
            image_1 = Image.open('data/profile.png')
            st.image(image_1, width=250)
        except:
            st.write("[Profile Image Placeholder]")
        st.write("**MSc Applied Computing**")
        st.write("Universiti Teknologi PETRONAS")
        st.write("Email: puteri_25014776@utp.edu.my")
    with col2:
        st.subheader("Research Focus")
        st.write("Specializing in Affective Computing to improve educational outcomes for students with diverse needs.")
        st.markdown("""[LinkedIn Profile](https://www.linkedin.com/in/aisyah-sofia-binti-muzaisham-77631a232/)""")

st.sidebar.divider()
st.sidebar.caption("Lumina AI | 2026 | Al-Khor, Qatar")

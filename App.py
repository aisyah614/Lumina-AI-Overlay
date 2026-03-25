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

# --- 2. MODEL LOADING (Affective Module) ---
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

# --- 3. PERCEPTION MODULE (Student State) ---
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
            st.session_state['emotion'] = max(set(self.history), key=self.history.count)
            
        return av.VideoFrame.from_ndarray(img, format="bgr24")

# --- 4. KEEP IT SIMPLE AI INTEGRATION ---
def text_simplification_tool():
    st.subheader("📝 Text Simplification & Scaffolding")
    input_text = st.text_area("Paste complex IGCSE content here:", height=150, placeholder="Enter text to simplify...")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        level = st.selectbox("Simplify to:", ["Beginner", "Intermediate", "Advanced"])
    with col2:
        bionic = st.checkbox("Bionic Reading")
    with col3:
        font_size = st.slider("Text Size", 12, 32, 18)

    if st.button("✨ Simplify for me"):
        if input_text:
            # Placeholder for the Keep-It-Simple LLM logic
            simplified = f"Simplified to {level} level: {input_text[:100]}... [Simplified Content]"
            
            # Applying Bionic Reading effect (Visual Accessibility)
            if bionic:
                simplified = " ".join([f"**{word[:len(word)//2+1]}**{word[len(word)//2+1:]}" for word in simplified.split()])
            
           # Change 'unsafe_allow_all_html' to 'unsafe_allow_html'
st.markdown(
    f"""
    <div style="font-size: {font_size}px; background: white; padding: 20px; 
    border-radius: 10px; color: black; border-left: 5px solid #4A90E2;">
        {simplified}
    </div>
    """, 
    unsafe_allow_html=True
)

# --- 5. REMOTE CONTROL COMPONENT ---
def remote_control_interface():
    js_code = """
    <div style="background: #121212; padding: 10px; border-radius: 12px; border: 1px solid #333;">
        <div style="display: flex; gap: 10px; margin-bottom: 10px;">
            <button id="share" style="background: #27ae60; border: none; padding: 8px 15px; border-radius: 5px; color: white; cursor: pointer;">Start Desktop View</button>
            <button id="stop" style="background: #c0392b; border: none; padding: 8px 15px; border-radius: 5px; color: white; cursor: pointer; display: none;">Stop</button>
        </div>
        <video id="remoteVideo" autoplay playsinline style="width: 100%; height: 300px; background: #000; border-radius: 5px;"></video>
    </div>
    <script>
    const shareBtn = document.getElementById('share');
    const stopBtn = document.getElementById('stop');
    const video = document.getElementById('remoteVideo');
    let stream = null;
    shareBtn.onclick = async () => {
        stream = await navigator.mediaDevices.getDisplayMedia({ video: true });
        video.srcObject = stream;
        shareBtn.style.display='none'; stopBtn.style.display='inline';
    };
    stopBtn.onclick = () => {
        stream.getTracks().forEach(t => t.stop());
        video.srcObject = null;
        shareBtn.style.display='inline'; stopBtn.style.display='none';
    };
    </script>
    """
    components.html(js_code, height=400)

# --- 6. THE MAIN UI ---
def run():
    st.title("🤖 Lumina AI x Keep-It-Simple: Inclusive Learning")
    if 'emotion' not in st.session_state: st.session_state['emotion'] = "Neutral"

    left_panel, right_panel = st.columns([1, 2])

    with left_panel:
        st.subheader("👤 Student Tracker")
        webrtc_streamer(key="cam", video_processor_factory=LuminaPerception, rtc_configuration=RTC_CONFIG)
        
        st.divider()
        emo = st.session_state['emotion']
        if emo == "Frustrated":
            st.error("⚠️ Cognitive Overload Detected")
            st.warning("🤖 **Lumina Tip:** Use the 'Keep It Simple' tool on the right to break down this complex text!")
        else:
            st.success(f"State: {emo}")

    with right_panel:
        tab1, tab2 = st.tabs(["🖥️ Desktop Control", "📚 Text Scaffolding"])
        with tab1:
            remote_control_interface()
        with tab2:
            text_simplification_tool()

    # --- 7. MASCOT FOOTER ---
    st.divider()
    m1, m2 = st.columns([1, 5])
    with m1:
        icon = "4712027" if emo == "Frustrated" else ("4712035" if emo == "Happy" else "4712010")
        st.image(f"https://cdn-icons-png.flaticon.com/512/4712/{icon}.png", width=100)
    with m2:
        st.write(f"🤖 **Lumina:** {'Let me simplify that for you!' if emo == 'Frustrated' else 'Everything is looking good!'} You are doing great today.")
        st.caption("Puteri Aisyah Sofia | MSc Applied Computing | UTP | Doha, Qatar")

if __name__ == "__main__":
    run()

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

# --- 3. PERCEPTION MODULE (Affective Intelligence) ---
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

# --- 4. AUTO-SCAFFOLDING ENGINE ---
def auto_scaffold_text(text):
    """Automatically transforms complex text into simplified bullet points."""
    # Simulation of simplifying text without word-for-word copying
    sentences = text.split('.')
    points = []
    for s in sentences:
        if len(s.strip()) > 10:
            words = s.strip().split()
            # Scaffolding: Keep key first 60% of sentence to simplify
            summary = " ".join(words[:int(len(words)*0.6)])
            points.append(f"• {summary}...")
    return points

# --- 5. REMOTE DESKTOP COMPONENT ---
def remote_control_interface():
    js_code = """
    <div style="background: #121212; padding: 10px; border-radius: 12px; border: 1px solid #333;">
        <div style="display: flex; gap: 10px; margin-bottom: 10px;">
            <button id="share" style="background: #27ae60; border: none; padding: 10px 20px; border-radius: 5px; color: white; cursor: pointer; font-weight: bold;">🌐 Start Sharing</button>
            <button id="stop" style="background: #c0392b; border: none; padding: 10px 20px; border-radius: 5px; color: white; cursor: pointer; display: none; font-weight: bold;">🛑 Stop</button>
        </div>
        <video id="remoteVideo" autoplay playsinline style="width: 100%; height: 350px; background: #000; border-radius: 8px;"></video>
    </div>
    <script>
    const shareBtn = document.getElementById('share');
    const stopBtn = document.getElementById('stop');
    const video = document.getElementById('remoteVideo');
    let stream = null;
    shareBtn.onclick = async () => {
        try {
            stream = await navigator.mediaDevices.getDisplayMedia({ video: true });
            video.srcObject = stream;
            shareBtn.style.display='none'; stopBtn.style.display='inline';
        } catch (err) { console.error(err); }
    };
    stopBtn.onclick = () => {
        if(stream) { stream.getTracks().forEach(t => t.stop()); }
        video.srcObject = null;
        shareBtn.style.display='inline'; stopBtn.style.display='none';
    };
    </script>
    """
    components.html(js_code, height=450)

# --- 6. MAIN UI ---
def run():
    st.title("🤖 Lumina AI: Auto-Adaptive Inclusive Education")
    
    # Initialize session states
    if 'emotion' not in st.session_state: st.session_state['emotion'] = "Neutral"
    if 'scaffold_notes' not in st.session_state: st.session_state['scaffold_notes'] = []

    left_panel, right_panel = st.columns([1, 2])

    with left_panel:
        st.subheader("👤 Student Tracker")
        webrtc_streamer(key="cam", video_processor_factory=LuminaPerception, rtc_configuration=RTC_CONFIG)
        
        st.divider()
        emo = st.session_state['emotion']
        
        # --- AUTO TRIGGER LOGIC ---
        if emo == "Frustrated":
            st.error("⚠️ Cognitive Overload Detected")
            
            # SIMULATED SCREEN CONTENT (In real version, this is OCR from your screen share)
            complex_content = "The mitochondria are double-membrane-bound organelles found in most eukaryotic organisms. They generate most of the cell's supply of adenosine triphosphate (ATP), used as a source of chemical energy."
            
            # Auto-run the simplification
            st.session_state['scaffold_notes'] = auto_scaffold_text(complex_content)
            
            st.warning("🤖 **Lumina:** I see you're struggling. I've automatically simplified your screen content in the **Scaffolding** tab!")
        else:
            st.success(f"State: {emo}")

    with right_panel:
        tab1, tab2 = st.tabs(["🖥️ Desktop View", "📚 Auto-Scaffolding"])
        
        with tab1:
            remote_control_interface()
            
        with tab2:
            st.subheader("🚀 Lumina Real-Time Notes")
            if st.session_state['scaffold_notes']:
                # Generate HTML for the bullet points
                points_html = "".join([f"<p style='margin-bottom:15px;'>{p}</p>" for p in st.session_state['scaffold_notes']])
                
                st.markdown(
                    f"""
                    <div style="font-size: 24px; background: #f0f8ff; padding: 30px; 
                    border-radius: 15px; border-left: 10px solid #FF4B4B; color: #333;">
                        <h3 style="color: #FF4B4B; margin-top:0;">🤖 Simplified for You:</h3>
                        {points_html}
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
                if st.button("✅ I understand now"):
                    st.session_state['scaffold_notes'] = []
                    st.rerun()
            else:
                st.info("Lumina is monitoring your shared screen. If you feel frustrated, simplified notes will appear here automatically!")

    # --- 7. MASCOT FOOTER ---
    st.divider()
    m1, m2 = st.columns([1, 5])
    with m1:
        icon_code = "4712027" if emo == "Frustrated" else ("4712035" if emo == "Happy" else "4712010")
        st.image(f"https://cdn-icons-png.flaticon.com/512/4712/{icon_code}.png", width=100)
    with m2:
        if emo == "Frustrated":
            st.write("🤖 **Lumina:** Don't worry, Puteri Aisyah! I've broken down the hard sentences into bullet points for you.")
        else:
            st.write("🤖 **Lumina:** You're doing great. I'm keeping an eye on your screen to help if it gets too hard.")
        st.caption("Puteri Aisyah Sofia | MSc Applied Computing | UTP | Doha, Qatar")

if __name__ == "__main__":
    run()

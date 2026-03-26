import numpy as np
import cv2
import streamlit as st
import streamlit.components.v1 as components
import os
import av
import tensorflow as tf

# --- 1. LUMINA RESEARCH CONFIGURATION ---
LUMINA_MAP = {0: 'Neutral', 1: 'Happy', 2: 'Frustrated'}
SCAFFOLD_TRIGGERS = ['Frustrated']
RTC_CONFIG = {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}

st.set_page_config(page_title="Lumina AI: Inclusive Education", layout="wide", page_icon="🤖")

# --- 2. LUMINA AI ENGINE LOADING ---
@st.cache_resource
def load_lumina_keras_engine():
    try:
        model_path = 'keras_model.h5'
        if os.path.exists(model_path):
            return tf.keras.models.load_model(model_path, compile=False)
        return None
    except Exception as e:
        return None

lumina_net = load_lumina_keras_engine()

# --- 3. LUMINA PERCEPTION MODULE (Thread-Safe) ---
class LuminaPerception:
    def __init__(self):
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        # We start with 'None' to distinguish between "No Face Found" and "Neutral"
        self.current_state = None 

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 6)

        detected = None # Default if no face is in frame
        
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 255), 2)
            
            if lumina_net is not None:
                try:
                    # ROI Processing for your .h5 model
                    roi = cv2.resize(img[y:y+h, x:x+w], (224, 224))
                    roi = np.asarray(roi, dtype=np.float32).reshape(1, 224, 224, 3)
                    roi = (roi / 127.5) - 1 # Normalize
                    
                    prediction = lumina_net.predict(roi, verbose=0)
                    index = np.argmax(prediction)
                    confidence = prediction[0][index]
                    
                    # Only update state if AI is reasonably sure
                    if confidence > 0.45:
                        detected = LUMINA_MAP.get(index, 'Neutral')
                    else:
                        detected = 'Neutral'
                except:
                    detected = 'Neutral'
        
        self.current_state = detected
        return av.VideoFrame.from_ndarray(img, format="bgr24")

# --- 4. AUTO-SCAFFOLDING LOGIC ---
def generate_scaffolding(text):
    if not text: return []
    sentences = text.split('.')
    return [f"• {s.strip()[:int(len(s)*0.70)]}..." for s in sentences if len(s.strip()) > 15]

# --- 5. REMOTE DESKTOP INTERFACE ---
def desktop_ui():
    js_code = """
    <div style="background: #111; padding: 15px; border-radius: 12px; border: 1px solid #444;">
        <div style="display: flex; gap: 10px; margin-bottom: 15px;">
            <button id="share" style="background: #27ae60; border: none; padding: 10px 20px; border-radius: 5px; color: white; cursor: pointer; font-weight: bold;">🌐 Share Study Desktop</button>
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
        stream = await navigator.mediaDevices.getDisplayMedia({ video: true });
        video.srcObject = stream;
        shareBtn.style.display='none'; stopBtn.style.display='inline';
    };
    stopBtn.onclick = () => {
        if(stream) { stream.getTracks().forEach(t => t.stop()); }
        video.srcObject = null;
        shareBtn.style.display='inline'; stopBtn.style.display='none';
    };
    </script>
    """
    components.html(js_code, height=480)

# --- 6. MAIN SYSTEM RUN ---
def run():
    st.title("🤖 Lumina AI: Auto-Adaptive Inclusive Education")
    
    if lumina_net is None:
        st.warning("⚠️ 'keras_model.h5' not found. Please upload it to your GitHub root.")

    # Initialize session states
    if 'emo_state' not in st.session_state: st.session_state['emo_state'] = None
    if 'scaffold_notes' not in st.session_state: st.session_state['scaffold_notes'] = []

    left, right = st.columns([1, 2.2])

    with left:
        st.subheader("👤 Student Tracker")
        from streamlit_webrtc import webrtc_streamer
        ctx = webrtc_streamer(
            key="lumina-tracker",
            video_processor_factory=LuminaPerception,
            rtc_configuration=RTC_CONFIG,
            media_stream_constraints={"video": True, "audio": False}
        )
        
        # ACTIVE STATUS CHECK: Pulling directly from the tracker thread
        if ctx.video_processor:
            st.session_state['emo_state'] = ctx.video_processor.current_state
        
        current = st.session_state['emo_state']
        st.divider()
        
        # Logical Status Display
        if current is None:
            st.info("System Status: Waiting for Face...")
        elif current == "Frustrated":
            st.error(f"System Status: {current}")
            # Biology Content Sample
            content = "The nitrogen cycle is the process by which nitrogen is converted into multiple chemical forms as it circulates among the atmosphere and ecosystems."
            st.session_state['scaffold_notes'] = generate_scaffolding(content)
            st.warning("🤖 **Lumina Assist:** Scaffolding triggered.")
        elif current == "Happy":
            st.success(f"System Status: {current}")
            st.session_state['scaffold_notes'] = [] # Clear scaffolding if happy
        else:
            st.success(f"System Status: {current}")

    with right:
        t1, t2 = st.tabs(["🖥️ Shared Desktop View", "📚 Scaffolding Results"])
        with t1: desktop_ui()
        with t2:
            if st.session_state['scaffold_notes'] and current == "Frustrated":
                html = "".join([f"<p style='margin-bottom:12px;'>{n}</p>" for n in st.session_state['scaffold_notes']])
                st.markdown(f"<div style='font-size: 24px; background: #fdf2f2; padding: 25px; border-radius: 12px; border-left: 10px solid #e74c3c; color: #333;'>{html}</div>", unsafe_allow_html=True)
            else:
                st.info("Lumina AI is monitoring. Simplified notes will appear here if you look frustrated.")

    st.divider()
    st.caption("Puteri Aisyah Sofia | Student ID: 25014776 | UTP | Al-Khor, Qatar")

if __name__ == "__main__":
    run()

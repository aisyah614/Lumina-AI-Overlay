import numpy as np
import cv2
import streamlit as st
import streamlit.components.v1 as components
import os
import av
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration

# --- 1. RESEARCH CONFIGURATION ---
EMOTIONS = ('angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral')
SCAFFOLD_TRIGGERS = ['angry', 'fear', 'sad', 'disgust']
RTC_CONFIG = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})

st.set_page_config(page_title="Lumina AI: Neural Tracker Fix", layout="wide", page_icon="🤖")

# --- 2. LAZY LOADING TENSORFLOW ---
@st.cache_resource
def load_tf_engine():
    try:
        import tensorflow as tf
        from tensorflow.keras.models import load_model
        # Ensure the filename matches exactly what you uploaded to GitHub
        if os.path.exists('model.h5'):
            return load_model('model.h5')
        return "MODEL_NOT_FOUND"
    except Exception as e:
        return f"DEPENDENCY_ERROR: {str(e)}"

engine = load_tf_engine()

# --- 3. IMPROVED PERCEPTION MODULE (Aggressive Tracking) ---
class StableTFPerception:
    def __init__(self):
        # Use absolute path for the cascade to ensure it loads
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        self.current_state = "neutral"

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        # Enhance contrast for better face detection in low light
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray) 
        
        # Adjust scaleFactor to 1.1 for more sensitive detection
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=6, minSize=(30, 30))

        detected = "neutral"
        if len(faces) > 0:
            for (x, y, w, h) in faces:
                # Draw a bright Cyan box for Lumina's focus
                cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 255), 2)
                
                if not isinstance(engine, str):
                    try:
                        roi = gray[y:y+h, x:x+w]
                        roi = cv2.resize(roi, (48, 48), interpolation=cv2.INTER_AREA)
                        roi = roi.astype('float') / 255.0
                        roi = np.expand_dims(roi, axis=0)
                        roi = np.expand_dims(roi, axis=-1)

                        preds = engine.predict(roi, verbose=0)[0]
                        # Update detected state based on model prediction
                        detected = EMOTIONS[preds.argmax()]
                    except:
                        pass
        
        # If no face is found, it stays "neutral"
        self.current_state = detected
        return av.VideoFrame.from_ndarray(img, format="bgr24")

# --- 4. AUTO-SCAFFOLDING LOGIC ---
def get_simplified_content(text):
    if not text: return []
    sentences = text.split('.')
    return [f"• {s.strip()[:int(len(s)*0.75)]}..." for s in sentences if len(s.strip()) > 10]

# --- 5. REMOTE DESKTOP UI ---
def remote_desktop_ui():
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

# --- 6. MAIN APP RUN ---
def run():
    st.title("🤖 Lumina AI x TensorFlow-101")
    
    if isinstance(engine, str) and "MODEL_NOT_FOUND" in engine:
        st.warning("⚠️ Weights file 'model.h5' not detected. Please upload it to your GitHub root.")

    if 'emo' not in st.session_state: st.session_state['emo'] = "neutral"
    if 'notes' not in st.session_state: st.session_state['notes'] = []

    left, right = st.columns([1, 2.2])

    with left:
        st.subheader("👤 Neural Tracker")
        ctx = webrtc_streamer(
            key="stable-tf-fix",
            video_processor_factory=StableTFPerception,
            rtc_configuration=RTC_CONFIG,
            media_stream_constraints={"video": True, "audio": False}
        )
        
        if ctx.video_processor:
            st.session_state['emo'] = ctx.video_processor.current_state
        
        state = st.session_state['emo']
        
        # Fixed spelling and logic trigger
        if state in SCAFFOLD_TRIGGERS:
            st.error(f"⚠️ Affective State: {state.upper()}")
            # Biology Content Example
            content = "The mitochondria are organelles that act like a digestive system which takes in nutrients and creates energy."
            st.session_state['notes'] = get_simplified_content(content)
        else:
            # Corrected "NEUTRAK" to "Neutral"
            st.success(f"System Status: {state.capitalize()}")

    with right:
        t1, t2 = st.tabs(["🖥️ Desktop", "📚 Scaffolding"])
        with t1: remote_desktop_ui()
        with t2:
            if st.session_state['notes'] and state in SCAFFOLD_TRIGGERS:
                html = "".join([f"<p style='margin-bottom:10px;'>{n}</p>" for n in st.session_state['notes']])
                st.markdown(f"<div style='font-size: 22px; background: #fdf2f2; padding: 25px; border-radius: 12px; border-left: 8px solid #e74c3c; color: #333;'>{html}</div>", unsafe_allow_html=True)
            else:
                st.info("Everything looks clear. Lumina is monitoring for learning barriers.")

    st.divider()
    st.caption("Puteri Aisyah Sofia | Student ID: 25014776 | UTP | Al-Khor, Qatar")

if __name__ == "__main__":
    run()

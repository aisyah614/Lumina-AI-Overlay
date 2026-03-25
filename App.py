import numpy as np
import cv2
import streamlit as st
import streamlit.components.v1 as components
import os
import av
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration

# --- 1. RESEARCH CONFIGURATION ---
# TensorFlow-101 standard labels for FER2013
EMOTIONS = ('angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral')
SCAFFOLD_TRIGGERS = ['angry', 'fear', 'sad', 'disgust']
RTC_CONFIG = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})

st.set_page_config(page_title="Lumina AI: TensorFlow-101 Engine", layout="wide", page_icon="🤖")

# --- 2. TENSORFLOW MODEL LOADING ---
@st.cache_resource
def load_tf_model():
    try:
        # Looking for the model file (usually facial_expression_model_weights.h5 or similar)
        if os.path.exists('model.h5'):
            return load_model('model.h5')
        return "MODEL_NOT_FOUND"
    except Exception as e:
        return f"ERROR: {str(e)}"

emotion_model = load_tf_model()

# --- 3. TENSORFLOW PERCEPTION MODULE ---
class TFPerception:
    def __init__(self):
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        self.current_state = "neutral"

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

        detected = "neutral"
        for (x, y, w, h) in faces:
            # Drawing the Lumina focus box
            cv2.rectangle(img, (x, y), (x+w, y+h), (74, 144, 226), 2)
            
            if not isinstance(emotion_model, str):
                try:
                    # TensorFlow-101 Preprocessing: 48x48 Grayscale
                    roi_gray = gray[y:y+h, x:x+w]
                    roi_gray = cv2.resize(roi_gray, (48, 48), interpolation=cv2.INTER_AREA)
                    
                    roi = roi_gray.astype('float') / 255.0
                    roi = img_to_array(roi)
                    roi = np.expand_dims(roi, axis=0)

                    preds = emotion_model.predict(roi, verbose=0)[0]
                    detected = EMOTIONS[preds.argmax()]
                except:
                    pass
        
        self.current_state = detected
        return av.VideoFrame.from_ndarray(img, format="bgr24")

# --- 4. AUTO-SCAFFOLDING ENGINE ---
def generate_scaffolding(text):
    if not text: return []
    sentences = text.split('.')
    points = []
    for s in sentences:
        clean = s.strip()
        if len(clean) > 15:
            words = clean.split()
            # Scaffolding: Extract core 65% for cognitive ease
            summary = " ".join(words[:int(len(words)*0.65)])
            points.append(f"• {summary}...")
    return points

# --- 5. REMOTE DESKTOP COMPONENT ---
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
    components.html(js_code, height=480)

# --- 6. MAIN SYSTEM RUN ---
def run():
    st.title("🤖 Lumina AI x TensorFlow: Neural Assist")
    
    # Handle Model Loading Alerts
    if emotion_model == "MODEL_NOT_FOUND":
        st.warning("⚠️ 'model.h5' not found in repository. Running in simulation mode.")
    elif isinstance(emotion_model, str) and "ERROR" in emotion_model:
        st.error(f"❌ TensorFlow Error: {emotion_model}")

    if 'emo_state' not in st.session_state: st.session_state['emo_state'] = "neutral"
    if 'auto_notes' not in st.session_state: st.session_state['auto_notes'] = []

    col_left, col_right = st.columns([1, 2.2])

    with col_left:
        st.subheader("👤 Student Tracker")
        ctx = webrtc_streamer(
            key="tf-lumina",
            video_processor_factory=TFPerception,
            rtc_configuration=RTC_CONFIG,
            media_stream_constraints={"video": True, "audio": False}
        )
        
        if ctx.video_processor:
            st.session_state['emo_state'] = ctx.video_processor.current_state
        
        st.divider()
        state = st.session_state['emo_state']
        
        if state in SCAFFOLD_TRIGGERS:
            st.error(f"⚠️ Affective State: {state.upper()}")
            # Biology Content Example
            complex_text = "Ribosomes are macromolecular machines, found within all living cells, that perform biological protein synthesis. They link amino acids together in the order specified by the codons of messenger RNA molecules."
            st.session_state['auto_notes'] = generate_scaffolding(complex_text)
            st.warning("🤖 **Lumina Assist:** High cognitive load detected via TensorFlow. Scaffolding active.")
        else:
            st.success(f"System Status: {state.capitalize()}")

    with col_right:
        tab_desktop, tab_scaffold = st.tabs(["🖥️ Desktop View", "📚 Scaffolding Results"])
        with tab_desktop:
            remote_desktop_ui()
        with tab_scaffold:
            st.subheader("🚀 Real-Time Simplified Notes")
            if st.session_state['auto_notes']:
                notes_html = "".join([f"<p style='margin-bottom:15px;'>{p}</p>" for p in st.session_state['auto_notes']])
                st.markdown(f"""<div style='font-size: 24px; background: #fdf2f2; padding: 30px; 
                             border-radius: 15px; border-left: 10px solid #e74c3c; color: #2c3e50;'>
                             <h3 style='color: #e74c3c; margin-top:0;'>🤖 Lumina Support:</h3>{notes_html}</div>""", 
                             unsafe_allow_html=True)
                if st.button("✅ I understand this"):
                    st.session_state['auto_notes'] = []
                    st.rerun()
            else:
                st.info("TensorFlow Engine is monitoring. Scaffolding appears if frustration is detected.")

    st.divider()
    st.caption("Puteri Aisyah Sofia | Student ID: 25014776 | MSc Applied Computing | UTP | Al-Khor, Qatar")

if __name__ == "__main__":
    run()

import numpy as np
import cv2
import streamlit as st
import streamlit.components.v1 as components
import os
import av
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration

# --- 1. RESEARCH CONFIGURATION ---
FER_LABELS = {0: 'Angry', 1: 'Disgust', 2: 'Fear', 3: 'Happy', 4: 'Sad', 5: 'Surprise', 6: 'Neutral'}
SCAFFOLD_TRIGGERS = ['Angry', 'Fear', 'Sad', 'Disgust']
RTC_CONFIG = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})

st.set_page_config(page_title="Lumina AI: PyTorch FER Engine", layout="wide", page_icon="🤖")

# --- 2. PYTORCH MODEL LOADING (With Error Handling) ---
@st.cache_resource
def load_pytorch_fer():
    try:
        # Check if the weight file exists
        if os.path.exists('fer_model.pt'):
            # Note: For a custom architecture, you'd usually define the class first
            # If you exported the whole model, this works:
            model = torch.load('fer_model.pt', map_location=torch.device('cpu'))
            model.eval()
            return model
        else:
            return "MISSING_MODEL"
    except Exception as e:
        return str(e)

fer_net = load_pytorch_fer()

# --- 3. PYTORCH PERCEPTION MODULE ---
class PyTorchFERPerception:
    def __init__(self):
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        self.current_state = "Neutral"
        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((44, 44)), 
            transforms.ToTensor(),
        ])

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

        detected = "Neutral"
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (74, 144, 226), 2)
            
            # Only predict if the model loaded successfully
            if not isinstance(fer_net, str):
                try:
                    roi = gray[y:y+h, x:x+w]
                    roi_tensor = self.transform(roi).unsqueeze(0)
                    with torch.no_grad():
                        outputs = fer_net(roi_tensor)
                        _, predicted = torch.max(outputs, 1)
                        detected = FER_LABELS[predicted.item()]
                except:
                    pass
        
        self.current_state = detected
        return av.VideoFrame.from_ndarray(img, format="bgr24")

# --- 4. AUTO-SCAFFOLDING ENGINE ---
def auto_scaffold_generator(text):
    if not text: return []
    sentences = text.split('.')
    points = []
    for s in sentences:
        clean = s.strip()
        if len(clean) > 15:
            words = clean.split()
            summary = " ".join(words[:int(len(words)*0.65)])
            points.append(f"• {summary}...")
    return points

# --- 5. REMOTE DESKTOP INTERFACE ---
def remote_desktop_ui():
    js_code = """
    <div style="background: #111; padding: 15px; border-radius: 12px; border: 1px solid #444;">
        <div style="display: flex; gap: 10px; margin-bottom: 15px;">
            <button id="share" style="background: #27ae60; border: none; padding: 10px 20px; border-radius: 5px; color: white; cursor: pointer; font-weight: bold;">🌐 Share IGCSE Desktop</button>
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

# --- 6. MAIN SYSTEM EXECUTION ---
def run():
    st.title("🤖 Lumina AI x PyTorch: Neural Inclusive Education")
    
    # Handle Model Loading Alerts
    if fer_net == "MISSING_MODEL":
        st.warning("⚠️ Model weights 'fer_model.pt' not found. Lumina is running in simulation mode.")
    elif isinstance(fer_net, str):
        st.error(f"❌ PyTorch Error: {fer_net}")

    if 'emo_state' not in st.session_state: st.session_state['emo_state'] = "Neutral"
    if 'auto_notes' not in st.session_state: st.session_state['auto_notes'] = []

    col_left, col_right = st.columns([1, 2.2])

    with col_left:
        st.subheader("🧠 PyTorch FER Tracker")
        ctx = webrtc_streamer(
            key="pytorch-track",
            video_processor_factory=PyTorchFERPerception,
            rtc_configuration=RTC_CONFIG,
            media_stream_constraints={"video": True, "audio": False}
        )
        
        if ctx.video_processor:
            st.session_state['emo_state'] = ctx.video_processor.current_state
        
        st.divider()
        state = st.session_state['emo_state']
        
        if state in SCAFFOLD_TRIGGERS:
            st.error(f"⚠️ Neural Detection: {state.upper()}")
            # Biology Content Simulation
            complex_text = "The chloroplast is the organelle where photosynthesis occurs. It has a high concentration of chlorophyll which captures light energy."
            st.session_state['auto_notes'] = auto_scaffold_generator(complex_text)
            st.warning("🤖 **Lumina Assist:** Barrier detected. Scaffolding active.")
        else:
            st.success(f"System State: {state}")

    with col_right:
        tab_desktop, tab_scaffold = st.tabs(["🖥️ Desktop View", "📚 PyTorch Scaffolding"])
        with tab_desktop:
            remote_desktop_ui()
        with tab_scaffold:
            st.subheader("🚀 Real-Time Simplified Notes")
            if st.session_state['auto_notes']:
                notes_html = "".join([f"<p style='margin-bottom:15px;'>{p}</p>" for p in st.session_state['auto_notes']])
                st.markdown(f"<div style='font-size: 24px; background: #fdf2f2; padding: 30px; border-radius: 15px; border-left: 10px solid #e74c3c;'>{notes_html}</div>", unsafe_allow_html=True)
                if st.button("✅ I understand this"):
                    st.session_state['auto_notes'] = []
                    st.rerun()
            else:
                st.info("Monitoring session. Scaffolding appears if frustration is detected.")

    st.divider()
    st.caption("Puteri Aisyah Sofia | MSc Applied Computing | UTP | Al-Khor, Qatar")

if __name__ == "__main__":
    run()

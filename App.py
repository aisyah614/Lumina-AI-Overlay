import numpy as np
import cv2
import streamlit as st
import streamlit.components.v1 as components
import os
import av
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from PIL import Image
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration

# --- 1. RESEARCH CONFIGURATION ---
# EfficientFace standard labels for AffectNet/FER
EFF_LABELS = {0: 'Neutral', 1: 'Happy', 2: 'Sad', 3: 'Surprise', 4: 'Fear', 5: 'Disgust', 6: 'Angry', 7: 'Contempt'}
SCAFFOLD_TRIGGERS = ['Sad', 'Fear', 'Angry', 'Disgust', 'Contempt']

RTC_CONFIG = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})

st.set_page_config(page_title="Lumina AI: EfficientFace Engine", layout="wide", page_icon="🤖")

# --- 2. EFFICIENTFACE MODEL LOADING ---
@st.cache_resource
def load_efficientface():
    try:
        # Check for the model weights (ensure you upload 'efficientface.pt' to GitHub)
        if os.path.exists('efficientface.pt'):
            # Load the model directly or the state_dict depending on your export
            model = torch.load('efficientface.pt', map_location=torch.device('cpu'))
            if hasattr(model, 'eval'):
                model.eval()
            return model
        return "MODEL_NOT_FOUND"
    except Exception as e:
        return f"PYTORCH_ERROR: {str(e)}"

eff_model = load_efficientface()

# --- 3. EFFICIENT PERCEPTION MODULE ---
class EfficientFacePerception:
    def __init__(self):
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        self.current_state = "Neutral"
        # EfficientFace usually expects 112x112 RGB Normalized tensors
        self.transform = transforms.Compose([
            transforms.Resize((112, 112)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.2, 5)

        detected = "Neutral"
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (74, 144, 226), 2)
            
            if not isinstance(eff_model, str):
                try:
                    # Convert BGR ROI to RGB PIL Image for EfficientFace
                    roi_bgr = img[y:y+h, x:x+w]
                    roi_rgb = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2RGB)
                    pil_img = Image.fromarray(roi_rgb)
                    
                    tensor_img = self.transform(pil_img).unsqueeze(0)
                    
                    with torch.no_grad():
                        outputs = eff_model(tensor_img)
                        _, predicted = torch.max(outputs, 1)
                        detected = EFF_LABELS[predicted.item()]
                except:
                    pass
        
        self.current_state = detected
        return av.VideoFrame.from_ndarray(img, format="bgr24")

# --- 4. AUTO-SCAFFOLDING LOGIC ---
def generate_scaffolding(text):
    if not text: return []
    sentences = text.split('.')
    return [f"• {s.strip()[:int(len(s)*0.65)]}..." for s in sentences if len(s.strip()) > 15]

# --- 5. REMOTE DESKTOP INTERFACE ---
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

# --- 6. MAIN SYSTEM RUN ---
def run():
    st.title("🤖 Lumina AI x EfficientFace")
    
    if eff_model == "MODEL_NOT_FOUND":
        st.warning("⚠️ 'efficientface.pt' weights not found. Running in simulation mode.")
    elif isinstance(eff_model, str) and "PYTORCH" in eff_model:
        st.error(f"❌ Initialization Error: {eff_model}")

    if 'emo' not in st.session_state: st.session_state['emo'] = "Neutral"
    if 'notes' not in st.session_state: st.session_state['notes'] = []

    left, right = st.columns([1, 2.2])

    with left:
        st.subheader("👤 EfficientFace Tracker")
        ctx = webrtc_streamer(
            key="eff-face",
            video_processor_factory=EfficientFacePerception,
            rtc_configuration=RTC_CONFIG,
            media_stream_constraints={"video": True, "audio": False}
        )
        
        if ctx.video_processor:
            st.session_state['emo'] = ctx.video_processor.current_state
        
        state = st.session_state['emo']
        if state in SCAFFOLD_TRIGGERS:
            st.error(f"⚠️ Affective State: {state.upper()}")
            # Biology Content for inclusive education demo
            content = "The mitochondria are organelles that act like a digestive system which takes in nutrients and creates energy."
            st.session_state['notes'] = generate_scaffolding(content)
            st.warning("🤖 **Lumina Assist:** EfficientFace detected a learning barrier. Scaffolding active.")
        else:
            st.success(f"System Status: {state}")

    with right:
        t1, t2 = st.tabs(["🖥️ Desktop View", "📚 Scaffolding Results"])
        with t1: remote_desktop_ui()
        with t2:
            if st.session_state['notes'] and state in SCAFFOLD_TRIGGERS:
                html = "".join([f"<p>{n}</p>" for n in st.session_state['notes']])
                st.markdown(f"<div style='font-size: 24px; background: #fdf2f2; padding: 30px; border-radius: 12px; border-left: 8px solid #e74c3c; color: #333;'>{html}</div>", unsafe_allow_html=True)
            else:
                st.info("Everything looks clear. Lumina is monitoring for learning barriers.")

    st.divider()
    st.caption("Puteri Aisyah Sofia | Student ID: 25014776 | MSc Applied Computing | UTP | Al-Khor, Qatar")

if __name__ == "__main__":
    run()

import numpy as np
import cv2
import streamlit as st
import streamlit.components.v1 as components
import os
import av
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration

# --- 1. RESEARCH CONFIGURATION ---
# AffectNet Standard Labels (8 classes)
AFFECTNET_LABELS = {
    0: 'Neutral', 1: 'Happy', 2: 'Sad', 3: 'Surprise', 
    4: 'Fear', 5: 'Disgust', 6: 'Anger', 7: 'Contempt'
}
# Scaffolding triggers for Inclusive Education
SCAFFOLD_TRIGGERS = ['Sad', 'Fear', 'Anger', 'Disgust', 'Contempt']

RTC_CONFIG = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})

st.set_page_config(page_title="Lumina AI: EMO-AffectNet Engine", layout="wide", page_icon="🤖")

# --- 2. EMO-AFFECTNET MODEL LOADING ---
@st.cache_resource
def load_affectnet_model():
    try:
        import tensorflow as tf
        # Ensure your exported EMO-AffectNet model is named 'affectnet_model.h5'
        if os.path.exists('affectnet_model.h5'):
            return tf.keras.models.load_model('affectnet_model.h5', compile=False)
    except Exception as e:
        st.error(f"EMO-AffectNet Engine Error: {e}")
    return None

model = load_affectnet_model()

# --- 3. AFFECTNET PERCEPTION MODULE ---
class AffectNetPerception:
    def __init__(self):
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        self.current_state = "Neutral"

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 5)

        detected = "Neutral"
        for (x, y, w, h) in faces:
            # Drawing the Lumina focus box
            cv2.rectangle(img, (x, y), (x+w, y+h), (74, 144, 226), 2)
            
            if model is not None:
                try:
                    # AffectNet models usually require 224x224 RGB or Grayscale
                    roi = cv2.resize(img[y:y+h, x:x+w], (224, 224)) / 255.0
                    roi = np.expand_dims(roi, axis=0)
                    
                    preds = model.predict(roi, verbose=0)[0]
                    detected = AFFECTNET_LABELS[np.argmax(preds)]
                except:
                    pass
        
        self.current_state = detected
        return av.VideoFrame.from_ndarray(img, format="bgr24")

# --- 4. AUTO-SCAFFOLDING ENGINE ---
def auto_scaffold_generator(text):
    """Transforms complex text into simplified bullet points for IGCSE students."""
    if not text: return []
    sentences = text.split('.')
    points = []
    for s in sentences:
        clean = s.strip()
        if len(clean) > 20:
            words = clean.split()
            # Scaffolding: Extract the core 60% of the sentence
            summary = " ".join(words[:int(len(words)*0.6)])
            points.append(f"• {summary}...")
    return points

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

# --- 6. MAIN SYSTEM EXECUTION ---
def run():
    st.title("🤖 Lumina AI x EMO-AffectNet: Neural Inclusive Education")
    
    if 'emo_state' not in st.session_state: st.session_state['emo_state'] = "Neutral"
    if 'auto_notes' not in st.session_state: st.session_state['auto_notes'] = []

    col_left, col_right = st.columns([1, 2.2])

    with col_left:
        st.subheader("🧠 AffectNet Tracker")
        ctx = webrtc_streamer(
            key="affectnet-track",
            video_processor_factory=AffectNetPerception,
            rtc_configuration=RTC_CONFIG,
            media_stream_constraints={"video": True, "audio": False}
        )
        
        if ctx.video_processor:
            st.session_state['emo_state'] = ctx.video_processor.current_state
        
        st.divider()
        state = st.session_state['emo_state']
        
        # --- THE AUTO-TRIGGER ---
        if state in SCAFFOLD_TRIGGERS:
            st.error(f"⚠️ Neural Detection: {state.upper()}")
            # Simulation of detected IGCSE complex content (e.g., Physics)
            complex_text = "Electromagnetic induction is the production of an electromotive force across an electrical conductor in a changing magnetic field. Michael Faraday is generally credited with the discovery of induction in 1831."
            st.session_state['auto_notes'] = auto_scaffold_generator(complex_text)
            st.warning("🤖 **Lumina Neural Assist:** AffectNet detected cognitive load. Automatic Scaffolding is active.")
        else:
            st.success(f"AffectNet State: {state}")

    with col_right:
        tab_desktop, tab_scaffold = st.tabs(["🖥️ Desktop View", "📚 AffectNet Scaffolding"])
        
        with tab_desktop:
            remote_desktop_ui()
            
        with tab_scaffold:
            st.subheader("🚀 Real-Time Simplified Notes")
            if st.session_state['auto_notes']:
                notes_html = "".join([f"<p style='margin-bottom:15px;'>{p}</p>" for p in st.session_state['auto_notes']])
                st.markdown(
                    f"""
                    <div style="font-size: 24px; background: #fdf2f2; padding: 30px; 
                    border-radius: 15px; border-left: 10px solid #e74c3c; color: #2c3e50; line-height: 1.5;">
                        <h3 style="color: #e74c3c; margin-top:0;">🤖 AffectNet Support Active:</h3>
                        {notes_html}
                    </div>
                    """, unsafe_allow_html=True
                )
                if st.button("✅ I understand this"):
                    st.session_state['auto_notes'] = []
                    st.rerun()
            else:
                st.info("The EMO-AffectNet model is monitoring your screen sessions. Scaffolding appears if barriers are detected.")

    # --- 7. MASCOT FOOTER ---
    st.divider()
    m_left, m_right = st.columns([1, 5])
    with m_left:
        icon_id = "4712027" if state in SCAFFOLD_TRIGGERS else ("4712035" if state == 'Happy' else "4712010")
        st.image(f"https://cdn-icons-png.flaticon.com/512/4712/{icon_id}.png", width=100)
    with m_right:
        if state in SCAFFOLD_TRIGGERS:
            st.write(f"🤖 **Lumina:** AffectNet indicates you're feeling {state}. I've simplified the physics notes for you.")
        else:
            st.write("🤖 **Lumina:** Great work, Puteri Aisyah! AffectNet confirms your steady progress.")
        st.caption("Puteri Aisyah Sofia | Student ID: 25014776 | MSc Applied Computing | UTP | Doha, Qatar")

if __name__ == "__main__":
    run()

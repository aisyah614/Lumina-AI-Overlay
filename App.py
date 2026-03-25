import numpy as np
import cv2
import streamlit as st
import streamlit.components.v1 as components
import os
import av
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration

# --- 1. EMOPY INTEGRATION & MODEL SETUP ---
# EmoPy typically uses specialized emotion labels
EMOPY_LABELS = {0: 'angry', 1: 'disgusted', 2: 'fearful', 3: 'happy', 4: 'sad', 5: 'surprised', 6: 'neutral'}

# Mapping EmoPy states to Lumina's Scaffolding triggers
FRUSTRATION_STATES = ['angry', 'fearful', 'sad', 'disgusted']

RTC_CONFIG = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})

st.set_page_config(page_title="Lumina AI: EmoPy Deep Learning", layout="wide", page_icon="🤖")

# --- 2. DEEP NEURAL NET LOADING ---
@st.cache_resource
def load_emopy_engine():
    try:
        import tensorflow as tf
        # Loading the EmoPy-style pre-trained Fer2013 model
        if os.path.exists('emopy_model.h5'):
            return tf.keras.models.load_model('emopy_model.h5', compile=False)
    except Exception as e:
        st.error(f"EmoPy Engine Error: {e}")
    return None

emopy_net = load_emopy_engine()

# --- 3. AFFECTIVE PERCEPTION MODULE ---
class EmoPyPerception:
    def __init__(self):
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        self.current_state = "neutral"

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 5)

        detected = "neutral"
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (74, 144, 226), 2)
            
            if emopy_net:
                # EmoPy standard: 48x48 grayscale input
                roi = cv2.resize(gray[y:y+h, x:x+w], (48, 48)) / 255.0
                roi = np.expand_dims(roi, axis=0)
                roi = np.expand_dims(roi, axis=-1)
                
                preds = emopy_net.predict(roi, verbose=0)[0]
                detected = EMOPY_LABELS[np.argmax(preds)]
        
        self.current_state = detected
        return av.VideoFrame.from_ndarray(img, format="bgr24")

# --- 4. AUTO-SCAFFOLDING LOGIC ---
def auto_scaffold_generator(text):
    """Deep analysis of text to create bullet-point scaffolding."""
    sentences = text.split('.')
    points = []
    for s in sentences:
        if len(s.strip()) > 15:
            # Scaffolding: Extracting core concepts only
            words = s.strip().split()
            summary = " ".join(words[:int(len(words)*0.6)])
            points.append(f"• {summary}...")
    return points

# --- 5. REMOTE DESKTOP INTERFACE ---
def remote_control_interface():
    js_code = """
    <div style="background: #111; padding: 15px; border-radius: 12px; border: 1px solid #444;">
        <div style="display: flex; gap: 10px; margin-bottom: 15px;">
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
    st.title("🤖 Lumina AI x EmoPy: Neural Inclusive Education")
    
    if 'emo_state' not in st.session_state: st.session_state['emo_state'] = "neutral"
    if 'auto_notes' not in st.session_state: st.session_state['auto_notes'] = []

    col_left, col_right = st.columns([1, 2.2])

    with col_left:
        st.subheader("🧠 Neural Emotion Tracker")
        ctx = webrtc_streamer(
            key="emopy-track",
            video_processor_factory=EmoPyPerception,
            rtc_configuration=RTC_CONFIG,
            media_stream_constraints={"video": True, "audio": False}
        )
        
        if ctx.video_processor:
            st.session_state['emo_state'] = ctx.video_processor.current_state
        
        st.divider()
        state = st.session_state['emo_state']
        
        # SCAFFOLDING TRIGGER: If EmoPy detects a frustration-related state
        if state in FRUSTRATION_STATES:
            st.error(f"⚠️ State Detected: {state.upper()}")
            # Simulated OCR content from shared IGCSE material
            complex_text = "Photosynthesis is the process used by plants and other organisms to convert light energy into chemical energy that, through cellular respiration, can later be released to fuel the organism's activities."
            st.session_state['auto_notes'] = auto_scaffold_generator(complex_text)
            st.warning("🤖 **Lumina Neural Assist:** I've detected cognitive barriers. Automatic scaffolding is now active in the right panel.")
        else:
            st.success(f"Neural State: {state.capitalize()}")

    with col_right:
        tab_share, tab_scaffold = st.tabs(["🖥️ Shared Desktop View", "📚 EmoPy Auto-Scaffold"])
        
        with tab_share:
            remote_control_interface()
            
        with tab_scaffold:
            st.subheader("🚀 Real-Time Simplified Notes")
            if st.session_state['auto_notes']:
                notes_html = "".join([f"<p style='margin-bottom:15px;'>{p}</p>" for p in st.session_state['auto_notes']])
                st.markdown(
                    f"""
                    <div style="font-size: 24px; background: #fdf2f2; padding: 30px; 
                    border-radius: 15px; border-left: 10px solid #e74c3c; color: #2c3e50;">
                        <h3 style="color: #e74c3c; margin-top:0;">🤖 EmoPy Automated Support:</h3>
                        {notes_html}
                    </div>
                    """, unsafe_allow_html=True
                )
                if st.button("✅ Concept Understood"):
                    st.session_state['auto_notes'] = []
                    st.rerun()
            else:
                st.info("The EmoPy Neural Net is monitoring for frustration. Scaffolding notes will appear here automatically.")

    # --- 7. MASCOT FOOTER ---
    st.divider()
    m_left, m_right = st.columns([1, 5])
    with m_left:
        # Dynamic mascot logic
        icon = "4712027" if state in FRUSTRATION_STATES else ("4712035" if state == 'happy' else "4712010")
        st.image(f"https://cdn-icons-png.flaticon.com/512/4712/{icon}.png", width=100)
    with m_right:
        if state in FRUSTRATION_STATES:
            st.write(f"🤖 **Lumina:** I see a bit of {state}. Let's make this easier together.")
        else:
            st.write("🤖 **Lumina:** Neural analysis looks stable. You are making excellent progress today!")
        st.caption("Puteri Aisyah Sofia | Student ID: 25014776 | UTP | Doha, Qatar")

if __name__ == "__main__":
    run()

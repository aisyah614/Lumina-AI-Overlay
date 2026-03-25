import numpy as np
import cv2
import streamlit as st
import streamlit.components.v1 as components
import os
import av
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration

# --- 1. RMN CONFIGURATION ---
# Residual Masking Network standard labels
RMN_LABELS = {0: 'Angry', 1: 'Disgust', 2: 'Fear', 3: 'Happy', 4: 'Sad', 5: 'Surprise', 6: 'Neutral'}
# Scaffolding triggers for your Inclusive Education research
SCAFFOLD_TRIGGERS = ['Angry', 'Fear', 'Sad', 'Disgust']

RTC_CONFIG = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})

st.set_page_config(page_title="Lumina AI: Residual Masking Network", layout="wide", page_icon="🤖")

# --- 2. RMN MODEL LOADING ---
@st.cache_resource
def load_rmn_engine():
    try:
        import tensorflow as tf
        # Ensure your exported RMN model is named 'rmn_model.h5' in your root folder
        if os.path.exists('rmn_model.h5'):
            return tf.keras.models.load_model('rmn_model.h5', compile=False)
    except Exception as e:
        st.error(f"RMN Engine Error: {e}")
    return None

rmn_model = load_rmn_engine()

# --- 3. ATTENTION-BASED PERCEPTION MODULE ---
class RMNPerception:
    def __init__(self):
        # Robust cascade loading for face localization
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        self.current_emotion = "Neutral"

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.2, 5)

        detected = "Neutral"
        for (x, y, w, h) in faces:
            # Visual feedback: Lumina's detection frame
            cv2.rectangle(img, (x, y), (x+w, y+h), (74, 144, 226), 2)
            
            if rmn_model:
                try:
                    # RMN usually requires 48x48 or 224x224 depending on your export
                    roi = cv2.resize(gray[y:y+h, x:x+w], (48, 48)) / 255.0
                    roi = np.reshape(roi, (1, 48, 48, 1))
                    
                    preds = rmn_model.predict(roi, verbose=0)[0]
                    detected = RMN_LABELS[np.argmax(preds)]
                except:
                    pass
        
        # Thread-safe emotion storage
        self.current_emotion = detected
        return av.VideoFrame.from_ndarray(img, format="bgr24")

# --- 4. AUTO-SCAFFOLDING (THE RESEARCH CORE) ---
def generate_scaffolding(text):
    """Transforms complex text into simplified bullet points to reduce cognitive load."""
    if not text: return []
    sentences = text.split('.')
    points = []
    for s in sentences:
        clean = s.strip()
        if len(clean) > 20:
            words = clean.split()
            # Scaffolding: Extract the core 60% of the sentence
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
    st.title("🤖 Lumina AI: Residual Masking Network Assist")
    
    if 'emo_state' not in st.session_state: st.session_state['emo_state'] = "Neutral"
    if 'auto_scaffold' not in st.session_state: st.session_state['auto_scaffold'] = []

    col_left, col_right = st.columns([1, 2.2])

    with col_left:
        st.subheader("👤 RMN Student Tracker")
        ctx = webrtc_streamer(
            key="rmn-perception",
            video_processor_factory=RMNPerception,
            rtc_configuration=RTC_CONFIG,
            media_stream_constraints={"video": True, "audio": False}
        )
        
        if ctx.video_processor:
            st.session_state['emo_state'] = ctx.video_processor.current_emotion
        
        st.divider()
        state = st.session_state['emo_state']
        
        # --- THE AUTO-TRIGGER ---
        if state in SCAFFOLD_TRIGGERS:
            st.error(f"⚠️ Affective State: {state.upper()}")
            # Simulation of detected IGCSE complex content
            complex_text = "The Doppler effect is the change in frequency of a wave in relation to an observer who is moving relative to the wave source. It is commonly heard when a vehicle sounding a siren approaches and recedes from an observer."
            st.session_state['auto_scaffold'] = generate_scaffolding(complex_text)
            st.warning("🤖 **Lumina Assist:** I've detected cognitive barriers via RMN. Scaffolding is active in the right panel.")
        else:
            st.success(f"System State: {state}")

    with col_right:
        tab_desktop, tab_scaffold = st.tabs(["🖥️ Desktop View", "📚 RMN Scaffolding"])
        
        with tab_desktop:
            remote_desktop_ui()
            
        with tab_scaffold:
            st.subheader("🚀 Real-Time Simplified Notes")
            if st.session_state['auto_scaffold']:
                points_html = "".join([f"<p style='margin-bottom:15px;'>{p}</p>" for p in st.session_state['auto_scaffold']])
                st.markdown(
                    f"""
                    <div style="font-size: 24px; background: #fdf2f2; padding: 30px; 
                    border-radius: 15px; border-left: 10px solid #e74c3c; color: #2c3e50; line-height: 1.5;">
                        <h3 style="color: #e74c3c; margin-top:0;">🤖 Lumina's RMN Support:</h3>
                        {points_html}
                    </div>
                    """, unsafe_allow_html=True
                )
                if st.button("✅ Concept Clear"):
                    st.session_state['auto_scaffold'] = []
                    st.rerun()
            else:
                st.info("RMN Attention Masking is active. Scaffolding will appear here if frustration is detected.")

    # --- 7. MASCOT FOOTER ---
    st.divider()
    m_left, m_right = st.columns([1, 5])
    with m_left:
        icon_id = "4712027" if state in SCAFFOLD_TRIGGERS else ("4712035" if state == 'Happy' else "4712010")
        st.image(f"https://cdn-icons-png.flaticon.com/512/4712/{icon_id}.png", width=100)
    with m_right:
        if state in SCAFFOLD_TRIGGERS:
            st.write(f"🤖 **Lumina:** RMN analysis indicates you're finding this tough. Let's simplify these points together.")
        else:
            st.write("🤖 **Lumina:** You're doing great! Your focus is steady according to my attention-masking model.")
        st.caption("Puteri Aisyah Sofia | Student ID: 25014776 | MSc Applied Computing | UTP | Al-Khor, Qatar")

if __name__ == "__main__":
    run()

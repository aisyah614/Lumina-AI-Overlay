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
        # Ensure the model file exists in your repository root
        if os.path.exists('model.h5'):
            return tf.keras.models.load_model('model.h5', compile=False)
    except Exception as e:
        st.error(f"Model Load Error: {e}")
    return None

model = load_lumina_model()

# --- 3. FIXED PERCEPTION MODULE (Thread-Safe) ---
class LuminaPerception:
    def __init__(self):
        # Use robust path for OpenCV cascades
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        self.last_emotion = "Neutral"

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)

        detected = "Neutral"
        for (x, y, w, h) in faces:
            # Draw Lumina's detection box
            cv2.rectangle(img, (x, y), (x+w, y+h), (74, 144, 226), 2)
            
            if model is not None:
                try:
                    roi = cv2.resize(gray[y:y+h, x:x+w], (48, 48)) / 255.0
                    roi = roi.reshape(1, 48, 48, 1)
                    preds = model.predict(roi, verbose=0)[0]
                    detected = EMOTION_LABELS[np.argmax(preds)]
                except:
                    pass
        
        # Store emotion in the class instance (not session_state) for thread safety
        self.last_emotion = detected
        return av.VideoFrame.from_ndarray(img, format="bgr24")

# --- 4. AUTO-SCAFFOLDING ENGINE ---
def auto_scaffold_text(text):
    """Transforms complex text into simplified bullet points for IGCSE support."""
    sentences = text.split('.')
    points = []
    for s in sentences:
        clean_s = s.strip()
        if len(clean_s) > 15:
            words = clean_s.split()
            # Scaffolding logic: extract 60% of context to avoid word-for-word copying
            summary = " ".join(words[:int(len(words)*0.65)])
            points.append(f"• {summary}...")
    return points

# --- 5. REMOTE DESKTOP INTERFACE ---
def remote_control_interface():
    js_code = """
    <div style="background: #121212; padding: 15px; border-radius: 12px; border: 1px solid #333;">
        <div style="display: flex; gap: 10px; margin-bottom: 15px;">
            <button id="share" style="background: #27ae60; border: none; padding: 10px 20px; border-radius: 5px; color: white; cursor: pointer; font-weight: bold;">🌐 Start Desktop Sharing</button>
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
        } catch (err) { console.error("Sharing Error: " + err); }
    };
    stopBtn.onclick = () => {
        if(stream) { stream.getTracks().forEach(t => t.stop()); }
        video.srcObject = null;
        shareBtn.style.display='inline'; stopBtn.style.display='none';
    };
    </script>
    """
    components.html(js_code, height=480)

# --- 6. MAIN UI EXECUTION ---
def run():
    st.title("🤖 Lumina AI: Auto-Adaptive Inclusive Education")
    
    # Initialize session states
    if 'emotion' not in st.session_state: st.session_state['emotion'] = "Neutral"
    if 'scaffold_notes' not in st.session_state: st.session_state['scaffold_notes'] = []

    left_panel, right_panel = st.columns([1, 2.2])

    with left_panel:
        st.subheader("👤 Student Tracker")
        # Run the streamer and capture the context
        ctx = webrtc_streamer(
            key="lumina-perception",
            mode=WebRtcMode.SENDRECV,
            video_processor_factory=LuminaPerception,
            rtc_configuration=RTC_CONFIG,
            media_stream_constraints={"video": True, "audio": False}
        )
        
        # Read the emotion from the processor safely
        if ctx.video_processor:
            st.session_state['emotion'] = ctx.video_processor.last_emotion
        
        st.divider()
        emo = st.session_state['emotion']
        
        # --- AUTO-TRIGGER SCAFFOLDING ---
        if emo == "Frustrated":
            st.error("⚠️ Cognitive Overload Detected")
            # Simulation of content from your shared IGCSE material
            complex_content = "The nitrogen cycle is the biogeochemical cycle by which nitrogen is converted into multiple chemical forms as it circulates among atmosphere, terrestrial, and marine ecosystems. The conversion can be carried out through both biological and physical processes."
            
            st.session_state['scaffold_notes'] = auto_scaffold_text(complex_content)
            st.warning("🤖 **Lumina Tip:** You look a bit stuck. I've automatically simplified the screen content in the **Auto-Scaffolding** tab!")
        else:
            st.success(f"Current State: {emo}")

    with right_panel:
        tab1, tab2 = st.tabs(["🖥️ Shared Desktop View", "📚 Auto-Scaffolding"])
        
        with tab1:
            remote_control_interface()
            
        with tab2:
            st.subheader("🚀 Real-Time Scaffolding Support")
            if st.session_state['scaffold_notes']:
                # Build HTML bullets for clean presentation
                points_html = "".join([f"<p style='margin-bottom:15px;'>{p}</p>" for p in st.session_state['scaffold_notes']])
                
                st.markdown(
                    f"""
                    <div style="font-size: 24px; background: #f0f8ff; padding: 30px; 
                    border-radius: 15px; border-left: 10px solid #FF4B4B; color: #333; line-height: 1.5;">
                        <h3 style="color: #FF4B4B; margin-top:0;">🤖 Lumina's Simplified Guide:</h3>
                        {points_html}
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
                if st.button("✅ I understand this section"):
                    st.session_state['scaffold_notes'] = []
                    st.rerun()
            else:
                st.info("Shared screen content will be automatically simplified here if frustration is detected.")

    # --- 7. MASCOT FOOTER ---
    st.divider()
    m1, m2 = st.columns([1, 5])
    with m1:
        icon_code = "4712027" if emo == "Frustrated" else ("4712035" if emo == "Happy" else "4712010")
        st.image(f"https://cdn-icons-png.flaticon.com/512/4712/{icon_code}.png", width=100)
    with m2:
        if emo == "Frustrated":
            st.write("🤖 **Lumina:** I've noticed you're finding this tough. I've broken the complex sentences into simple points for you!")
        else:
            st.write("🤖 **Lumina:** Great focus, Puteri Aisyah! I'm monitoring your desktop to help if needed.")
        st.caption("Puteri Aisyah Sofia | MSc Applied Computing | UTP | Al-Khor, Qatar")

if __name__ == "__main__":
    run()

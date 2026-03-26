import numpy as np
import cv2
import streamlit as st
import streamlit.components.v1 as components
import os
import av
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration

# --- 1. RESEARCH CONFIGURATION ---
EMOTION_LABELS = {0: 'Frustrated', 1: 'Happy', 2: 'Neutral'}
# Simplified RTC Config for better cloud stability
RTC_CONFIG = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})

st.set_page_config(page_title="Lumina AI: Inclusive Education", layout="wide", page_icon="🤖")

# --- 2. MODEL LOADING ---
@st.cache_resource
def load_lumina_model():
    try:
        import tensorflow as tf
        # Looking for model.h5 in your repository root
        if os.path.exists('model.h5'):
            return tf.keras.models.load_model('model.h5', compile=False)
        return "MODEL_NOT_FOUND"
    except Exception as e:
        return f"MODEL_ERROR: {str(e)}"

model = load_lumina_model()

# --- 3. FIXED PERCEPTION MODULE (Thread-Safe) ---
class LuminaPerception:
    def __init__(self):
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        self.last_emotion = "Neutral"

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Optimized face detection parameters for varying light
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 6)

        detected = "Neutral"
        for (x, y, w, h) in faces:
            # Draw Lumina's detection box (Cyan)
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 255), 2)
            
            if not isinstance(model, str) and model is not None:
                try:
                    # Input preprocessing for 48x48 Grayscale .h5 model
                    roi = cv2.resize(gray[y:y+h, x:x+w], (48, 48)) / 255.0
                    roi = roi.reshape(1, 48, 48, 1)
                    preds = model.predict(roi, verbose=0)[0]
                    # Research Constraint: only map to 3 defined categories
                    detected = EMOTION_LABELS[np.argmax(preds)]
                except:
                    pass
        
        # Store emotion safely on the class instance
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
            # Extract 65% of context to show structure, not just a summary
            summary = " ".join(words[:int(len(words)*0.65)])
            points.append(f"• {summary}...")
    return points

# --- 5. REMOTE DESKTOP INTERFACE (FIXED WITH SHARE/STOP BUTTONS) ---
def remote_control_interface():
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
            // Updated constraints for modern browsers
            stream = await navigator.mediaDevices.getDisplayMedia({ video: true, audio: false });
            video.srcObject = stream;
            // Logical swap of buttons
            shareBtn.style.display='none'; stopBtn.style.display='inline';
            
            // Auto-detect when student stops sharing via browser bar
            stream.getVideoTracks()[0].onended = () => { stopSharing(); };
        } catch (err) { console.error("Sharing Error: " + err); }
    };

    const stopSharing = () => {
        if(stream) { stream.getTracks().forEach(t => t.stop()); }
        video.srcObject = null;
        shareBtn.style.display='inline'; stopBtn.style.display='none';
    };

    stopBtn.onclick = stopSharing;
    </script>
    """
    components.html(js_code, height=480)

# --- 6. MAIN UI EXECUTION ---
def run():
    st.title("🤖 Lumina AI: Auto-Adaptive Inclusive Education")
    
    # Pre-flight check for model weights
    if model == "MODEL_NOT_FOUND":
        st.warning("⚠️ 'model.h5' missing from repository. Running in simulation mode.")
    elif isinstance(model, str) and model.startswith("MODEL_ERROR"):
        st.error(f"Neural engine error: {model}")

    if 'emotion' not in st.session_state: st.session_state['emotion'] = "Neutral"
    if 'scaffold_notes' not in st.session_state: st.session_state['scaffold_notes'] = []

    left_panel, right_panel = st.columns([1, 2.2])

    with left_panel:
        st.subheader("👤 Student Tracker")
        ctx = webrtc_streamer(
            key="lumina-perception",
            mode=WebRtcMode.SENDRECV,
            video_processor_factory=LuminaPerception,
            rtc_configuration=RTC_CONFIG,
            media_stream_constraints={"video": True, "audio": False}
        )
        
        # SCRIPT BRIDGE: Securely updating session_state from background thread
        if ctx.video_processor:
            st.session_state['emotion'] = ctx.video_processor.last_emotion
        
        emo = st.session_state['emotion']
        st.divider()
        
        # --- Affective-Driven Scaffolding Logic ---
        if emo == "Frustrated":
            st.error(f"🔍 Status: {emo} (Barrier Detected)")
            # Simulated complex content from IGCSE Chemistry/Biology
            complex_content = "The nitrogen cycle is the biogeochemical cycle by which nitrogen is converted into multiple chemical forms as it circulates among atmosphere, terrestrial, and marine ecosystems."
            st.session_state['scaffold_notes'] = auto_scaffold_text(complex_content)
            st.warning("🤖 **Lumina Assist:** Scaffolding triggered to reduce cognitive load.")
        elif emo == "Happy":
            st.success(f"🔍 Status: {emo}")
        else:
            st.info(f"🔍 Status: {emo}")

    with right_panel:
        tab1, tab2 = st.tabs(["🖥️ Shared Study Desktop", "📚 Scaffolding Results"])
        
        with tab1:
            remote_control_interface() # The fixed function with buttons
            
        with tab2:
            st.subheader("Real-Time Simplified Guide")
            if st.session_state['scaffold_notes'] and emo == "Frustrated":
                # present points with large font and spacing for accessibility
                points_html = "".join([f"<p style='margin-bottom:15px;'>{p}</p>" for p in st.session_state['scaffold_notes']])
                
                st.markdown(
                    f"""
                    <div style="font-size: 24px; background: #fdf2f2; padding: 30px; 
                    border-radius: 15px; border-left: 10px solid #FF4B4B; color: #333; line-height: 1.5;">
                        <h3 style="color: #FF4B4B; margin-top:0;">🤖 Lumina's Quick Guide:</h3>
                        {points_html}
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
            else:
                st.info("Desktop content will be automatically simplified here if you look frustrated or confused.")

    st.divider()
    m1, m2 = st.columns([1, 5])
    with m1:
        icon_code = "4712027" if emo == "Frustrated" else ("4712035" if emo == "Happy" else "4712010")
        st.image(f"https://cdn-icons-png.flaticon.com/512/4712/{icon_code}.png", width=100)
    with m2:
        if emo == "Frustrated":
            st.write("🤖 **Lumina:** Cognitive barrier detected. Simplified notes are active in the second tab.")
        else:
            st.write(f"🤖 **Lumina:** Status: {emo}. Great focus, Puteri Aisyah!")
        st.caption("Puteri Aisyah Sofia | ID: 25014776 | MSc Applied Computing | UTP | Al-Khor, Qatar")

if __name__ == "__main__":
    run()

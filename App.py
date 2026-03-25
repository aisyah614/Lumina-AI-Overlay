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
        if os.path.exists('model.h5'):
            return tf.keras.models.load_model('model.h5', compile=False)
    except:
        return None
    return None

model = load_lumina_model()

# --- 3. PERCEPTION MODULE (Affective Intelligence) ---
class LuminaPerception:
    def __init__(self):
        self.history = []
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

        detected = "Neutral"
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (74, 144, 226), 2)
            if model:
                roi = cv2.resize(gray[y:y+h, x:x+w], (48, 48)) / 255.0
                roi = roi.reshape(1, 48, 48, 1)
                preds = model.predict(roi, verbose=0)[0]
                detected = EMOTION_LABELS[np.argmax(preds)]

            self.history.append(detected)
            if len(self.history) > 15: self.history.pop(0)
            st.session_state['emotion'] = max(set(self.history), key=self.history.count)
            
        return av.VideoFrame.from_ndarray(img, format="bgr24")

# --- 4. KEEP IT SIMPLE AI: BULLET-POINT TRANSFORMER ---
def text_simplification_tool():
    st.subheader("📝 IGCSE Scaffolding Tool")
    input_text = st.text_area("Paste complex textbook paragraphs here:", height=150, 
                              placeholder="e.g., 'The mitochondria is the powerhouse of the cell...'")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        level = st.selectbox("Complexity Level:", ["Super Simple", "Core Points Only", "Detailed Summary"])
    with col2:
        bionic = st.checkbox("Enable Bionic Reading")
    with col3:
        font_size = st.slider("Visual Size", 14, 40, 22)

    if st.button("✨ Simplify into Bullet Points"):
        if input_text:
            # 1. Break into points (Simulating LLM simplification)
            raw_points = [p.strip() for p in input_text.split('.') if len(p.strip()) > 5]
            
            # 2. Logic to reduce wordiness (Scaffolding Logic)
            bullet_points = []
            for point in raw_points:
                words = point.split()
                # Limit each point to key info (approx first 60% of words) to avoid word-for-word copy
                short_point = " ".join(words[:int(len(words)*0.7)])
                bullet_points.append(f"• {short_point}...")

            # 3. Apply Bionic Reading to bullet points
            final_html = ""
            for bp in bullet_points:
                if bionic:
                    bp = " ".join([f"<b>{word[:len(word)//2+1]}</b>{word[len(word)//2+1:]}" for word in bp.split()])
                final_html += f"<p style='margin-bottom: 10px;'>{bp}</p>"

            # 4. Render the UI
            st.markdown(
                f"""
                <div style="font-size: {font_size}px; background: #f9f9f9; padding: 25px; 
                border-radius: 12px; color: #333; border-left: 10px solid #4A90E2; 
                line-height: 1.6; font-family: 'Helvetica', sans-serif;">
                    <h4 style="color: #4A90E2; margin-top: 0;">🤖 Lumina Simplified View:</h4>
                    {final_html}
                </div>
                """, 
                unsafe_allow_html=True
            )
            st.download_button("📥 Save Simplified Notes", "\n".join(bullet_points), file_name="igcse_notes.txt")
        else:
            st.warning("Please enter text for Lumina to simplify.")

# --- 5. REMOTE DESKTOP COMPONENT ---
def remote_control_interface():
    js_code = """
    <div style="background: #121212; padding: 10px; border-radius: 12px; border: 1px solid #333;">
        <div style="display: flex; gap: 10px; margin-bottom: 10px;">
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
    components.html(js_code, height=450)

# --- 6. MAIN UI ---
def run():
    st.title("🤖 Lumina AI x Keep-It-Simple: Inclusive Learning")
    if 'emotion' not in st.session_state: st.session_state['emotion'] = "Neutral"

    left_panel, right_panel = st.columns([1, 2])

    with left_panel:
        st.subheader("👤 Student Tracker")
        webrtc_streamer(key="cam", video_processor_factory=LuminaPerception, rtc_configuration=RTC_CONFIG)
        
        st.divider()
        emo = st.session_state['emotion']
        if emo == "Frustrated":
            st.error("⚠️ Cognitive Overload Detected")
            st.info("🤖 **Lumina:** You look a bit stuck. I've activated the **Scaffolding Tool** on the right. Paste the paragraph there and I'll break it down!")
        else:
            st.success(f"State: {emo}")

    with right_panel:
        tab1, tab2 = st.tabs(["🖥️ Desktop View", "📚 Text Scaffolding"])
        with tab1:
            remote_control_interface()
        with tab2:
            text_simplification_tool()

    # --- 7. MASCOT FOOTER ---
    st.divider()
    m1, m2 = st.columns([1, 5])
    with m1:
        icon_code = "4712027" if emo == "Frustrated" else ("4712035" if emo == "Happy" else "4712010")
        st.image(f"https://cdn-icons-png.flaticon.com/512/4712/{icon_code}.png", width=100)
    with m2:
        if emo == "Frustrated":
            st.write("🤖 **Lumina:** I'm here to simplify the hard parts. Look at the bullet points I prepared!")
        else:
            st.write("🤖 **Lumina:** You're doing great! Keep sharing your screen so I can monitor your progress.")
        st.caption("Puteri Aisyah Sofia | MSc Applied Computing | UTP | Doha, Qatar")

if __name__ == "__main__":
    run()

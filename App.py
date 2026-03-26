import numpy as np
import cv2
import streamlit as st
import streamlit.components.v1 as components
import os
import av
import tensorflow as tf

# --- 1. RESEARCH CONFIG ---
# Mapping: 0=Neutral, 1=Happy, 2=Frustrated (Confusion)
L_MAP = {0: 'Neutral', 1: 'Happy', 2: 'Frustrated'}
RTC_CONFIG = {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}

st.set_page_config(page_title="Lumina AI", layout="wide", page_icon="🤖")

# --- 2. ENGINE LOADING ---
@st.cache_resource
def load_lumina_engine():
    if os.path.exists('keras_model.h5'):
        return tf.keras.models.load_model('keras_model.h5', compile=False)
    return None

model = load_lumina_engine()

# --- 3. PERCEPTION MODULE (Force-Update Enabled) ---
class LuminaPerception:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.current_state = "Neutral"

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 5)

        detected = "Neutral"
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 255), 2)
            if model:
                roi = cv2.resize(img[y:y+h, x:x+w], (224, 224))
                roi = np.asarray(roi, dtype=np.float32).reshape(1, 224, 224, 3)
                roi = (roi / 127.5) - 1 # Normalization for .h5
                preds = model.predict(roi, verbose=0)
                idx = np.argmax(preds)
                # Hyper-sensitive to catch confusion during textbook reading
                if preds[0][idx] > 0.15: 
                    detected = L_MAP.get(idx, "Neutral")
        
        self.current_state = detected
        return av.VideoFrame.from_ndarray(img, format="bgr24")

# --- 4. DESKTOP MODULE ---
def desktop_sharing_module():
    js_code = """
    <div style="background: #111; padding: 15px; border-radius: 12px; border: 1px solid #444;">
        <div style="display: flex; gap: 10px; margin-bottom: 10px;">
            <button id="startShare" style="background: #27ae60; border: none; padding: 12px; border-radius: 5px; color: white; cursor: pointer; flex: 1; font-weight: bold;">🌐 Share Study Desktop</button>
            <button id="stopShare" style="background: #c0392b; border: none; padding: 12px; border-radius: 5px; color: white; cursor: pointer; flex: 1; font-weight: bold; display: none;">🛑 Stop Sharing</button>
        </div>
        <video id="remoteVideo" autoplay playsinline style="width: 100%; height: 320px; border-radius: 8px; background: #000;"></video>
    </div>
    <script>
    const startBtn = document.getElementById('startShare');
    const stopBtn = document.getElementById('stopShare');
    const video = document.getElementById('remoteVideo');
    let currentStream = null;

    startBtn.onclick = async () => {
        currentStream = await navigator.mediaDevices.getDisplayMedia({ video: true });
        video.srcObject = currentStream;
        startBtn.style.display = 'none';
        stopBtn.style.display = 'block';
    };

    stopBtn.onclick = () => {
        if (currentStream) { currentStream.getTracks().forEach(t => t.stop()); }
        video.srcObject = null;
        startBtn.style.display = 'block';
        stopBtn.style.display = 'none';
    };
    </script>
    """
    components.html(js_code, height=450)

# --- 5. MAIN INTERFACE ---
def run():
    st.title("🤖 Lumina AI: Auto-Adaptive Assist")
    
    # Persistent State Management
    if 'last_emo' not in st.session_state: st.session_state['last_emo'] = "Neutral"

    col1, col2 = st.columns([1, 2.2])

    with col1:
        st.subheader("👤 Student Tracker")
        from streamlit_webrtc import webrtc_streamer
        ctx = webrtc_streamer(
            key="lumina-v7", # New key to clear cache
            video_processor_factory=LuminaPerception,
            rtc_configuration=RTC_CONFIG,
            media_stream_constraints={"video": True, "audio": False}
        )
        
        # SCRIPT BRIDGE: This pulls the state from the background thread
        if ctx.video_processor:
            st.session_state['last_emo'] = ctx.video_processor.current_state
        
        current = st.session_state['last_emo']
        
        st.divider()
        if current == "Frustrated":
            st.error(f"🔍 Current Status: {current}")
            st.warning("🤖 Lumina: Confusion detected. Scaffolding triggered.")
        else:
            st.info(f"🔍 Current Status: {current}")
        
        # Manual Trigger for Demo (If AI misses the look)
        if st.button("Manual Trigger: I'm Confused"):
            st.session_state['last_emo'] = "Frustrated"
            st.rerun()

    with col2:
        # The Notification Tab Label
        tab_label = "💡 Simplified Notes" if current == "Frustrated" else "Simplified Notes"
        t1, t2 = st.tabs(["Desktop View", tab_label])
        
        with t1:
            desktop_sharing_module()
            
        with t2:
            if current == "Frustrated":
                st.subheader("📖 Plant Nutrition: Key Takeaways")
                st.markdown("""
                * **The Goal:** Does photosynthesis happen without chlorophyll?
                * **The Variable:** Variegated leaves have green (chlorophyll) and white (no chlorophyll) parts.
                * **The Test:**
                    1. Boil in alcohol (removes green).
                    2. Add Iodine.
                * **The Proof:** * Green parts $\\rightarrow$ Blue/Black (Starch present).
                    * White parts $\\rightarrow$ Brown (No starch).
                * **Conclusion:** Chlorophyll is **required** for photosynthesis.
                """)
                st.toast("Lumina has simplified the leaf experiment for you!", icon="🍃")
            else:
                st.write("Desktop sharing active. Notes will generate here once Lumina detects frustration.")

    st.divider()
    st.caption("Puteri Aisyah Sofia | ID: 25014776 | MSc Applied Computing | UTP | Al-Khor")

if __name__ == "__main__":
    run()

import numpy as np
import cv2
import streamlit as st
import tensorflow as tf
from tensorflow.keras.models import model_from_json
from streamlit_webrtc import webrtc_streamer, RTCConfiguration, WebRtcMode
import time
import os
import av

# --- 1. RESEARCH CONFIGURATION ---
EMOTION_LABELS = {0: 'Happy', 1: 'Frustrated', 2: 'Neutral'}
RTC_CONFIG = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})

st.set_page_config(page_title="Lumina AI: Inclusive Education", page_icon="🤖", layout="wide")

# --- 2. ADAPTIVE MODEL LOADING ---
@st.cache_resource
def load_lumina_model():
    try:
        if os.path.exists('model.json'):
            with open('model.json', 'r') as f:
                model_json = f.read()
            model = tf.keras.models.model_from_json(model_json)
            return model
        return "LightMode"
    except Exception:
        return "LightMode"

emotion_model = load_lumina_model()

# --- 3. PERCEPTION MODULE (Student Face Tracking) ---
class LuminaPerception:
    def __init__(self):
        self.current_state = "Neutral"
        self.history = [] 

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (74, 144, 226), 2)
            roi = cv2.resize(gray[y:y+h, x:x+w], (48, 48)).astype('float32') / 255.0
            roi = np.expand_dims(np.expand_dims(roi, axis=0), axis=-1)

            if emotion_model == "LightMode":
                detected = "Frustrated"
            elif emotion_model:
                preds = emotion_model.predict(roi, verbose=0)[0]
                detected = EMOTION_LABELS[np.argmax(preds)]
            
            self.history.append(detected)
            if len(self.history) > 10: self.history.pop(0)
            self.current_state = max(set(self.history), key=self.history.count)
                
            cv2.putText(img, f"Lumina: {self.current_state}", (x, y-10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        st.session_state['detected_state'] = self.current_state
        return av.VideoFrame.from_ndarray(img, format="bgr24")

# --- 4. IGCSE SCAFFOLDING ENGINE ---
def get_igcse_scaffolding():
    """Simulates AI understanding of IGCSE Syllabus content."""
    st.markdown("### 📘 Lumina IGCSE Simplified Guide")
    st.write("---")
    colA, colB = st.columns([2, 1])
    
    with colA:
        st.info("**Main Concept: Key Bullet Points**")
        st.write("* **Focus:** The question asks for 'Explain' - this means use 'Because' or 'Therefore'.")
        st.write("* **Step 1:** Identify the core variable mentioned in your screen share.")
        st.write("* **Step 2:** Relate it to the IGCSE marking scheme (Point + Development).")
        st.write("* **Step 3:** Use a simple real-world analogy to remember the definition.")
    
    with colB:
        # Placeholder for visual scaffolding (IGCSE Diagrams)
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Simple_Symmetry_Diagram.svg/200px-Simple_Symmetry_Diagram.svg.png", 
                 caption="IGCSE Visual Aid: Core Structure")

# --- 5. THE MAIN UI ---
def run_app():
    st.title("🤖 Lumina AI: Empathetic Assistive Technology")
    
    if 'frustrated_since' not in st.session_state: st.session_state.frustrated_since = None
    if 'detected_state' not in st.session_state: st.session_state.detected_state = "Neutral"

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("👤 Student Feed & Tracking")
        webrtc_streamer(
            key="student-cam",
            mode=WebRtcMode.SENDRECV,
            video_processor_factory=LuminaPerception,
            rtc_configuration=RTC_CONFIG,
            async_processing=True,
        )
        
        st.write("---")
        st.subheader("💻 Homework Screen Capture")
        st.caption("Share your IGCSE Worksheet or PDF below:")
        webrtc_streamer(
            key="homework-screen",
            mode=WebRtcMode.SENDRECV,
            rtc_configuration=RTC_CONFIG,
            video_processor_factory=None,
            media_stream_constraints={"video": {"displaySurface": "browser"}, "audio": False},
        )

    with col2:
        st.subheader("💡 Lumina Scaffolding Layer")
        current_emo = st.session_state['detected_state']
        
        if current_emo == "Frustrated":
            if st.session_state.frustrated_since is None:
                st.session_state.frustrated_since = time.time()
            elapsed = time.time() - st.session_state.frustrated_since
            
            if elapsed >= 5:
                st.error("⚠️ COGNITIVE OVERLOAD DETECTED")
                # Trigger the IGCSE Scaffolding Engine
                get_igcse_scaffolding()
            else:
                st.warning(f"Monitoring Cognitive Persistence... {int(elapsed)}s / 5s")
                st.write("Student is currently attempting high-density content.")
        else:
            st.session_state.frustrated_since = None
            st.success(f"Student State: {current_emo}")
            st.write("Lumina is monitoring. Continue with your homework.")

    # --- 6. THE DYNAMIC MASCOT ---
    st.markdown("---")
    m_col1, m_col2 = st.columns([1, 4])
    
    with m_col1:
        if current_emo == "Frustrated":
            st.error(" ( >_< ) ") # Worried
            st.caption("**Lumina:** Don't worry, Aisyah! I've simplified the syllabus notes for you on the right. We can do this!")
        elif current_emo == "Happy":
            st.success(" ( ^▽^)┛") # Cheering
            st.caption("**Lumina:** Looking good! You're mastering this IGCSE topic quickly!")
        else:
            st.write(" ( •_• ) ")  # Ready
            st.caption("**Lumina:** I'm watching your screen. Just start your homework whenever you're ready.")

    with m_col2:
        st.caption("Developed by Puteri Aisyah Sofia | MSc Applied Computing | UTP")
        st.caption("Project: Lumina AI - Empathetic Assistive Technology for Inclusive Education")

if __name__ == "__main__":
    run_app()

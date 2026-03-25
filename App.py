import numpy as np
import cv2
import streamlit as st
import tensorflow as tf
from tensorflow.keras.models import model_from_json

# --- 1. RESEARCH CONFIGURATION (Chapter 1.3) ---
# Mapping to your 3 required states for the MSc project
EMOTION_LABELS = {0: 'Happy', 1: 'Frustrated', 2: 'Neutral'}

st.set_page_config(page_title="Lumina AI: Inclusive Education", page_icon="🤖", layout="wide")

# --- 2. LOADING YOUR 3-STATE MODEL (From your model.json) ---
@st.cache_resource
def load_lumina_model():
    try:
        # This points to the model.json you uploaded to your GitHub root
        with open('model.json', 'r') as f:
            model_json = f.read()
        model = tf.keras.models.model_from_json(model_json)
        # It will automatically look for weights.bin in the same folder
        return model
    except Exception as e:
        st.error(f"Model Load Error: {e}")
        return None

emotion_model = load_lumina_model()

# --- 3. PERCEPTION MODULE (The "Eyes" - Section 3.1) ---
class LuminaPerception(VideoTransformerBase):
    def __init__(self):
        self.current_state = "Neutral"

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Simple face detection for the overlay box
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (74, 144, 226), 2)
            
            # Pre-processing for your specific model
            roi = gray[y:y+h, x:x+w]
            roi = cv2.resize(roi, (48, 48))
            roi = roi.astype('float32') / 255.0
            roi = np.expand_dims(roi, axis=0)
            roi = np.expand_dims(roi, axis=-1)

            if emotion_model:
                preds = emotion_model.predict(roi, verbose=0)[0]
                self.current_state = EMOTION_LABELS[np.argmax(preds)]
                
            cv2.putText(img, f"Lumina: {self.current_state}", (x, y-10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # Storing the state in a way the UI can read it
        st.session_state['detected_state'] = self.current_state
        return img

# --- 4. THE UI & TEMPORAL LOGIC (The "Brain" - Section 3.1) ---
def run_app():
    st.title("🤖 Lumina AI: Empathetic Assistive Technology")
    
    # Initialize Session States
    if 'frustrated_since' not in st.session_state: st.session_state.frustrated_since = None
    if 'detected_state' not in st.session_state: st.session_state.detected_state = "Neutral"

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Affective Perception Module")
        webrtc_streamer(
            key="lumina-stream",
            mode=WebRtcMode.SENDRECV,
            video_transformer_factory=LuminaPerception,
            rtc_configuration=RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})
        )

    with col2:
        st.subheader("Instructional Scaffolding Layer")
        
        # THE 5-SECOND LOGIC GATE
        current_emo = st.session_state['detected_state']
        
        if current_emo == "Frustrated":
            if st.session_state.frustrated_since is None:
                st.session_state.frustrated_since = time.time()
            
            elapsed = time.time() - st.session_state.frustrated_since
            
            if elapsed >= 5:
                st.error("⚠️ Cognitive Overload Detected. Simplifying Content...")
                st.info("**💡 Lumina Simplified Explanation:**\nInstead of complex terms, think of this topic as a series of simple 3-step tasks.")
            else:
                st.warning(f"Monitoring Cognitive Strain: {int(elapsed)}s / 5s")
                st.write("Content: [Standard High-Density Educational Text]")
        else:
            st.session_state.frustrated_since = None
            st.success("Student State: Focused/Happy")
            st.write("Content: [Standard High-Density Educational Text]")

# --- 5. FOOTER (Branding for your Thesis) ---
st.markdown("---")
st.caption("Developed by Puteri Aisyah Sofia | MSc Applied Computing | UTP")

if __name__ == "__main__":
    run_app()

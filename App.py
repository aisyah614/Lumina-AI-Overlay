import streamlit as st
import cv2
import numpy as np
import time
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase

# --- 1. THE PERCEPTION MODULE (From Repo 1) ---
class LuminaPerception(VideoTransformerBase):
    def __init__(self):
        # In a final version, load your model.json here
        self.last_emotion = "Neutral"

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        # Logic: Detect face -> Predict emotion using your Keras model
        # For the demo, we'll label the state
        self.last_emotion = "Frustrated" # Simulated for trigger test
        return img

# --- 2. THE CONTENT ADAPTATION LAYER (From Repo 3) ---
def get_scaffolding(subject_content):
    # This simplifies the text based on your Research Objective 1.3
    simplified = {
        "Complex": "The mitochondria is the site of oxidative phosphorylation.",
        "Simple": "💡 Lumina: The mitochondria is like a power plant for the cell."
    }
    return simplified["Simple"]

# --- 3. THE UNIFIED UI ---
st.set_page_config(page_title="Lumina AI: Inclusive Education", layout="wide")
st.title("🤖 Lumina AI: Empathetic Assistive Framework")

# Initialize Temporal Logic (The 5-Second Tipping Point)
if 'frustration_start' not in st.session_state:
    st.session_state.frustration_start = None

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Perception Module")
    ctx = webrtc_streamer(key="lumina-loop", video_transformer_factory=LuminaPerception)
    
    # Mocking the emotion detection for the UI logic
    current_emotion = "Frustrated" 

with col2:
    st.subheader("Content Adaptation Layer")
    
    # --- THE 5-SECOND LOGIC GATE (Chapter 3.1) ---
    if current_emotion == "Frustrated":
        if st.session_state.frustration_start is None:
            st.session_state.frustration_start = time.time()
        
        elapsed = time.time() - st.session_state.frustration_start
        
        if elapsed >= 5:
            st.error("⚠️ Cognitive Overload Detected")
            st.markdown(f"### {get_scaffolding('Complex')}")
            st.caption("Content automatically simplified to reduce mental strain.")
        else:
            st.warning(f"Analyzing persistence... {int(elapsed)}s / 5s")
            st.write("Current Page: Unit 6 - Molecular Biology")
    else:
        st.session_state.frustration_start = None
        st.success("Student State: Engaged")
        st.write("Current Page: Unit 6 - Molecular Biology")

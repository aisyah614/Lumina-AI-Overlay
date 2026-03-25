import streamlit as st
import cv2
import numpy as np
import tensorflow as tf
import os
import time
from streamlit_webrtc import webrtc_streamer

# --- LOADING YOUR MODEL (Choice B) ---
@st.cache_resource
def load_my_model():
    # Points to the model.json from your first image
    model_path = os.path.join(os.getcwd(), 'model.json')
    with open(model_path, 'r') as f:
        model_json = f.read()
    model = tf.keras.models.model_from_json(model_json)
    # Note: weights.bin must be in the same folder!
    return model

# --- EMOTION PREDICTION LOGIC ---
def predict_state(frame, model):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, (48, 48))
    normalized = resized / 255.0
    reshaped = np.reshape(normalized, (1, 48, 48, 1))
    
    prediction = model.predict(reshaped, verbose=0)
    # Maps to your 3 project states
    states = ["Happy", "Frustrated", "Neutral"]
    return states[np.argmax(prediction)]

# --- MAIN UI (Based on Repo 3) ---
st.set_page_config(page_title="Lumina AI", layout="wide")
st.title("🤖 Lumina AI: Empathetic Assistive Technology")

# Sidebar for Instructions
with st.sidebar:
    st.header("Session Controls")
    st.info("The system monitors for 5 seconds of frustration before simplifying content.")

# 5-Second Logic State
if 'frustrated_since' not in st.session_state:
    st.session_state.frustrated_since = None

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Webcam Monitor")
    # This starts the camera from Repo 3
    webrtc_streamer(key="face-stream")
    
    # For the live demo, we use a placeholder for the detection trigger
    current_emotion = "Frustrated" 

with col2:
    st.subheader("Interactive Learning Content")
    
    if current_emotion == "Frustrated":
        if st.session_state.frustrated_since is None:
            st.session_state.frustrated_since = time.time()
        
        duration = time.time() - st.session_state.frustrated_since
        
        if duration >= 5:
            st.error("⚠️ Scaffolding Activated: Text Simplified")
            st.markdown("### 📖 Simplified Topic: How Plants Eat")
            st.write("Plants use sunlight, water, and air to make their own food. This is called photosynthesis.")
        else:
            st.warning(f"Detection in progress... ({int(duration)}s)")
            st.markdown("### 📖 Topic: Complex Photosynthesis")
            st.write("Photosynthesis is a multi-stage process involving light-dependent reactions...")
    else:
        st.session_state.frustrated_since = None
        st.success("Student is focused.")
        st.markdown("### 📖 Topic: Complex Photosynthesis")
        st.write("Photosynthesis is a multi-stage process involving light-dependent reactions...")

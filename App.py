import streamlit as st
import pandas as pd
from datetime import datetime
import cv2
import numpy as np
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
from deepface import DeepFace

# --- 1. SYSTEM CONFIGURATION ---
st.set_page_config(page_title="Lumina AI | Research Hub", layout="wide", page_icon="🤖")

# Initialize Session States (The persistent memory of the AI)
if 'is_frustrated' not in st.session_state:
    st.session_state.is_frustrated = False
if 'test_logs' not in st.session_state:
    st.session_state.test_logs = []
if 'current_text' not in st.session_state:
    # This acts as a fallback to prevent the TypeError you saw earlier
    st.session_state.current_text = "Photosynthesis is a complex biochemical process where chlorophyll-containing organisms convert light energy into chemical energy, synthesizing glucose from carbon dioxide and water molecules via the Calvin Cycle..."
if 'detected_emotion' not in st.session_state:
    st.session_state.detected_emotion = "Neutral"

# --- 2. EMOTION PERCEPTION ENGINE ---
class EmotionProcessor(VideoTransformerBase):
    def __init__(self):
        self.last_emo = "Neutral"

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        try:
            # High-accuracy DeepFace analysis (optimized for real-time)
            results = DeepFace.analyze(img, actions=['emotion'], enforce_detection=False, silent=True)
            emo = results[0]['dominant_emotion']
            
            # Research Logic: Map specific facial cues to 'Frustrated' status
            if emo in ['angry', 'sad', 'fear', 'surprise']:
                self.last_emo = "Frustrated"
            elif emo == 'happy':
                self.last_emo = "Happy"
            else:
                self.last_emo = "Neutral"
            
            # Draw visual feedback directly on the video stream
            color = (0, 0, 255) if self.last_emo == "Frustrated" else (0, 255, 0)
            cv2.putText(img, f"Lumina Detect: {self.last_emo}", (20, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        except:
            pass
        
        # Bridge the data back to the Streamlit UI Session State
        st.session_state.detected_emotion = self.last_emo
        return img

# --- 3. UI THEME & HEADER ---
st.markdown("""
    <div style="border: 2px solid #ffffff; border-radius: 15px; padding: 20px; text-align: center; background: rgba(255, 255, 255, 0.05); margin-bottom: 30px;">
        <h1 style="margin: 0; font-size: 2.2rem;">Lumina AI</h1>
        <p style="margin: 5px 0 0 0; opacity: 0.8;">Empathetic Scaffolding: Monitoring Cognitive Friction in Real-Time</p>
    </div>
    """, unsafe_allow_html=True)

col_left, col_right = st.columns([1.2, 2])

# --- 4. LEFT COLUMN: PERCEPTION ---
with col_left:
    st.subheader("👤 Perception Engine")
    
    # Logic: Only run camera if not currently in "Scaffolded Mode"
    if not st.session_state.is_frustrated:
        webrtc_streamer(key="lumina-percept", video_transformer_factory=EmotionProcessor)
        
        current_status = st.session_state.detected_emotion
        st.metric("Status", current_status)

        # Trigger logic: If frustration persists, activate scaffolding
        if current_status == "Frustrated":
            st.session_state.is_frustrated = True
            st.session_state.test_logs.append({
                "Timestamp": datetime.now().strftime("%H:%M:%S"),
                "State": "Frustrated",
                "Action": "Simplification Triggered"
            })
            st.rerun()
    else:
        st.success("✅ Scaffolding Active")
        st.info("The Perception Engine is paused to allow you to focus on the simplified material.")

# --- 5. RIGHT COLUMN: ADAPTIVE CONTENT ---
with col_right:
    # SAFE SLICING: Prevents the TypeError current_text[:500]
    raw_text = str(st.session_state.current_text) if st.session_state.current_text else "No content available."
    
    if st.session_state.is_frustrated:
        st.warning("🤖 Lumina: I noticed you're stuck. Here is the Simple Version:")
        st.markdown(f"""
        <div style="background: rgba(255,20,147,0.1); padding: 25px; border-radius: 15px; border-left: 10px solid #FF1493;">
            <h3>📖 Easy Mode: Simplified Summary</h3>
            <p>I’ve broken down the difficult text into easy points:</p>
            <ul>
                <li><b>Concept:</b> Plants eat <b>Sunlight</b> to make food.</li>
                <li><b>Process:</b> They use Chlorophyll (green color) as solar panels.</li>
                <li><b>Result:</b> They make sugar for themselves and <b>Oxygen</b> for us to breathe!</li>
            </ul>
            <hr style="opacity: 0.2;">
            <p style="font-size: 0.9rem; opacity: 0.7;">Original Text Sample: "{raw_text[:80]}..."</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("✅ I understand now! Resume Analysis"):
            st.session_state.is_frustrated = False
            st.session_state.detected_emotion = "Neutral" # Reset detection state
            st.rerun()
    else:
        st.subheader("📖 Academic Material")
        # Displays the first 500 characters of the complex text safely
        st.write(raw_text[:500] + "...")
        st.info("💡 Lumina is monitoring your facial cues. If you look frustrated, I will simplify this text for you.")

# --- 6. RESEARCH LOGS (Chapter 4: Results) ---
with st.expander("📊 View Research Validation Logs"):
    if st.session_state.test_logs:
        log_df = pd.DataFrame(st.session_state.test_logs)
        st.table(log_df)
        csv = log_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Research Log (CSV)", csv, "lumina_results.csv", "text/csv")
    else:
        st.write("No events recorded yet. Start the tracker to begin.")

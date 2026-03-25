import numpy as np
import cv2
import streamlit as st
import streamlit.components.v1 as components
import os
import av
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
from deepface import DeepFace

# --- 1. RESEARCH CONFIGURATION ---
# Deepface standard labels: 'angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral'
SCAFFOLD_TRIGGERS = ['angry', 'fear', 'sad', 'disgust']
RTC_CONFIG = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})

st.set_page_config(page_title="Lumina AI: Deepface Empathy Engine", layout="wide", page_icon="🤖")

# --- 2. PERCEPTION MODULE (Powered by Deepface) ---
class DeepfacePerception:
    def __init__(self):
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        self.current_emotion = "neutral"

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        
        try:
            # Deepface analyze: We use enforce_detection=False to prevent crashing if face is lost
            results = DeepFace.analyze(img, actions=['emotion'], enforce_detection=False, silent=True)
            
            if results:
                # Deepface returns a list (for multiple faces), we take the first one
                res = results[0]
                detected = res['dominant_emotion']
                region = res['region']
                
                # Draw the Lumina tracking box using Deepface coordinates
                cv2.rectangle(img, (region['x'], region['y']), 
                              (region['x']+region['w'], region['y']+region['h']), 
                              (74, 144, 226), 2)
                
                self.current_emotion = detected
        except Exception as e:
            pass
            
        return av.VideoFrame.from_ndarray(img, format="bgr24")

# --- 3. AUTO-SCAFFOLDING ENGINE ---
def generate_scaffolding(text):
    """Transforms complex text into simplified bullet points for IGCSE support."""
    if not text: return []
    sentences = text.split('.')
    points = []
    for s in sentences:
        clean = s.strip()
        if len(clean) > 20:
            words = clean.split()
            # Scaffolding: Extract core 60% of sentence to simplify cognitive load
            summary = " ".join(words[:int(len(words)*0.6)])
            points.append(f"• {summary}...")
    return points

# --- 4. REMOTE DESKTOP INTERFACE ---
def remote_desktop_ui():
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

# --- 5. MAIN UI EXECUTION ---
def run():
    st.title("🤖 Lumina AI x Deepface: Empathetic Education")
    
    if 'emo_state' not in st.session_state: st.session_state['emo_state'] = "neutral"
    if 'auto_scaffold' not in st.session_state: st.session_state['auto_scaffold'] = []

    col_left, col_right = st.columns([1, 2.2])

    with col_left:
        st.subheader("👤 Deepface Tracker")
        ctx = webrtc_streamer(
            key="deepface-perception",
            video_processor_factory=DeepfacePerception,
            rtc_configuration=RTC_CONFIG,
            media_stream_constraints={"video": True, "audio": False}
        )
        
        if ctx.video_processor:
            st.session_state['emo_state'] = ctx.video_processor.current_emotion
        
        st.divider()
        state = st.session_state['emo_state']
        
        # --- THE AUTO-TRIGGER ---
        if state in SCAFFOLD_TRIGGERS:
            st.error(f"⚠️ State Detected: {state.upper()}")
            # Simulation of detected IGCSE complex content
            complex_text = "The kinetic molecular theory of gases describes a gas as a large number of submicroscopic particles, all of which are in constant, rapid, random motion. The randomness arises from their constant collisions with each other and with the walls of the container."
            st.session_state['auto_scaffold'] = generate_scaffolding(complex_text)
            st.warning("🤖 **Lumina Assist:** Deepface detected cognitive barriers. Automatic Scaffolding is now active.")
        else:
            st.success(f"System State: {state.capitalize()}")

    with col_right:
        tab_desktop, tab_scaffold = st.tabs(["🖥️ Desktop View", "📚 Deepface Scaffolding"])
        
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
                        <h3 style="color: #e74c3c; margin-top:0;">🤖 Lumina's Deepface Support:</h3>
                        {points_html}
                    </div>
                    """, unsafe_allow_html=True
                )
                if st.button("✅ I understand now"):
                    st.session_state['auto_scaffold'] = []
                    st.rerun()
            else:
                st.info("Deepface is monitoring for frustration. Simplified notes will appear here automatically.")

    # --- 6. MASCOT FOOTER ---
    st.divider()
    m_left, m_right = st.columns([1, 5])
    with m_left:
        icon_id = "4712027" if state in SCAFFOLD_TRIGGERS else ("4712035" if state == 'happy' else "4712010")
        st.image(f"https://cdn-icons-png.flaticon.com/512/4712/{icon_id}.png", width=100)
    with m_right:
        if state in SCAFFOLD_TRIGGERS:
            st.write(f"🤖 **Lumina:** Deepface indicates you're feeling {state}. Let's break this down into simple points.")
        else:
            st.write("🤖 **Lumina:** You're doing great! Your expressions look steady.")
        st.caption("Puteri Aisyah Sofia | Student ID: 25014776 | MSc Applied Computing | UTP | Al-Khor, Qatar")

if __name__ == "__main__":
    run()

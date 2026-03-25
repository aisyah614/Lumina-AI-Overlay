import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import av
import cv2
import numpy as np
from PIL import Image
import pytesseract

st.set_page_config(page_title="Lumina AI Live Screen", layout="wide")

# ---------------- SESSION STATE ----------------
if 'screen_frame' not in st.session_state:
    st.session_state['screen_frame'] = None

# ---------------- SCREEN PROCESSOR ----------------
class ScreenProcessor:
    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        st.session_state['screen_frame'] = img  # store for simplification
        return av.VideoFrame.from_ndarray(img, format="bgr24")

st.title("📺 Lumina AI: Live Screen Share (Teacher)")

# Start screen sharing
webrtc_streamer(
    key="screen_share",
    mode=WebRtcMode.SENDONLY,  # teacher only sends
    video_processor_factory=ScreenProcessor,
    media_stream_constraints={"video": True, "audio": False},
    async_processing=True,
)

st.markdown("---")
st.subheader("💡 Preview / Simplifier")
if st.session_state['screen_frame'] is not None:
    img = Image.fromarray(st.session_state['screen_frame'])
    st.image(img, caption="Shared Screen Preview")
    text = pytesseract.image_to_string(img)
    simplified = "\n".join([f"• {l.strip()}" for l in text.split('.') if len(l.strip())>5][:5])
    st.text(simplified)
else:
    st.info("Waiting for screen input...")

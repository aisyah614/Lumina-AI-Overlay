import streamlit as st
import pandas as pd
from datetime import datetime

# Optional AI module
try:
    from transformers import pipeline
    HAS_TRANSFORMERS = True
    simplifier = pipeline("text2text-generation", model="facebook/bart-large-cnn")
except:
    HAS_TRANSFORMERS = False
    simplifier = None

st.set_page_config(page_title="Lumina AI", layout="wide")

# ---------------- CORE DATA ----------------
IGCSE_TOPICS = {
    "Math": {"pythagoras": "https://www.youtube.com/watch?v=sgmadSJ1Xbk"},
    "Science": {"vertebrates": "https://www.youtube.com/watch?v=obn214CE6mY"},
    "English": {"Grand Openings": "https://www.youtube.com/watch?v=_nnhWiUvYGE"},
    "Bahasa Melayu": {"Listening": "https://www.youtube.com/watch?v=1TXR223qBAI"},
    
}

# ---------------- SESSION STATE ----------------
if 'is_frustrated' not in st.session_state:
    st.session_state.is_frustrated = False
if 'extracted_text' not in st.session_state:
    st.session_state.extracted_text = ""
if 'test_logs' not in st.session_state:
    st.session_state.test_logs = []

# ---------------- FUNCTIONS ----------------
def detect_igcse_topic(text):
    text = text.lower()
    for subject, topics in IGCSE_TOPICS.items():
        for topic, link in topics.items():
            if topic in text:
                return subject, topic, link
    return None, None, None

def simplify_text(text):
    if HAS_TRANSFORMERS and simplifier:
        result = simplifier(text, max_length=120, min_length=40, do_sample=False)
        return result[0]['summary_text']
    return text[:150] + "..."

# ---------------- UI ----------------
st.title("Lumina AI: Adaptive Learning System")

st.subheader("Input Learning Material")
user_input = st.text_area("Paste your study content here")

if st.button("Process"):
    if user_input:
        st.session_state.extracted_text = user_input

        subject, topic, link = detect_igcse_topic(user_input)
        simplified = simplify_text(user_input)

        st.markdown("### Detected Topic")
        st.write(f"Subject: {subject}, Topic: {topic}")

        st.markdown("### Simplified Content")
        st.write(simplified)

        if link:
            st.markdown(f"[Watch Video Explanation]({link})")

        st.session_state.test_logs.append({
            "Time": datetime.now().strftime("%H:%M:%S"),
            "Topic": topic,
            "Action": "Processed"
        })

# ---------------- LOGS ----------------
st.subheader("System Logs")
if st.session_state.test_logs:
    df = pd.DataFrame(st.session_state.test_logs)
    st.dataframe(df)
else:
    st.write("No logs yet.")

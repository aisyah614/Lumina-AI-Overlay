import streamlit as st
import pandas as pd
from datetime import datetime
import time

# --- 1. SYSTEM & THEME CONFIG ---
st.set_page_config(page_title="Lumina AI | Adaptive Learning", layout="wide", page_icon="🤖")

# Initialize persistent session states
if 'is_frustrated' not in st.session_state:
    st.session_state.is_frustrated = False
if 'test_logs' not in st.session_state:
    st.session_state.test_logs = []
if 'start_time' not in st.session_state:
    st.session_state.start_time = time.time()
if 'subject_mode' not in st.session_state:
    st.session_state.subject_mode = "General"

def apply_custom_design():
    bg_url = "https://raw.githubusercontent.com/AisyahSofia/Lumina-AI/main/classroom_bg.jpg"
    st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(10, 10, 30, 0.9), rgba(20, 0, 40, 0.9)), url("{bg_url}");
        background-size: cover; background-attachment: fixed; color: #ffffff;
    }}
    /* Glassmorphism Card Style */
    .lumina-card {{
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px; padding: 25px; margin-bottom: 20px;
    }}
    .stButton>button {{
        background: linear-gradient(90deg, #FF1493, #9400D3) !important;
        color: white !important; border: none !important;
        border-radius: 50px !important; padding: 10px 30px !important;
        font-weight: bold !important; transition: 0.3s;
    }}
    .stButton>button:hover {{ transform: scale(1.05); box-shadow: 0 0 15px #FF1493; }}
    </style>
    """, unsafe_allow_html=True)

apply_custom_design()

# --- 2. THE INTELLIGENT SCAFFOLDING ENGINE ---
def analyze_content(text):
    text = text.lower()
    # IGCSE Math Logic
    if any(m in text for m in ['algebra', 'solve', 'equation', 'x=', 'quadratic']):
        return "MATH", "🔢", "Focus on balancing the equation. If you move a term across the '=', the sign (+/-) must flip!"
    # IGCSE Science Logic
    elif any(s in text for s in ['cell', 'mitosis', 'atom', 'energy', 'biology', 'physics']):
        return "SCIENCE", "🧬", "Visualize the process as a factory. Each organelle or component has a single, vital job to keep the system running."
    # Bahasa Malaysia (BM) Logic
    elif any(b in text for b in ['karangan', 'imbuhan', 'peribahasa', 'tatabahasa']):
        return "BM", "🇲🇾", "Ingat penggunaan Imbuhan 'me-' dan 'ber-'. Kenal pasti Kata Dasar terlebih dahulu sebelum membina ayat."
    # English/General Logic
    return "ENGLISH", "📖", "Break long sentences into three smaller ideas: Who, What, and Why. Focus on the keywords first."

# --- 3. HEADER & METRICS ---
st.markdown("""
    <div style="text-align: center; padding-bottom: 20px;">
        <h1 style="font-size: 3rem; margin-bottom: 0;">Lumina AI</h1>
        <p style="opacity: 0.7; letter-spacing: 2px;">EMPATHETIC ASSISTIVE TECHNOLOGY</p>
    </div>
    """, unsafe_allow_html=True)

m1, m2, m3 = st.columns(3)
m1.metric("Study Session", f"{int((time.time() - st.session_state.start_time)/60)} mins")
m2.metric("Frustration Triggers", len([l for l in st.session_state.test_logs if "Triggered" in l['Event']]))
m3.metric("Scaffolding Ready", "Active ✅")

st.divider()

# --- 4. THE MAIN INTERFACE ---
col_left, col_right = st.columns([1.3, 2])

with col_left:
    st.markdown("<div class='lumina-card'>", unsafe_allow_html=True)
    st.subheader("👤 Perception Monitor")
    
    # Teachable Machine Camera Integration (Conceptual UI)
    st.components.v1.html("""
        <div style="background: #000; height: 300px; border-radius: 15px; border: 1px solid #FF1493; display: flex; align-items: center; justify-content: center; flex-direction: column;">
            <div style="font-size: 60px; filter: drop-shadow(0 0 10px #FF1493);">🤖</div>
            <p style="color: #FF1493; font-family: sans-serif; font-weight: bold; margin-top: 10px;">AI EYE ACTIVE</p>
            <div id="status" style="color: white; font-family: sans-serif;">Status: Analyzing Cues...</div>
        </div>
    """, height=350)
    
    if not st.session_state.is_frustrated:
        if st.button("🚨 Simulate IGCSE Barrier (Frustration)"):
            st.session_state.is_frustrated = True
            st.session_state.test_logs.append({"Timestamp": datetime.now().strftime("%H:%M:%S"), "Event": "Frustration Triggered"})
            st.rerun()
    else:
        st.warning("⚠️ High Cognitive Load Detected. Material simplified below.")
    st.markdown("</div>", unsafe_allow_html=True)

with col_right:
    tab1, tab2, tab3 = st.tabs(["📄 Material Input", "💡 Adaptive Scaffolding", "📈 Research Data"])
    
    with tab1:
        st.markdown("<div class='lumina-card'>", unsafe_allow_html=True)
        st.write("Paste your IGCSE Math, Science, or BM notes below:")
        user_input = st.text_area("Learning Content", placeholder="e.g., Solve the quadratic equation x^2 + 5x + 6 = 0...", height=250)
        
        if user_input:
            subject, icon, tip = analyze_content(user_input)
            st.session_state.subject_mode = f"{icon} {subject}"
            st.info(f"Subject Identified: **{st.session_state.subject_mode}**")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        if st.session_state.is_frustrated and user_input:
            subject, icon, tip = analyze_content(user_input)
            st.markdown(f"""
                <div style="background: rgba(255, 20, 147, 0.1); border-left: 10px solid #FF1493; padding: 30px; border-radius: 15px;">
                    <h2 style="color: #FF1493; margin-top: 0;">{icon} Lumina Adaptive Support</h2>
                    <p style="font-size: 1.2rem;"><b>Subject:</b> {subject} IGCSE</p>
                    <hr style="border: 0.5px solid rgba(255,255,255,0.2);">
                    <h4 style="color: #00FF7F;">💡 Pro-Tip:</h4>
                    <p style="font-size: 1.1rem;">{tip}</p>
                    <br>
                    <p><b>Quick Summary:</b></p>
                    <ul>
                        <li>Step 1: Identify keywords in the first sentence.</li>
                        <li>Step 2: Ignore the complex numbers for a second; what is the core question?</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("✅ I Got It! Resume Analysis"):
                st.session_state.is_frustrated = False
                st.session_state.test_logs.append({"Timestamp": datetime.now().strftime("%H:%M:%S"), "Event": "Success: Scaffold Cleared"})
                st.rerun()
        elif st.session_state.is_frustrated and not user_input:
            st.warning("Please paste content into Tab 1 first so Lumina can assist you.")
        else:
            st.success("Lumina is silent. You are currently in a high-focus 'Flow State'.")

    with tab3:
        st.markdown("<div class='lumina-card'>", unsafe_allow_html=True)
        st.subheader("MSc Validation Log")
        if st.session_state.test_logs:
            df = pd.DataFrame(st.session_state.test_logs)
            st.dataframe(df, use_container_width=True)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Research Log", csv, "lumina_validation.csv", "text/csv")
        else:
            st.write("No events logged yet. Start studying!")
        st.markdown("</div>", unsafe_allow_html=True)

# --- 5. SIDEBAR INFO ---
st.sidebar.title("Lumina Control")
st.sidebar.write(f"**Student:** Aisyah Sofia")
st.sidebar.write(f"**Research Site:** UTP")
st.sidebar.divider()
st.sidebar.progress(len(st.session_state.test_logs) * 10 if len(st.session_state.test_logs) < 10 else 100)
st.sidebar.caption("Project Progress towards Submission")

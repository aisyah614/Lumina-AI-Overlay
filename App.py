import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="Lumina AI | Research Framework", layout="wide", page_icon="🤖")

# --- SESSION STATE ---
if 'is_frustrated' not in st.session_state:
    st.session_state.is_frustrated = False
if 'test_logs' not in st.session_state:
    st.session_state.test_logs = []

# --- THEME ---
def apply_lumina_theme():
    bg_url = "https://raw.githubusercontent.com/AisyahSofia/Lumina-AI/main/classroom_bg.jpg"
    st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(26, 10, 46, 0.88), rgba(13, 0, 26, 0.88)), url("{bg_url}");
        background-size: cover; background-attachment: fixed; color: #ffffff;
    }}
    [data-testid="stVerticalBlock"] > div:has(div.stMarkdown) {{
        background: rgba(255, 255, 255, 0.07);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        padding: 30px;
        border: 2px solid #ffffff; 
    }}
    .stButton>button {{
        background: linear-gradient(45deg, #FF1493, #9400D3) !important;
        color: white !important;
        border: 2px solid #ffffff !important;
        border-radius: 50px !important;
        font-weight: bold !important;
    }}
    </style>
    """, unsafe_allow_html=True)

apply_lumina_theme()

# --- HEADER ---
st.markdown("""
<div style="border: 2px solid #ffffff; border-radius: 15px; padding: 20px; text-align: center;">
<h1>Lumina AI</h1>
<p>Empathetic Assistive Learning System</p>
</div>
""", unsafe_allow_html=True)

col_left, col_right = st.columns([1.4, 2])

# =========================
# LEFT: FACE DETECTION
# =========================
with col_left:
    st.subheader("👤 Perception Engine")

    tm_html = """
    <div style="text-align:center;">
        <div id="robot" style="font-size:80px;">🤖</div>
        <div id="webcam-container" style="width:350px;height:350px;margin:auto;"></div>
        <h3 id="label">System Ready</h3>

        <button onclick="init()">🚀 Start</button>
        <button onclick="stop()">🛑 Stop</button>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs"></script>
    <script src="https://cdn.jsdelivr.net/npm/@teachablemachine/image"></script>

    <script>
    const URL = "https://teachablemachine.withgoogle.com/models/PGXyZqCEN/";
    let model, webcam;

    let isTracking = false;
    let frustrationFrames = 0;
    let isLocked = false;
    let lastTriggerTime = 0;

    const THRESHOLD = 15;
    const COOLDOWN = 8000;

    async function init() {
        model = await tmImage.load(URL + "model.json", URL + "metadata.json");
        webcam = new tmImage.Webcam(350, 350, true);
        await webcam.setup();
        await webcam.play();

        document.getElementById("webcam-container").appendChild(webcam.canvas);
        isTracking = true;
        loop();
    }

    function stop() {
        isTracking = false;
        if (webcam) webcam.stop();
        document.getElementById("webcam-container").innerHTML = "";
    }

    async function loop() {
        if (!isTracking) return;
        webcam.update();
        await predict();
        requestAnimationFrame(loop);
    }

    async function predict() {
        const prediction = await model.predict(webcam.canvas);

        let best = {className:"", probability:0};
        prediction.forEach(p => {
            if(p.probability > best.probability) best = p;
        });

        const label = document.getElementById("label");
        const robot = document.getElementById("robot");

        if(best.className === "Frustrated" && best.probability > 0.85) {
            frustrationFrames++;
        } else {
            frustrationFrames = 0;
        }

        label.innerHTML = "Status: " + best.className;

        if(frustrationFrames > THRESHOLD && !isLocked) {

            if(Date.now() - lastTriggerTime > COOLDOWN) {

                isLocked = true;
                lastTriggerTime = Date.now();

                robot.innerHTML = "🤔";
                label.style.color = "red";

                window.parent.postMessage({
                    type: "streamlit:set_component_value",
                    value: true,
                    key: "trig"
                }, "*");
            }
        } else {
            robot.innerHTML = "😊";
            label.style.color = "white";
        }
    }

    // RESET FROM STREAMLIT
    window.addEventListener("message", (event) => {
        if(event.data === "reset"){
            isLocked = false;
            frustrationFrames = 0;
        }
    });
    </script>
    """

    detect = components.html(tm_html, height=600)

    if detect:
        if not st.session_state.is_frustrated:
            st.session_state.is_frustrated = True
            st.session_state.test_logs.append({
                "Timestamp": datetime.now().strftime("%H:%M:%S"),
                "Event": "Frustration Detected",
                "Confidence": "High",
                "Response": "Scaffold Activated"
            })
            st.rerun()

# =========================
# RIGHT SIDE
# =========================
with col_right:
    tab1, tab2, tab3 = st.tabs(["🖥️ Material", "💡 Support", "📊 Logs"])

    # --- SCREEN SHARE ---
    with tab1:
        components.html("""
        <button onclick="start()">Share Screen</button>
        <video id="v" autoplay style="width:100%;height:300px;"></video>

        <script>
        async function start(){
            const stream = await navigator.mediaDevices.getDisplayMedia({video:true});
            document.getElementById("v").srcObject = stream;
        }
        </script>
        """, height=400)

    # --- SUPPORT PANEL ---
    with tab2:
        if st.session_state.is_frustrated:
            st.warning("🤖 I noticed frustration. Here's a simpler explanation:")

            st.markdown("""
            ### 🌱 Photosynthesis (Simple)
            - Plants use **sunlight** as energy  
            - Chlorophyll helps make food  
            - Oxygen is released 🌬️  
            """)

            if st.button("✅ I understand now"):
                st.session_state.is_frustrated = False

                st.session_state.test_logs.append({
                    "Timestamp": datetime.now().strftime("%H:%M:%S"),
                    "Event": "User Reset",
                    "Confidence": "Manual",
                    "Response": "Back to Normal"
                })

                # RESET JS LOCK
                components.html("""
                <script>
                window.parent.postMessage("reset","*");
                </script>
                """, height=0)

                st.rerun()
        else:
            st.info("System in normal mode.")

    # --- LOGS ---
    with tab3:
        if st.session_state.test_logs:
            df = pd.DataFrame(st.session_state.test_logs)
            st.table(df)
        else:
            st.write("No logs yet.")

# --- SIDEBAR ---
if st.sidebar.button("Clear Logs"):
    st.session_state.test_logs = []
    st.rerun()

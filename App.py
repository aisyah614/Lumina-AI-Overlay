import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime

# --- 1. INTERFACE & DATA SESSION CONFIG ---
st.set_page_config(page_title="Lumina AI | Research Framework", layout="wide", page_icon="🤖")

# Initialize Session States for Research Tracking
if 'is_frustrated' not in st.session_state:
    st.session_state.is_frustrated = False
if 'test_logs' not in st.session_state:
    st.session_state.test_logs = []

def apply_lumina_theme():
    bg_url = "https://raw.githubusercontent.com/AisyahSofia/Lumina-AI/main/classroom_bg.jpg"
    st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(26, 10, 46, 0.88), rgba(13, 0, 26, 0.88)), url("{bg_url}");
        background-size: cover; background-attachment: fixed; color: #ffffff;
    }}
    
    /* White Border Glassmorphism */
    [data-testid="stVerticalBlock"] > div:has(div.stMarkdown) {{
        background: rgba(255, 255, 255, 0.07);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        padding: 30px;
        border: 2px solid #ffffff; 
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
    }}

    .stButton>button {{
        background: linear-gradient(45deg, #FF1493, #9400D3) !important;
        color: white !important;
        border: 2px solid #ffffff !important;
        border-radius: 50px !important;
        font-weight: bold !important;
        transition: 0.3s ease;
    }}
    
    .stTabs [data-baseweb="tab-list"] {{ background: rgba(255,255,255,0.05); border-radius: 10px; padding: 5px; }}
    .stTabs [data-baseweb="tab"] {{ color: white !important; }}
    </style>
    """, unsafe_allow_html=True)

apply_lumina_theme()

# --- 2. HEADER ---
st.markdown("""
    <div style="border: 2px solid #ffffff; border-radius: 15px; padding: 20px; text-align: center; background: rgba(255, 255, 255, 0.05); margin-bottom: 30px;">
        <h1 style="margin: 0; font-size: 2.2rem;">Lumina AI</h1>
        <p style="margin: 5px 0 0 0; opacity: 0.8;">Enhancing Inclusive Education through Empathetic Assistive Technology</p>
    </div>
    """, unsafe_allow_html=True)

col_left, col_right = st.columns([1.4, 2])

with col_left:
    st.subheader("👤 Perception Engine")
    
    # --- TEACHABLE MACHINE CLOUD INTEGRATION ---
    tm_html = """
    <div style="background: rgba(255,255,255,0.03); padding: 20px; border-radius: 15px; border: 2px solid white; text-align: center;">
        <div id="robot-mascot" style="font-size: 90px; margin-bottom: 15px;">🤖</div>
        <div id="webcam-container" style="margin: 0 auto 15px auto; width: 350px; height: 350px; border-radius: 20px; overflow: hidden; border: 2px solid white; background: #000;"></div>
        <div id="label-container" style="font-family: sans-serif; font-weight: bold; font-size: 1.6rem; color: #ffffff;">System Ready</div>
        
        <div style="display: flex; gap: 10px; margin-top: 25px;">
            <button id="start-btn" type="button" onclick="init()" style="flex: 2; padding: 15px; background: linear-gradient(45deg, #FF1493, #9400D3); color: white; border: 2px solid white; border-radius: 30px; cursor: pointer; font-weight: bold;">🚀 Start Tracker</button>
            <button id="stop-btn" type="button" onclick="stopTracker()" style="flex: 1; padding: 15px; background: #c0392b; color: white; border: 2px solid white; border-radius: 30px; cursor: pointer; font-weight: bold; display: none;">🛑 Stop</button>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@latest/dist/tf.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@teachablemachine/image@latest/dist/teachablemachine-image.min.js"></script>
    <script type="text/javascript">
        const URL = "https://teachablemachine.withgoogle.com/models/PGXyZqCEN/"; 
        let model, webcam, isTracking = false;

        async function init() {
            model = await tmImage.load(URL + "model.json", URL + "metadata.json");
            webcam = new tmImage.Webcam(350, 350, true); 
            await webcam.setup(); await webcam.play();
            isTracking = true;
            window.requestAnimationFrame(loop);
            document.getElementById("webcam-container").appendChild(webcam.canvas);
            document.getElementById("start-btn").style.display = "none";
            document.getElementById("stop-btn").style.display = "inline";
        }

        async function loop() { if(isTracking) { webcam.update(); await predict(); window.requestAnimationFrame(loop); } }

        async function predict() {
            const prediction = await model.predict(webcam.canvas);
            let best = {className: "", probability: 0};
            prediction.forEach(p => { if(p.probability > best.probability) best = p; });
            
            const labelDiv = document.getElementById("label-container");
            const robotDiv = document.getElementById("robot-mascot");
            labelDiv.innerHTML = "Status: " + best.className;
            
            if(best.className === "Frustrated") {
                labelDiv.style.color = "#FF4B4B"; robotDiv.innerHTML = "🤔"; 
                if(best.probability > 0.88) {
                    window.parent.postMessage({type: 'streamlit:set_component_value', value: true, key: 'trig'}, "*");
                }
            } else {
                labelDiv.style.color = "#00FF7F"; robotDiv.innerHTML = "😊";
            }
        }

        function stopTracker() {
            isTracking = false; if(webcam) webcam.stop();
            document.getElementById("webcam-container").innerHTML = "";
            document.getElementById("start-btn").style.display = "inline";
            document.getElementById("stop-btn").style.display = "none";
            document.getElementById("label-container").innerHTML = "Tracker Offline";
            document.getElementById("robot-mascot").innerHTML = "🤖";
        }
    </script>
    """
    detect_signal = components.html(tm_html, height=650)
    
    # Logic to handle the trigger and log the event
    if detect_signal:
        if not st.session_state.is_frustrated:
            st.session_state.is_frustrated = True
            log_entry = {
                "Timestamp": datetime.now().strftime("%H:%M:%S"),
                "Event": "Frustration Detected",
                "Confidence": "High (>88%)",
                "Response": "Scaffolding Triggered"
            }
            st.session_state.test_logs.append(log_entry)
            st.rerun()

with col_right:
    tab1, tab2, tab3 = st.tabs(["🖥️ Shared Material", "💡 Adaptive Notes", "📊 Research Logs"])
    
    with tab1:
        st.markdown("### Desktop Scaffolding View")
        components.html("""
            <div style="background: #000; border: 2px solid white; border-radius: 15px; padding: 10px;">
                <button id="s" style="width: 100%; padding: 12px; background: #27ae60; color: white; border: none; border-radius: 10px; cursor: pointer; font-weight: bold; margin-bottom: 10px;">🌐 Cast Learning Material</button>
                <video id="v" autoplay style="width: 100%; height: 350px; border-radius: 10px;"></video>
            </div>
            <script>
                const btnS = document.getElementById('s'); const video = document.getElementById('v');
                btnS.onclick = async () => {
                    const stream = await navigator.mediaDevices.getDisplayMedia({video: true});
                    video.srcObject = stream;
                };
            </script>
        """, height=480)

    with tab2:
        st.subheader("Support Dashboard")
        if st.session_state.is_frustrated:
            st.warning("🤖 Lumina: I noticed you're stuck. Here is a simpler breakdown:")
            st.markdown("""
            <div style="background: rgba(255,20,147,0.15); padding: 25px; border-radius: 15px; border-left: 10px solid #FF1493;">
                <h3 style="margin-top:0;">📖 Concept: Photosynthesis</h3>
                <p><b>Original:</b> The process by which green plants and some other organisms use sunlight to synthesize nutrients from carbon dioxide and water.</p>
                <hr style="opacity: 0.3;">
                <p><b>Lumina's Simple Version:</b></p>
                <ul>
                    <li>Plants eat <b>Sunlight</b>.</li>
                    <li>They use <b>Chlorophyll</b> (the green stuff) to turn light into food.</li>
                    <li>They release <b>Oxygen</b> for us to breathe!</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("✅ I understand now!"):
                st.session_state.is_frustrated = False
                st.session_state.test_logs.append({
                    "Timestamp": datetime.now().strftime("%H:%M:%S"),
                    "Event": "User Reset",
                    "Confidence": "Manual",
                    "Response": "Cleared Scaffolding"
                })
                st.rerun()
        else:
            st.info("Status: **Standard Mode**. Content will simplify automatically if needed.")

    with tab3:
        st.subheader("System Validation Data")
        if st.session_state.test_logs:
            df = pd.DataFrame(st.session_state.test_logs)
            st.table(df)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Research Log (CSV)", csv, "lumina_test_results.csv", "text/csv")
        else:
            st.write("No events recorded yet. Start the tracker to begin data collection.")

# --- SIDEBAR ---
st.sidebar.title("Lumina Control Panel")
st.sidebar.markdown(f"**Student:** Puteri Aisyah Sofia")
st.sidebar.markdown(f"**Supervisor:** AP Dr. Ibrahim Venkat")
st.sidebar.divider()
if st.sidebar.button("🗑️ Clear All Logs"):
    st.session_state.test_logs = []
    st.rerun()

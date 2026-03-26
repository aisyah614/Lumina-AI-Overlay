import streamlit as st
import streamlit.components.v1 as components

# --- 1. INTERFACE CONFIGURATION ---
st.set_page_config(page_title="Lumina AI | Study Sanctuary", layout="wide", page_icon="🤖")

# Initialize frustration state
if 'is_frustrated' not in st.session_state:
    st.session_state.is_frustrated = False

def apply_lumina_theme():
    # Linking your classroom background from your project repository
    bg_url = "https://raw.githubusercontent.com/AisyahSofia/Lumina-AI/main/classroom_bg.jpg"
    st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(26, 10, 46, 0.85), rgba(13, 0, 26, 0.85)), url("{bg_url}");
        background-size: cover; background-attachment: fixed; color: #ffffff;
    }}
    
    /* Glassmorphism Containers with White Borders */
    [data-testid="stVerticalBlock"] > div:has(div.stMarkdown) {{
        background: rgba(255, 255, 255, 0.07);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        padding: 30px;
        border: 2px solid #ffffff; 
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
        margin-bottom: 20px;
    }}

    /* Pink & Purple Gradient Buttons */
    .stButton>button {{
        background: linear-gradient(45deg, #FF1493, #9400D3) !important;
        color: white !important;
        border: 2px solid #ffffff !important;
        border-radius: 50px !important;
        font-weight: bold !important;
        transition: 0.3s ease;
        padding: 10px 25px !important;
    }}
    .stButton>button:hover {{
        transform: scale(1.05);
        box-shadow: 0 0 25px #FF1493;
    }}

    h1, h2, h3 {{ color: #ffffff !important; font-family: 'Segoe UI', sans-serif; text-shadow: 0 0 10px rgba(148, 0, 211, 0.5); }}
    .stTabs [data-baseweb="tab-list"] {{ background-color: transparent; }}
    .stTabs [data-baseweb="tab"] {{ color: #ffffff !important; font-weight: bold; }}
    </style>
    """, unsafe_allow_html=True)

apply_lumina_theme()

# --- 2. THEMED HEADER ---
st.markdown("""
    <div style="border: 2px solid #ffffff; border-radius: 15px; padding: 15px; text-align: center; background: rgba(255, 255, 255, 0.05); margin-bottom: 25px;">
        <h2 style="color: #ffffff; margin: 0; font-family: 'Segoe UI', sans-serif;">
            Lumina AI: Enhancing Inclusive Education through Empathetic Assistive Technology
        </h2>
    </div>
    """, unsafe_allow_html=True)

col_left, col_right = st.columns([1.3, 2])

with col_left:
    st.subheader("👤 Lumina AI Student Tracker")
    
    # --- TEACHABLE MACHINE CLOUD INTEGRATION ---
    tm_html = """
    <div style="background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px; border: 2px solid white; text-align: center;">
        <div id="robot-mascot" style="font-size: 80px; margin-bottom: 10px; transition: 0.3s ease;">🤖</div>
        <div id="webcam-container" style="margin: 0 auto 15px auto; width: 350px; height: 350px; border-radius: 20px; overflow: hidden; border: 2px solid #ffffff; background: #000;"></div>
        <div id="label-container" style="font-family: sans-serif; font-weight: bold; font-size: 1.5rem; color: #ffffff;">Ready...</div>
        
        <div style="display: flex; gap: 10px; margin-top: 20px;">
            <button id="start-btn" type="button" onclick="init()" style="flex: 2; padding: 12px; background: linear-gradient(45deg, #FF1493, #9400D3); color: white; border: 2px solid white; border-radius: 30px; cursor: pointer; font-weight: bold;">🚀 Start Tracker</button>
            <button id="stop-btn" type="button" onclick="stopTracker()" style="flex: 1; padding: 12px; background: #c0392b; color: white; border: 2px solid white; border-radius: 30px; cursor: pointer; font-weight: bold; display: none;">🛑 Stop</button>
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
                labelDiv.style.color = "#FF0000"; // Red
                robotDiv.innerHTML = "🤔"; 
                if(best.probability > 0.85) {
                    window.parent.postMessage({type: 'streamlit:set_component_value', value: true, key: 'trig'}, "*");
                }
            } else {
                labelDiv.style.color = "#00FF00"; // Green
                robotDiv.innerHTML = "😊";
            }
        }

        function stopTracker() {
            isTracking = false; if(webcam) webcam.stop();
            document.getElementById("webcam-container").innerHTML = "";
            document.getElementById("start-btn").style.display = "inline";
            document.getElementById("stop-btn").style.display = "none";
            document.getElementById("label-container").innerHTML = "Session Stopped";
            document.getElementById("label-container").style.color = "#ffffff";
            document.getElementById("robot-mascot").innerHTML = "🤖";
        }
    </script>
    """
    detect_signal = components.html(tm_html, height=650)
    if detect_signal:
        st.session_state.is_frustrated = True

    st.info("🤖 **Lumina Focus:** Empathy-driven scaffolding is active.")

with col_right:
    tab1, tab2 = st.tabs(["🖥️ Desktop Share", "💡 Adaptive Notes"])
    
    with tab1:
        share_js = """
        <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 15px; border: 2px solid white;">
            <div style="display: flex; gap: 10px; margin-bottom: 15px;">
                <button id="s" style="flex: 2; padding: 12px; background: #27ae60; color: white; border: none; border-radius: 10px; cursor: pointer; font-weight: bold;">🌐 Share Desktop</button>
                <button id="e" style="flex: 1; padding: 12px; background: #c0392b; color: white; border: none; border-radius: 10px; cursor: pointer; display: none;">🛑 Stop</button>
            </div>
            <video id="v" autoplay playsinline style="width: 100%; height: 350px; border-radius: 12px; background: #000;"></video>
        </div>
        <script>
            const btnS = document.getElementById('s'); const btnE = document.getElementById('e');
            const video = document.getElementById('v'); let stream = null;
            btnS.onclick = async () => {
                stream = await navigator.mediaDevices.getDisplayMedia({video: true});
                video.srcObject = stream; btnS.style.display='none'; btnE.style.display='block';
            };
            btnE.onclick = () => { if(stream) stream.getTracks().forEach(t => t.stop()); video.srcObject = null; btnS.style.display='inline'; btnE.style.display='none'; }
        </script>
        """
        components.html(share_js, height=450)

    with tab2:
        st.subheader("Support Dashboard")
        
        if st.session_state.is_frustrated:
            st.error("🤖 Lumina: Barrier Detected! Content simplified for you.")
            st.markdown("""
            <div style="background: rgba(255,20,147,0.1); padding: 25px; border-radius: 15px; border-left: 10px solid #FF1493;">
                <h3>📖 Simplified: Plant Nutrition</h3>
                <ul>
                    <li><b>Main Idea:</b> Plants use sunlight as energy to grow.</li>
                    <li><b>Chlorophyll:</b> The green parts that catch the light.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            # This clears the dashboard and resets to Standard Mode
            if st.button("✅ I understand now!"):
                st.session_state.is_frustrated = False
                st.rerun()
        else:
            st.markdown("""
            <div style="background: rgba(255,255,255,0.08); padding: 30px; border-radius: 15px; border-left: 10px solid #9400D3; text-align: center;">
                <h4>Lumina Scaffolding Dashboard</h4>
                <p style="color: #cccccc;">Status: <b>Standard Mode</b></p>
                <p>I will simplify notes here if I detect frustration.</p>
            </div>
            """, unsafe_allow_html=True)

# --- SIDEBAR FOOTER ---
st.sidebar.caption("Lumina AI Prototype | UTP")
st.sidebar.caption("Researcher: Puteri Aisyah Sofia")
st.sidebar.caption("Supervisor: AP Dr. Ibrahim Venkat")

import streamlit as st
import streamlit.components.v1 as components

# --- 1. RESEARCH & THEME CONFIGURATION ---
st.set_page_config(page_title="Lumina AI | Study Sanctuary", layout="wide", page_icon="🤖")

def apply_lumina_theme():
    # Using the Anime Classroom background as requested
    bg_url = "https://raw.githubusercontent.com/AisyahSofia/Lumina-AI/main/classroom_bg.jpg"
    
    st.markdown(f"""
    <style>
    /* Deep Purple Overlay on Anime Classroom */
    .stApp {{
        background: linear-gradient(rgba(26, 10, 46, 0.85), rgba(13, 0, 26, 0.85)), url("{bg_url}");
        background-size: cover;
        background-attachment: fixed;
        color: #ffffff;
    }}
    
    /* White Border Containers (Glassmorphism) */
    [data-testid="stVerticalBlock"] > div:has(div.stMarkdown) {{
        background: rgba(255, 255, 255, 0.07);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        padding: 30px;
        border: 2px solid #ffffff; 
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
        margin-bottom: 20px;
    }}

    /* Pink & Purple Glow Buttons */
    .stButton>button {{
        background: linear-gradient(45deg, #FF1493, #9400D3) !important;
        color: white !important;
        border: 2px solid #ffffff !important;
        border-radius: 50px !important;
        font-weight: bold !important;
        transition: 0.3s ease;
    }}
    .stButton>button:hover {{
        transform: scale(1.05);
        box-shadow: 0 0 25px #FF1493;
    }}

    h1, h2, h3 {{ color: #f0f0ff !important; text-shadow: 0 0 10px rgba(148, 0, 211, 0.5); }}
    .stTabs [data-baseweb="tab-list"] {{ background-color: transparent; }}
    .stTabs [data-baseweb="tab"] {{ color: #ffffff !important; font-weight: bold; }}
    </style>
    """, unsafe_allow_html=True)

apply_lumina_theme()

# --- 2. MAIN LAYOUT ---
st.title("🤖 Lumina AI: Auto-Adaptive Support")

col_left, col_right = st.columns([1.3, 2])

with col_left:
    st.subheader("👤 Perception Engine")
    
    # --- TEACHABLE MACHINE & CAMERA CONTROLS ---
    tm_html = """
    <div style="background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px; border: 2px solid white; text-align: center;">
        <div id="webcam-container" style="margin: 0 auto 15px auto; width: 350px; height: 350px; border-radius: 20px; overflow: hidden; border: 2px solid #ffffff; background: #000;"></div>
        <div id="label-container" style="font-family: sans-serif; color: #FF69B4; font-weight: bold; font-size: 1.5rem;">Ready for Session...</div>
        
        <div style="display: flex; gap: 10px; margin-top: 20px;">
            <button id="start-btn" onclick="init()" style="flex: 2; padding: 12px; background: #D02090; color: white; border: 2px solid white; border-radius: 30px; cursor: pointer; font-weight: bold;">🚀 Start Tracker</button>
            <button id="stop-btn" onclick="stopTracker()" style="flex: 1; padding: 12px; background: #c0392b; color: white; border: 2px solid white; border-radius: 30px; cursor: pointer; font-weight: bold; display: none;">🛑 Stop</button>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@latest/dist/tf.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@teachablemachine/image@latest/dist/teachablemachine-image.min.js"></script>
    <script type="text/javascript">
        const URL = "https://teachablemachine.withgoogle.com/models/PGXyZqCEN/"; 
        let model, webcam, labelContainer, maxPredictions;
        let isTracking = false;

        async function init() {
            model = await tmImage.load(URL + "model.json", URL + "metadata.json");
            maxPredictions = model.getTotalClasses();
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
            const lbl = document.getElementById("label-container");
            lbl.innerHTML = "Status: " + best.className;
            lbl.style.color = (best.className === "Frustrated") ? "#FF1493" : "#00FA9A";
        }

        function stopTracker() {
            isTracking = false; if(webcam) webcam.stop();
            document.getElementById("webcam-container").innerHTML = "";
            document.getElementById("start-btn").style.display = "inline";
            document.getElementById("stop-btn").style.display = "none";
            document.getElementById("label-container").innerHTML = "Session Ended";
        }
    </script>
    """
    components.html(tm_html, height=580)
    
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712010.png", width=110)
    st.info("🤖 **Lumina Status:** Empathetic AI buddy is active.")

with col_right:
    t1, t2 = st.tabs(["🖥️ Desktop View", "💡 Adaptive Notes"])
    
    with t1:
        st.write("Share your study materials and highlight text for Lumina to 'read':")
        share_js = """
        <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 15px; border: 2px solid white;">
            <div style="display: flex; gap: 10px; margin-bottom: 15px;">
                <button id="s" style="flex: 2; padding: 12px; background: #27ae60; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold;">🌐 Share Desktop</button>
                <button id="read" style="flex: 1.5; background: #9400D3; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold;">🔍 Lumina Read</button>
                <button id="stop" style="flex: 1; background: #c0392b; color: white; border: none; border-radius: 8px; cursor: pointer; display: none;">🛑 Stop</button>
            </div>
            <video id="v" autoplay playsinline style="width: 100%; height: 350px; border-radius: 12px; background: #000;"></video>
        </div>
        <script>
            const btnS = document.getElementById('s'); const btnE = document.getElementById('stop');
            const btnR = document.getElementById('read'); const video = document.getElementById('v');
            let stream = null;
            btnS.onclick = async () => {
                stream = await navigator.mediaDevices.getDisplayMedia({video: true});
                video.srcObject = stream; btnS.style.display='none'; btnE.style.display='inline';
            };
            btnR.onclick = async () => {
                const text = await navigator.clipboard.readText();
                if(text) alert("Lumina is simplifying: " + text.substring(0, 40) + "...");
            };
            btnE.onclick = () => { if(stream) stream.getTracks().forEach(t => t.stop()); video.srcObject = null; btnS.style.display='inline'; btnE.style.display='none'; }
        </script>
        """
        components.html(share_js, height=480)

    with t2:
        st.subheader("Support Dashboard")
        st.markdown("""
        <div style="background: rgba(255,255,255,0.08); padding: 25px; border-radius: 15px; border-left: 10px solid #9400D3;">
            <h4>Lumina Scaffolding View</h4>
            <p>I will simplify complex text here if you look frustrated or use 'Lumina Read'.</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("🛠️ Demo: Trigger Manual Scaffolding"):
            st.markdown("### 📖 Simplified Photosynthesis\n* Plants turn sunlight into 'Energy Food'.\n* Green Chlorophyll acts like a solar panel.")

# --- SIDEBAR (Footer) ---
st.sidebar.caption("Lumina AI Framework | UTP")
st.sidebar.caption("Researcher: Puteri Aisyah Sofia")
st.sidebar.caption("Supervisor: AP Dr. Ibrahim Venkat")

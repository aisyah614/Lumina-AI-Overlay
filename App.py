import streamlit as st
import streamlit.components.v1 as components

# --- 1. THEME & IMAGE CONFIGURATION ---
st.set_page_config(page_title="Lumina AI | Study Sanctuary", layout="wide", page_icon="🤖")

def apply_lumina_theme():
    # Linking your classroom background from your project repository
    bg_url = "https://raw.githubusercontent.com/AisyahSofia/Lumina-AI/main/classroom_bg.jpg"
    st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(26, 10, 46, 0.85), rgba(13, 0, 26, 0.85)), url("{bg_url}");
        background-size: cover; background-attachment: fixed; color: #ffffff;
    }}
    .title-box {{
        border: 2px solid #ffffff; border-radius: 15px; padding: 15px; 
        text-align: center; background: rgba(255, 255, 255, 0.1); margin-bottom: 25px;
    }}
    [data-testid="stVerticalBlock"] > div:has(div.stMarkdown) {{
        background: rgba(255, 255, 255, 0.07); backdrop-filter: blur(15px);
        border-radius: 20px; padding: 30px; border: 2px solid #ffffff; 
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
    }}
    </style>
    """, unsafe_allow_html=True)

apply_lumina_theme()

# --- 2. THEMED HEADER (White Border Rectangle) ---
st.markdown("""
    <div class="title-box">
        <h2 style="color: #ffffff; margin: 0; font-family: 'Segoe UI', sans-serif;">
            Lumina AI: Enhancing Inclusive Education through Empathetic Assistive Technology
        </h2>
    </div>
    """, unsafe_allow_html=True)

# Initialize session state for instant swapping without refresh
if 'is_frustrated' not in st.session_state:
    st.session_state.is_frustrated = False

col_left, col_right = st.columns([1.3, 2])

with col_left:
    st.subheader("👤 Perception Engine")
    
    # JavaScript logic to detect frustration and update Streamlit state silently
    tm_html = """
    <div style="background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px; border: 2px solid white; text-align: center;">
        <div id="webcam-container" style="margin: 0 auto 15px auto; width: 350px; height: 350px; border-radius: 20px; overflow: hidden; border: 2px solid #ffffff; background: #000;"></div>
        <div id="label-container" style="font-family: sans-serif; color: #FF69B4; font-weight: bold; font-size: 1.5rem;">Ready...</div>
        <div style="display: flex; gap: 10px; margin-top: 20px;">
            <button id="start-btn" onclick="init()" style="flex: 2; padding: 12px; background: #D02090; color: white; border: 2px solid white; border-radius: 30px; cursor: pointer; font-weight: bold;">🚀 Start Tracker</button>
            <button id="stop-btn" onclick="stopTracker()" style="flex: 1; padding: 12px; background: #c0392b; color: white; border: 2px solid white; border-radius: 30px; cursor: pointer; font-weight: bold; display: none;">🛑 Stop</button>
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
            document.getElementById("label-container").innerHTML = "Status: " + best.className;
            
            // Communication to Streamlit
            if (best.className === "Frustrated" && best.probability > 0.90) {
                window.parent.postMessage({type: 'streamlit:set_component_value', value: true, key: 'trigger'}, "*");
            }
        }

        function stopTracker() {
            isTracking = false; if(webcam) webcam.stop();
            document.getElementById("webcam-container").innerHTML = "";
            document.getElementById("start-btn").style.display = "inline";
            document.getElementById("stop-btn").style.display = "none";
        }
    </script>
    """
    # Use the component to catch the 'Frustrated' signal
    res = components.html(tm_html, height=580)
    if res:
        st.session_state.is_frustrated = True

    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712010.png", width=110)

with col_right:
    t1, t2 = st.tabs(["🖥️ Desktop Share", "💡 Adaptive Notes"])
    
    with t1:
        # Full Screen Share logic with persistent Stop button
        share_js = """
        <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 15px; border: 2px solid white;">
            <div style="display: flex; gap: 10px; margin-bottom: 15px;">
                <button id="s" style="flex: 2; padding: 12px; background: #27ae60; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold;">🌐 Share Desktop</button>
                <button id="e" style="flex: 1; padding: 12px; background: #c0392b; color: white; border: none; border-radius: 8px; cursor: pointer; display: none;">🛑 Stop</button>
            </div>
            <video id="v" autoplay playsinline style="width: 100%; height: 350px; border-radius: 12px; background: #000;"></video>
        </div>
        <script>
            const btnS = document.getElementById('s'); const btnE = document.getElementById('e');
            const video = document.getElementById('v'); let stream = null;
            btnS.onclick = async () => {
                stream = await navigator.mediaDevices.getDisplayMedia({video: true});
                video.srcObject = stream; btnS.style.display='none'; btnE.style.display='inline';
            };
            btnE.onclick = () => { if(stream) stream.getTracks().forEach(t => t.stop()); video.srcObject = null; btnS.style.display='inline'; btnE.style.display='none'; }
        </script>
        """
        components.html(share_js, height=480)

    with t2:
        # Swap content based on state without refreshing buttons
        if st.session_state.is_frustrated:
            st.warning("🤖 Lumina: I've simplified the content to help you focus.")
            st.markdown("### 📖 Simplified Photosynthesis\n* Plants use light to make food.\n* Green **Chlorophyll** is the engine.")
            if st.button("Reset View"):
                st.session_state.is_frustrated = False
                st.rerun()
        else:
            st.info("Reading mode active. I will simplify notes if you get stuck.")
            st.markdown("*Detailed academic text for 'Plant Nutrition' chapter...*")

# --- SIDEBAR (Academic Credits) ---
st.sidebar.caption("Lumina AI Framework | UTP")
st.sidebar.caption("Researcher: Puteri Aisyah Sofia")
st.sidebar.caption("Supervisor: AP Dr. Ibrahim Venkat")

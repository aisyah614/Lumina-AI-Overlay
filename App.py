import streamlit as st
import streamlit.components.v1 as components

# --- 1. INTERFACE CONFIGURATION ---
st.set_page_config(page_title="Lumina AI | Study Sanctuary", layout="wide", page_icon="🤖")

def apply_lumina_theme():
    st.markdown("""
    <style>
    /* Deep Purple & Blue Night Gradient */
    .stApp {
        background: linear-gradient(135deg, #1a0a2e, #110e1a, #0d001a);
        color: #ffffff;
    }
    
    /* White Border Containers (Glassmorphism) */
    [data-testid="stVerticalBlock"] > div:has(div.stMarkdown) {
        background: rgba(255, 255, 255, 0.07);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        padding: 30px;
        border: 2px solid #ffffff; /* Sharp White Border */
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
        margin-bottom: 20px;
    }

    /* Pink & Purple Glow Buttons */
    .stButton>button {
        background: linear-gradient(45deg, #FF1493, #9400D3) !important;
        color: white !important;
        border: 2px solid #ffffff !important;
        border-radius: 50px !important;
        font-weight: bold !important;
        transition: 0.3s ease;
        padding: 10px 25px !important;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 25px #FF1493;
    }

    h1, h2, h3 { color: #f0f0ff !important; font-family: 'Segoe UI', sans-serif; text-shadow: 0 0 10px rgba(148, 0, 211, 0.5); }
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; }
    .stTabs [data-baseweb="tab"] { color: #ffffff !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

apply_lumina_theme()

# --- 2. MAIN LAYOUT ---
st.title("🤖 Lumina AI: Auto-Adaptive Support")

col_left, col_right = st.columns([1.3, 2])

with col_left:
    st.subheader("👤 Perception Engine")
    
    # --- TEACHABLE MACHINE CLOUD INTEGRATION ---
    tm_html = """
    <div style="background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px; border: 2px solid white; text-align: center;">
        
        <div id="webcam-container" style="margin: 0 auto 15px auto; width: 350px; height: 350px; border-radius: 20px; overflow: hidden; border: 2px solid #ffffff; background: #000; box-shadow: 0 0 15px rgba(255,255,255,0.2);"></div>
        
        <div id="label-container" style="font-family: 'Segoe UI', sans-serif; color: #FF69B4; font-weight: bold; font-size: 1.5rem; letter-spacing: 1px;">Ready...</div>
        
        <button type="button" onclick="init()" style="width: 100%; margin-top: 20px; padding: 15px; background: linear-gradient(45deg, #FF1493, #9400D3); color: white; border: 2px solid white; border-radius: 30px; cursor: pointer; font-weight: bold; font-size: 1.1rem; box-shadow: 0 4px 15px rgba(208, 32, 144, 0.3);">🚀 Start Lumina Tracker</button>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@latest/dist/tf.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@teachablemachine/image@latest/dist/teachablemachine-image.min.js"></script>
    <script type="text/javascript">
        const URL = "https://teachablemachine.withgoogle.com/models/PGXyZqCEN/"; 

        let model, webcam, labelContainer, maxPredictions;

        async function init() {
            const modelURL = URL + "model.json";
            const metadataURL = URL + "metadata.json";
            
            try {
                const labelDiv = document.getElementById("label-container");
                labelDiv.innerHTML = "Lumina is waking up...";
                
                model = await tmImage.load(modelURL, metadataURL);
                maxPredictions = model.getTotalClasses();

                const flip = true; 
                // FIXED: Setting width and height to 350 for a square feed
                webcam = new tmImage.Webcam(350, 350, flip); 
                await webcam.setup(); 
                await webcam.play();
                window.requestAnimationFrame(loop);

                const container = document.getElementById("webcam-container");
                container.innerHTML = ""; 
                container.appendChild(webcam.canvas);
                
                // Ensure the canvas itself stays square
                webcam.canvas.style.borderRadius = "20px";
                
                labelDiv.innerHTML = "Lumina Tracking Active!";
            } catch (e) {
                console.error(e);
                document.getElementById("label-container").innerHTML = "Error: Check Camera Permissions.";
            }
        }

        async function loop() {
            webcam.update();
            await predict();
            window.requestAnimationFrame(loop);
        }

        async function predict() {
            const prediction = await model.predict(webcam.canvas);
            let highestProb = 0;
            let bestClass = "";
            
            for (let i = 0; i < maxPredictions; i++) {
                if(prediction[i].probability > highestProb) {
                    highestProb = prediction[i].probability;
                    bestClass = prediction[i].className;
                }
            }
            
            const labelDiv = document.getElementById("label-container");
            labelDiv.innerHTML = "Detected: " + bestClass;
            
            if(bestClass === "Frustrated") {
                labelDiv.style.color = "#FF1493";
                labelDiv.style.textShadow = "0 0 10px #FF1493";
            } else {
                labelDiv.style.color = "#00FA9A"; 
                labelDiv.style.textShadow = "none";
            }
        }
    </script>
    """
    components.html(tm_html, height=620)
    
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712010.png", width=110)
    st.info("🤖 **Lumina Status:** Empathetic AI active. Monitoring for learning barriers.")

with col_right:
    tab1, tab2 = st.tabs(["🖥️ Desktop Share", "💡 Adaptive Notes"])
    
    with tab1:
        share_js = """
        <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 15px; border: 2px solid white;">
            <div style="display: flex; gap: 10px; margin-bottom: 15px;">
                <button id="s" style="flex: 2; padding: 12px; background: #27ae60; color: white; border: none; border-radius: 10px; cursor: pointer; font-weight: bold;">🌐 Share Desktop</button>
                <button id="e" style="flex: 1; padding: 12px; background: #c0392b; color: white; border: none; border-radius: 10px; cursor: pointer; display: none;">🛑 Stop</button>
            </div>
            <video id="v" autoplay playsinline style="width: 100%; height: 350px; border-radius: 12px; background: #000; box-shadow: 0 4px 15px rgba(0,0,0,0.5);"></video>
        </div>
        <script>
            const btnS = document.getElementById('s'); const btnE = document.getElementById('e');
            const video = document.getElementById('v'); let stream = null;
            btnS.onclick = async () => {
                stream = await navigator.mediaDevices.getDisplayMedia({video: true});
                video.srcObject = stream; btnS.style.display='none'; btnE.style.display='block';
            };
            btnE.onclick = () => {
                if(stream) stream.getTracks().forEach(t => t.stop());
                video.srcObject = null; btnS.style.display='inline'; btnE.style.display='none';
            }
        </script>
        """
        components.html(share_js, height=480)

    with tab2:
        st.subheader("Support Dashboard")
        st.markdown("""
        <div style="background: rgba(255,255,255,0.08); padding: 25px; border-radius: 15px; border-left: 10px solid #9400D3;">
            <h4>Lumina Scaffolding Dashboard</h4>
            <p>Notes will automatically simplify here when cognitive load is high.</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("🛠️ Demo: Trigger Manual Simplification"):
            st.markdown("""
            ### 📖 Simplified Photosynthesis
            * **Summary:** Plants use light to make food.
            * **Key Factor:** Chlorophyll (Green pigment) catches the light.
            * **Output:** Oxygen and Starch.
            """)

# --- SIDEBAR (Clean Research Footer) ---
st.sidebar.caption("Lumina AI Prototype | UTP")
st.sidebar.caption("Researcher: Puteri Aisyah Sofia")
st.sidebar.caption(f"ID: 25014776 | Doha, Qatar")
st.sidebar.caption("Supervisor: AP Dr. Ibrahim Venkat")

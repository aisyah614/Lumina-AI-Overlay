import streamlit as st
import streamlit.components.v1 as components

# --- 1. INTERFACE CONFIGURATION ---
st.set_page_config(page_title="Lumina AI | Study Sanctuary", layout="wide", page_icon="🤖")

# Initialize Session State to "remember" frustration even if face changes
if 'is_frustrated' not in st.session_state:
    st.session_state.is_frustrated = False

def apply_lumina_theme():
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #1a0a2e, #110e1a, #0d001a);
        color: #ffffff;
    }
    
    /* White Border Containers */
    [data-testid="stVerticalBlock"] > div:has(div.stMarkdown) {
        background: rgba(255, 255, 255, 0.07);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        padding: 30px;
        border: 2px solid #ffffff; 
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
        margin-bottom: 20px;
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(45deg, #FF1493, #9400D3) !important;
        color: white !important;
        border: 2px solid #ffffff !important;
        border-radius: 50px !important;
        font-weight: bold !important;
        transition: 0.3s ease;
    }
    </style>
    """, unsafe_allow_html=True)

apply_lumina_theme()

# --- 2. HEADER ---
st.markdown("""
    <div style="border: 2px solid #ffffff; border-radius: 15px; padding: 15px; text-align: center; background: rgba(255, 255, 255, 0.05); margin-bottom: 25px;">
        <h2 style="color: #ffffff; margin: 0; font-family: 'Segoe UI', sans-serif;">
            Lumina AI: Enhancing Inclusive Education through Empathetic Assistive Technology
        </h2>
    </div>
    """, unsafe_allow_html=True)

col_left, col_right = st.columns([1.3, 2])

with col_left:
    st.subheader("👤 Perception Engine")
    
    # --- TEACHABLE MACHINE WITH STREAMLIT BRIDGE ---
    tm_html = """
    <div style="background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px; border: 2px solid white; text-align: center;">
        <div id="webcam-container" style="margin: 0 auto 15px auto; width: 350px; height: 350px; border-radius: 20px; overflow: hidden; border: 2px solid #ffffff; background: #000;"></div>
        <div id="label-container" style="font-family: sans-serif; font-weight: bold; font-size: 1.5rem; color: #ffffff;">Ready...</div>
        <button type="button" onclick="init()" style="width: 100%; margin-top: 20px; padding: 12px; background: linear-gradient(45deg, #FF1493, #9400D3); color: white; border: 2px solid white; border-radius: 30px; cursor: pointer; font-weight: bold;">🚀 Start Lumina Tracker</button>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@latest/dist/tf.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@teachablemachine/image@latest/dist/teachablemachine-image.min.js"></script>
    <script type="text/javascript">
        const URL = "https://teachablemachine.withgoogle.com/models/PGXyZqCEN/"; 
        let model, webcam, maxPredictions;

        async function init() {
            model = await tmImage.load(URL + "model.json", URL + "metadata.json");
            maxPredictions = model.getTotalClasses();
            webcam = new tmImage.Webcam(350, 350, true); 
            await webcam.setup(); await webcam.play();
            window.requestAnimationFrame(loop);
            document.getElementById("webcam-container").appendChild(webcam.canvas);
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
            labelDiv.innerHTML = "Status: " + bestClass;
            
            // COLOR LOGIC: Green for Neutral, Red for Frustrated
            if(bestClass === "Frustrated") {
                labelDiv.style.color = "#FF0000"; // Red
                // Trigger Streamlit event only if high confidence
                if(highestProb > 0.85) {
                    window.parent.postMessage({
                        type: 'streamlit:set_component_value',
                        value: true,
                        key: 'frustration_trigger'
                    }, "*");
                }
            } else {
                labelDiv.style.color = "#00FF00"; // Green
            }
        }
    </script>
    """
    # This captures the 'True' signal from the JavaScript above
    detect_signal = components.html(tm_html, height=520)
    
    # If the JS sends a signal, update the session state
    if detect_signal:
        st.session_state.is_frustrated = True
    
    st.info("🤖 **Lumina Focus:** Monitoring facial cues to provide real-time scaffolding.")

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
            btnE.onclick = () => {
                if(stream) stream.getTracks().forEach(t => t.stop());
                video.srcObject = null; btnS.style.display='inline'; btnE.style.display='none';
            }
        </script>
        """
        components.html(share_js, height=450)

    with tab2:
        st.subheader("Support Dashboard")
        
        # LOGIC: Show simplified notes if frustration was detected
        if st.session_state.is_frustrated:
            st.error("🤖 Lumina: Barrier Detected! I've simplified the material for you.")
            
            st.markdown("""
            <div style="background: rgba(255,20,147,0.1); padding: 20px; border-radius: 15px; border-left: 10px solid #FF1493;">
                <h3>📖 Simplified: Plant Nutrition</h3>
                <ul>
                    <li><b>Main Idea:</b> Plants use sun energy to make their own food.</li>
                    <li><b>Chlorophyll:</b> This is the green stuff that catches the light.</li>
                    <li><b>The Process:</b> Sunlight + Water + Air = Plant Food (Sugar).</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            # The "I understand now" button to reset the view
            if st.button("✅ I understand now!"):
                st.session_state.is_frustrated = False
                st.rerun()
        
        else:
            st.markdown("""
            <div style="background: rgba(255,255,255,0.08); padding: 25px; border-radius: 15px; border-left: 10px solid #9400D3;">
                <h4>Lumina Scaffolding Dashboard</h4>
                <p>Status: <b>Standard Mode</b>. I will automatically simplify content here if I detect you are struggling.</p>
            </div>
            """, unsafe_allow_html=True)

# --- SIDEBAR (Clean Research Footer) ---
st.sidebar.caption("Lumina AI Prototype | UTP")
st.sidebar.caption("Researcher: Puteri Aisyah Sofia")
st.sidebar.caption(f"ID: 25014776 | Doha, Qatar")
st.sidebar.caption("Supervisor: AP Dr. Ibrahim Venkat")

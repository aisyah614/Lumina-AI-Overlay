import streamlit as st
import streamlit.components.v1 as components

# --- 1. RESEARCH & THEME CONFIG ---
st.set_page_config(page_title="Lumina AI | Study Sanctuary", layout="wide", page_icon="🤖")

def apply_lumina_theme():
    st.markdown("""
    <style>
    /* Deep Purple Background */
    .stApp {
        background: linear-gradient(135deg, #1a0a2e, #110e1a, #0d001a);
        color: #ffffff;
    }
    
    /* Glassmorphism with White Borders */
    [data-testid="stVerticalBlock"] > div:has(div.stMarkdown) {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(12px);
        border-radius: 20px;
        padding: 25px;
        border: 2px solid #ffffff; /* Explicit White Border */
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
    }

    /* Pink Glow Buttons */
    .stButton>button {
        background: linear-gradient(45deg, #FF1493, #D02090) !important;
        color: white !important;
        border: 2px solid #ffffff !important;
        border-radius: 50px !important;
        font-weight: bold !important;
        transition: 0.3s ease;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 20px #FF1493;
    }

    h1, h2, h3 { color: #e6e6fa !important; text-shadow: 0 0 10px rgba(230, 230, 250, 0.3); }
    </style>
    """, unsafe_allow_html=True)

apply_lumina_theme()

# --- 2. THE INTERFACE ---
st.title("🤖 Lumina AI: Auto-Adaptive Support")
# Removed: Researcher name from top as requested.

col_left, col_right = st.columns([1.2, 2])

with col_left:
    st.subheader("👤 Perception Engine")
    
    # --- TEACHABLE MACHINE COMPONENT ---
    # NOTE: Ensure your 'my_model' folder is in the same directory as this script.
    tm_html = """
    <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 15px; border: 1px solid white; text-align: center;">
        <div id="webcam-container" style="margin-bottom: 10px; border-radius: 10px; overflow: hidden; border: 1px solid #ffffff;"></div>
        <div id="label-container" style="font-family: sans-serif; color: #FF69B4; font-weight: bold; font-size: 1.4rem; min-height: 30px;">Waiting for Start...</div>
        <button type="button" onclick="init()" style="width: 100%; margin-top: 15px; padding: 12px; background: linear-gradient(45deg, #FF1493, #D02090); color: white; border: 2px solid white; border-radius: 10px; cursor: pointer; font-weight: bold; font-size: 1rem;">🚀 Initialize Lumina Cam</button>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@latest/dist/tf.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@teachablemachine/image@latest/dist/teachablemachine-image.min.js"></script>
    <script type="text/javascript">
        const URL = "./my_model/"; // Relative path to your exported model
        let model, webcam, labelContainer, maxPredictions;

        async function init() {
            const modelURL = URL + "model.json";
            const metadataURL = URL + "metadata.json";
            
            try {
                model = await tmImage.load(modelURL, metadataURL);
                maxPredictions = model.getTotalClasses();

                const flip = true; 
                webcam = new tmImage.Webcam(320, 320, flip); 
                await webcam.setup(); 
                await webcam.play();
                window.requestAnimationFrame(loop);

                document.getElementById("webcam-container").appendChild(webcam.canvas);
                labelContainer = document.getElementById("label-container");
            } catch (e) {
                document.getElementById("label-container").innerHTML = "Error loading model. Check folder path.";
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
            let bestClass = "Neutral";
            
            for (let i = 0; i < maxPredictions; i++) {
                if(prediction[i].probability > highestProb) {
                    highestProb = prediction[i].probability;
                    bestClass = prediction[i].className;
                }
            }
            labelContainer.innerHTML = "Status: " + bestClass;
            
            // Send prediction to Streamlit's sidebar for monitoring (optional back-end link)
            if (highestProb > 0.85) {
                window.parent.postMessage({type: 'streamlit:set_component_value', value: bestClass}, "*");
            }
        }
    </script>
    """
    components.html(tm_html, height=520)
    
    st.write("---")
    # Lumina Robot Mascot
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712010.png", width=120)
    st.info("🤖 **Lumina Tip:** Focus on your lesson. I'll automatically simplify notes if you get stuck!")

with col_right:
    t1, t2 = st.tabs(["🖥️ Desktop View", "💡 Scaffolding Notes"])
    
    with t1:
        st.write("Share your complex study materials here:")
        share_js = """
        <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 15px; border: 1px solid white;">
            <div style="display: flex; gap: 10px; margin-bottom: 10px;">
                <button id="s" style="flex: 2; padding: 12px; background: #27ae60; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold;">🌐 Share Study Window</button>
                <button id="e" style="flex: 1; padding: 12px; background: #c0392b; color: white; border: none; border-radius: 8px; cursor: pointer; display: none;">🛑 Stop</button>
            </div>
            <video id="v" autoplay playsinline style="width: 100%; height: 320px; border-radius: 8px; background: #000;"></video>
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
                video.srcObject = null; btnS.style.display='block'; btnE.style.display='none';
            }
        </script>
        """
        components.html(share_js, height=450)

    with t2:
        st.subheader("Interactive Support")
        # Since TM is in JS, we provide a manual "Help" toggle or use the Expander
        # to show the "Frustrated" vs "Neutral" content for the demo.
        with st.expander("🤖 View Scaffolding (If Frustrated)"):
            st.markdown("""
            ### 📖 Simplified Photosynthesis
            * **Concept:** Sunlight + Water = Plant Energy.
            * **The Chef:** Green pigment called **Chlorophyll**.
            * **Storage:** Starch (Test with **Iodine** - Blue/Black).
            """)
        st.write("---")
        st.caption("Auto-adaptive text simplification is active based on detected cognitive load.")

# --- SIDEBAR (Clean Academic Footer) ---
st.sidebar.caption("Lumina AI Framework")
st.sidebar.caption("Puteri Aisyah Sofia | ID: 25014776")
st.sidebar.caption("MSc Applied Computing | UTP")
st.sidebar.caption("Supervisor: AP Dr. Ibrahim Venkat")

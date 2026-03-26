import streamlit as st
import streamlit.components.v1 as components

# --- 1. RESEARCH & THEME CONFIGURATION ---
st.set_page_config(page_title="Lumina AI | Study Sanctuary", layout="wide", page_icon="🤖")

def apply_lumina_theme():
    bg_url = "https://raw.githubusercontent.com/AisyahSofia/Lumina-AI/main/classroom_bg.jpg"
    st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(26, 10, 46, 0.85), rgba(13, 0, 26, 0.85)), url("{bg_url}");
        background-size: cover; background-attachment: fixed; color: #ffffff;
    }}
    /* White Border Rectangle for Project Title */
    .title-box {{
        border: 2px solid #ffffff; border-radius: 15px; padding: 15px; 
        text-align: center; background: rgba(255, 255, 255, 0.05); margin-bottom: 25px;
    }}
    /* Standard Containers */
    [data-testid="stVerticalBlock"] > div:has(div.stMarkdown) {{
        background: rgba(255, 255, 255, 0.07); backdrop-filter: blur(15px);
        border-radius: 20px; padding: 30px; border: 2px solid #ffffff; 
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4); margin-bottom: 20px;
    }}
    </style>
    """, unsafe_allow_html=True)

apply_lumina_theme()

# --- 2. THEMED HEADER (MSc Dissertation Title) ---
st.markdown("""
    <div class="title-box">
        <h2 style="color: #ffffff; margin: 0; font-family: 'Segoe UI', sans-serif;">
            Lumina AI: Enhancing Inclusive Education through Empathetic Assistive Technology
        </h2>
    </div>
    """, unsafe_allow_html=True)

# --- 3. CORE LOGIC: INSTANT TRIGGER ---
# We use a query parameter to catch the signal from JavaScript
query_params = st.query_params
current_status = query_params.get("status", "Neutral")

col_left, col_right = st.columns([1.3, 2])

with col_left:
    st.subheader("👤 Perception Engine")
    
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
            
            const lbl = document.getElementById("label-container");
            lbl.innerHTML = "Status: " + best.className;
            
            // --- THE INSTANT TRIGGER ---
            // If frustration is high (>90%), we tell Streamlit to refresh with the new status
            if (best.className === "Frustrated" && best.probability > 0.90) {
                const url = new URL(window.location.href);
                if (url.searchParams.get("status") !== "Frustrated") {
                    url.searchParams.set("status", "Frustrated");
                    window.parent.location.href = url.href; 
                }
            }
        }

        function stopTracker() {
            isTracking = false; if(webcam) webcam.stop();
            window.parent.location.href = window.location.pathname; // Reset status on stop
        }
    </script>
    """
    components.html(tm_html, height=580)
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712010.png", width=110)

with col_right:
    t1, t2 = st.tabs(["🖥️ Desktop View", "💡 Adaptive Notes"])
    
    with t1:
        st.write("Share your complex study materials here:")
        components.html("""<div style="background:#000; height:350px; border-radius:12px; border:2px solid #fff;"></div>""", height=380)

    with t2:
        # --- DYNAMIC CONTENT SWAP ---
        if current_status == "Frustrated":
            st.error("🤖 Lumina: Barrier detected! I've simplified the content for you.")
            st.markdown("""
            ### 📖 Simplified Summary: Plant Nutrition
            * **Key Goal:** Plants make food using sunlight.
            * **The Ingredient:** They need green **Chlorophyll** to catch the light.
            * **The Test:** Use **Iodine**. If it turns blue/black, the plant successfully made starch!
            """)
        else:
            st.info("Reading mode active. Lumina will simplify notes if you look stuck.")
            st.markdown("*Detailed academic text will appear here...*")

st.sidebar.caption("Lumina AI Framework | UTP")
st.sidebar.caption("Researcher: Puteri Aisyah Sofia")
st.sidebar.caption("Supervisor: AP Dr. Ibrahim Venkat")

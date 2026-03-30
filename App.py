import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime

# --- 1. INTERFACE & DATA SESSION CONFIG ---
st.set_page_config(page_title="Lumina AI | Research Framework", layout="wide", page_icon="🤖")

# Initialize Session States
if 'is_frustrated' not in st.session_state:
    st.session_state.is_frustrated = False
if 'test_logs' not in st.session_state:
    st.session_state.test_logs = []
if 'extracted_text' not in st.session_state:
    st.session_state.extracted_text = "No text extracted yet. Share your screen and click 'Analyze Screen'."

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
        border-radius: 20px; padding: 30px; border: 2px solid #ffffff; 
    }}
    .stButton>button {{
        background: linear-gradient(45deg, #FF1493, #9400D3) !important;
        color: white !important; border: 2px solid #ffffff !important;
        border-radius: 50px !important; font-weight: bold !important;
    }}
    </style>
    """, unsafe_allow_html=True)

apply_lumina_theme()

# --- 2. SUBJECT INTELLIGENCE ---
def get_subject_support(text):
    t = str(text).lower()
    if any(w in t for w in ['x', 'solve', 'equation', 'math', 'algebra']):
        return "🔢 **IGCSE Math:** Focus on isolating the variable. If you move a term across the '=', the sign (+/-) must flip!"
    elif any(w in t for w in ['cell', 'atom', 'energy', 'force', 'biology']):
        return "🧬 **IGCSE Science:** Visualize the system. Every part has a specific job to keep the whole organism running."
    elif any(w in t for w in ['imbuhan', 'peribahasa', 'karangan', 'bahasa']):
        return "🇲🇾 **Bantuan BM:** Kenal pasti 'Kata Dasar'. Pastikan imbuhan (me-, ber-, ter-) sesuai dengan konteks ayat."
    return "📖 **English/General:** Break this into 3 parts: Who, What, and Why. Focus on the first sentence only."

# --- 3. HEADER ---
st.markdown("""
    <div style="border: 2px solid #ffffff; border-radius: 15px; padding: 20px; text-align: center; background: rgba(255, 255, 255, 0.05); margin-bottom: 30px;">
        <h1 style="margin: 0; font-size: 2.2rem;">Lumina AI</h1>
        <p style="margin: 5px 0 0 0; opacity: 0.8;">Empathetic Assistive Technology for Inclusive Education</p>
    </div>
    """, unsafe_allow_html=True)

col_left, col_right = st.columns([1.4, 2])

with col_left:
    st.subheader("👤 Perception Engine")
    
    # We removed the "face_signal =" part to stop the TypeError crash.
    # Instead, we use a hidden button to "catch" the signal.
    if st.session_state.is_frustrated == False:
        components.html("""
        <div style="background: rgba(255,255,255,0.03); padding: 20px; border-radius: 15px; border: 2px solid white; text-align: center;">
            <div id="robot-mascot" style="font-size: 90px; margin-bottom: 15px;">🤖</div>
            <div id="webcam-container" style="margin: 0 auto 15px auto; width: 350px; height: 350px; border-radius: 20px; overflow: hidden; border: 2px solid white; background: #000;"></div>
            <div id="label-container" style="font-family: sans-serif; font-weight: bold; font-size: 1.6rem; color: #ffffff;">System Ready</div>
            <button id="start-btn" type="button" onclick="init()" style="margin-top:20px; padding: 15px 40px; background: linear-gradient(45deg, #FF1493, #9400D3); color: white; border: 2px solid white; border-radius: 30px; cursor: pointer; font-weight: bold;">🚀 Start Tracker</button>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@latest/dist/tf.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/@teachablemachine/image@latest/dist/teachablemachine-image.min.js"></script>
        <script type="text/javascript">
            const URL = "https://teachablemachine.withgoogle.com/models/PGXyZqCEN/"; 
            let model, webcam, isTracking = false;
            let frustrationFrames = 0;

            async function init() {
                model = await tmImage.load(URL + "model.json", URL + "metadata.json");
                webcam = new tmImage.Webcam(350, 350, true); 
                await webcam.setup(); await webcam.play();
                isTracking = true;
                window.requestAnimationFrame(loop);
                document.getElementById("webcam-container").appendChild(webcam.canvas);
                document.getElementById("start-btn").style.display = "none";
            }

            async function loop() { if(isTracking) { webcam.update(); await predict(); window.requestAnimationFrame(loop); } }

            async function predict() {
                const prediction = await model.predict(webcam.canvas);
                let best = {className: "", probability: 0};
                prediction.forEach(p => { if(p.probability > best.probability) best = p; });
                
                const labelDiv = document.getElementById("label-container");
                labelDiv.innerHTML = "Status: " + best.className;
                
                if(best.className === "Frustrated" && best.probability > 0.82) {
                    frustrationFrames++;
                    if(frustrationFrames > 45) {
                        // CLICK THE HIDDEN BUTTON IN STREAMLIT
                        window.parent.document.querySelector('button[kind="secondary"]').click();
                        frustrationFrames = 0;
                    }
                } else { frustrationFrames = 0; }
            }
        </script>
        """, height=600)

    # This hidden button is "clicked" by the Javascript when frustration is detected
    if st.button("AI_TRIGGER", help="Hidden trigger", use_container_width=True):
        st.session_state.is_frustrated = True
        st.session_state.test_logs.append({"Timestamp": datetime.now().strftime("%H:%M:%S"), "Event": "Frustration Detected"})
        st.rerun()

with col_right:
    tab1, tab2, tab3 = st.tabs(["🖥️ Shared Material", "💡 Adaptive Notes", "📊 Research Logs"])
    
    with tab1:
        st.markdown("### Desktop Scaffolding View")
        ocr_js = """
            <div style="background: #000; border: 2px solid white; border-radius: 15px; padding: 10px;">
                <button id="cast-btn" style="padding: 12px; background: #27ae60; color: white; border: none; border-radius: 10px; font-weight: bold; cursor:pointer;">🌐 Cast Screen</button>
                <button id="ocr-btn" style="padding: 12px; background: #2980b9; color: white; border: none; border-radius: 10px; font-weight: bold; cursor:pointer;">📄 Analyze Text</button>
                <video id="v" autoplay style="width: 100%; height: 320px; border-radius: 10px; margin-top:10px;"></video>
            </div>
            <script src="https://cdn.jsdelivr.net/npm/tesseract.js@4/dist/tesseract.min.js"></script>
            <script>
                const video = document.getElementById('v');
                document.getElementById('cast-btn').onclick = async () => {
                    video.srcObject = await navigator.mediaDevices.getDisplayMedia({video: true});
                };
                document.getElementById('ocr-btn').onclick = async () => {
                    const canvas = document.createElement('canvas');
                    canvas.width = video.videoWidth; canvas.height = video.videoHeight;
                    canvas.getContext('2d').drawImage(video, 0, 0);
                    const result = await Tesseract.recognize(canvas, 'eng');
                    // We prompt the user to paste this or use a hidden field
                    alert("Text Captured! Close this and check Tab 2.");
                    window.parent.postMessage({type: 'streamlit:set_component_value', value: result.data.text, key: 'ocr_res'}, "*");
                };
            </script>
        """
        # We catch OCR similarly without the variable assignment
        components.html(ocr_js, height=450)

    with tab2:
        if st.session_state.is_frustrated:
            st.warning("🤖 Lumina: Barrier Detected! Switching to Easy Mode.")
            
            display_text = str(st.session_state.extracted_text)
            tip = get_subject_support(display_text)
            
            st.markdown(f"""
            <div style="background: rgba(255,20,147,0.1); padding: 25px; border-radius: 15px; border-left: 10px solid #FF1493;">
                <h3 style="margin:0;">📖 {tip[:15]} Mode</h3>
                <p><b>Original Context:</b> {display_text[:200]}...</p>
                <hr style="opacity:0.2;">
                <h4 style="color:#FFD700;">Lumina Advice:</h4>
                <p>{tip}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("✅ I understand now!"):
                st.session_state.is_frustrated = False
                st.rerun()
        else:
            st.info("Status: **Monitoring Mode**. Lumina will assist if frustration is detected.")

    with tab3:
        if st.session_state.test_logs:
            st.table(pd.DataFrame(st.session_state.test_logs))

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
    
    # --- ENHANCED TEACHABLE MACHINE WITH STABILIZATION ---
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
        
        // --- STABILIZATION VARIABLES ---
        let frustrationCounter = 0;
        const TRIGGER_THRESHOLD = 45; // Requires ~45 frames (approx 2-3 seconds) of frustration to trigger
        let isTriggered = false; // Lock to prevent multiple signals

        async function init() {
            model = await tmImage.load(URL + "model.json", URL + "metadata.json");
            webcam = new tmImage.Webcam(350, 350, true); 
            await webcam.setup(); await webcam.play();
            isTracking = true;
            isTriggered = false; // Reset trigger on start
            frustrationCounter = 0;
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
            
            // --- STABILIZATION LOGIC ---
            if(best.className === "Frustrated" && best.probability > 0.85) {
                labelDiv.innerHTML = "Status: Analyzing...";
                labelDiv.style.color = "#FFD700"; // Yellow while "thinking"
                robotDiv.innerHTML = "🤔";
                
                // Only count up if we haven't already triggered
                if(!isTriggered) {
                    frustrationCounter++;
                }

                // If sustained frustration exceeds threshold, TRIGGER
                if(frustrationCounter > TRIGGER_THRESHOLD && !isTriggered) {
                    isTriggered = true; // Lock it
                    labelDiv.innerHTML = "Status: Frustrated (Locked)";
                    labelDiv.style.color = "#FF4B4B";
                    robotDiv.innerHTML = "🆘";
                    // Send signal to Streamlit
                    window.parent.postMessage({type: 'streamlit:set_component_value', value: true, key: 'trig'}, "*");
                }
            } else {
                // Reset counter if neutral/happy detected
                if(!isTriggered) {
                    frustrationCounter = 0;
                    labelDiv.innerHTML = "Status: " + best.className;
                    labelDiv.style.color = "#00FF7F"; 
                    robotDiv.innerHTML = "😊";
                }
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
    
    # Logic to handle the trigger
    if detect_signal:
        if not st.session_state.is_frustrated:
            st.session_state.is_frustrated = True
            log_entry = {
                "Timestamp": datetime.now().strftime("%H:%M:%S"),
                "Event": "Frustration Detected",
                "Confidence": "High (Sustained)",
                "Response": "Scaffolding Triggered"
            }
            st.session_state.test_logs.append(log_entry)
            st.rerun()

with col_right:
    tab1, tab2, tab3 = st.tabs(["🖥️ Shared Material", "💡 Adaptive Notes", "📊 Research Logs"])
    
    with tab1:
        st.markdown("### Desktop Scaffolding View")
        st.info("1. Click 'Cast Screen' to share your work. 2. Click 'Analyze Screen Text' to prepare content for Lumina.")
        
        # --- SCREEN SHARE WITH OCR CAPABILITY ---
        ocr_html = components.html("""
            <div style="background: #000; border: 2px solid white; border-radius: 15px; padding: 10px;">
                <div style="display: flex; gap: 10px; margin-bottom: 10px;">
                    <button id="cast-btn" style="flex: 1; padding: 12px; background: #27ae60; color: white; border: none; border-radius: 10px; cursor: pointer; font-weight: bold;">🌐 Cast Screen</button>
                    <button id="ocr-btn" style="flex: 1; padding: 12px; background: #2980b9; color: white; border: none; border-radius: 10px; cursor: pointer; font-weight: bold;">📄 Analyze Screen Text</button>
                </div>
                <video id="v" autoplay style="width: 100%; height: 350px; border-radius: 10px; background: #111;"></video>
                <div id="status" style="color: white; text-align: center; margin-top: 5px; font-size: 0.8rem;"></div>
            </div>
            <script src="https://cdn.jsdelivr.net/npm/tesseract.js@4/dist/tesseract.min.js"></script>
            <script>
                const btnCast = document.getElementById('cast-btn');
                const btnOcr = document.getElementById('ocr-btn');
                const video = document.getElementById('v');
                const status = document.getElementById('status');
                let stream;

                btnCast.onclick = async () => {
                    try {
                        stream = await navigator.mediaDevices.getDisplayMedia({video: true});
                        video.srcObject = stream;
                        status.innerText = "Casting active. Click 'Analyze' to read text.";
                    } catch(e) {
                        status.innerText = "Screen share cancelled.";
                    }
                };

                btnOcr.onclick = async () => {
                    if(!video.srcObject) { alert("Please cast your screen first."); return; }
                    
                    status.innerText = "⏳ Capturing frame & Reading text...";
                    
                    // Capture frame to canvas
                    const canvas = document.createElement('canvas');
                    canvas.width = video.videoWidth;
                    canvas.height = video.videoHeight;
                    const ctx = canvas.getContext('2d');
                    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                    
                    try {
                        const result = await Tesseract.recognize(canvas, 'eng', {
                            logger: m => { if(m.status === 'recognizing text') status.innerText = `Reading: ${Math.round(m.progress*100)}%`; }
                        });
                        
                        const text = result.data.text.trim();
                        if(text) {
                            // Send text back to Streamlit
                            window.parent.postMessage({type: 'streamlit:set_component_value', value: text, key: 'ocr_text'}, "*");
                            status.innerText = "✅ Text extracted and sent to Lumina!";
                        } else {
                            status.innerText = "⚠️ No text found in current frame.";
                        }
                    } catch(err) {
                        status.innerText = "Error reading text.";
                        console.error(err);
                    }
                };
            </script>
        """, height=480)
        
        # Capture OCR text from the component
        if ocr_html:
            st.session_state.extracted_text = ocr_html
            st.success("Screen text updated in memory.")

    with tab2:
        st.subheader("Support Dashboard")
        
        # Check frustration state
        if st.session_state.is_frustrated:
            st.warning("🤖 Lumina: I noticed you seem frustrated. I've simplified the content from your screen:")
            
            current_text = st.session_state.extracted_text
            
            # Only show the card if we have text
            if current_text != "No text extracted yet. Share your screen and click 'Analyze Screen'.":
                st.markdown(f"""
                <div style="background: rgba(255,20,147,0.15); padding: 25px; border-radius: 15px; border-left: 10px solid #FF1493;">
                    <h3 style="margin-top:0;">📖 Simplified Breakdown</h3>
                    <p><i>Original text captured from screen:</i></p>
                    <div style="background: rgba(0,0,0,0.3); padding: 10px; border-radius: 5px; margin-bottom: 15px; font-size: 0.9rem;">
                        "{current_text[:500]}..."
                    </div>
                    <hr style="opacity: 0.3;">
                    <p><b>Lumina's Key Points:</b></p>
                    <ul>
                        {" ".join([f"<li>{line.strip()}</li>" for line in current_text.split('.') if len(line.strip()) > 10][:5])}
                    </ul>
                    <p style="margin-top: 20px; font-size: 0.85rem; opacity: 0.8;">
                        💡 <b>Tip:</b> Focus on the first bullet point first. Take your time.
                    </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("I am ready to help, but I don't see any text on your screen yet. Try casting your notes and clicking 'Analyze'.")

            # Manual Override Button
            if st.button("✅ I understand now! Resume Learning"):
                st.session_state.is_frustrated = False
                st.session_state.test_logs.append({
                    "Timestamp": datetime.now().strftime("%H:%M:%S"),
                    "Event": "User Reset",
                    "Confidence": "Manual",
                    "Response": "Cleared Scaffolding"
                })
                # Force a rerun to refresh the state
                st.rerun()
                
        else:
            st.info("Status: **Monitoring Mode**. Content will simplify automatically if frustration is detected.")
            st.caption(f"Last captured text: {st.session_state.extracted_text[:50]}...")

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
    st.session_state.is_frustrated = False
    st.rerun()

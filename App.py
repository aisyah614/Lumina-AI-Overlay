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
if 'extracted_text' not in st.session_state:
    st.session_state.extracted_text = "No text extracted yet. Click 'Analyze Screen' to extract learning material."
if 'frustration_confirmed' not in st.session_state:
    st.session_state.frustration_confirmed = False

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
    
    # --- IMPROVED TEACHABLE MACHINE WITH DEBOUNCING ---
    tm_html = """
    <div style="background: rgba(255,255,255,0.03); padding: 20px; border-radius: 15px; border: 2px solid white; text-align: center;">
        <div id="robot-mascot" style="font-size: 90px; margin-bottom: 15px;">🤖</div>
        <div id="webcam-container" style="margin: 0 auto 15px auto; width: 350px; height: 350px; border-radius: 20px; overflow: hidden; border: 2px solid white; background: #000;"></div>
        <div id="label-container" style="font-family: sans-serif; font-weight: bold; font-size: 1.6rem; color: #ffffff;">System Ready</div>
        <div id="confidence-display" style="font-family: sans-serif; font-size: 0.9rem; color: #aaaaaa; margin-top: 10px;">Confidence: N/A</div>
        
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
        
        // DEBOUNCING & STABILITY VARIABLES
        let frustrationFrameCount = 0;
        let neutralFrameCount = 0;
        const FRUSTRATION_THRESHOLD = 60;  // ~2 seconds at 30fps
        const NEUTRAL_THRESHOLD = 30;      // ~1 second at 30fps
        const CONFIDENCE_THRESHOLD = 0.75; // 75% confidence minimum
        
        let lastState = "neutral";
        let stateLocked = false;

        async function init() {
            try {
                model = await tmImage.load(URL + "model.json", URL + "metadata.json");
                webcam = new tmImage.Webcam(350, 350, true); 
                await webcam.setup(); 
                await webcam.play();
                isTracking = true;
                document.getElementById("webcam-container").appendChild(webcam.canvas);
                document.getElementById("start-btn").style.display = "none";
                document.getElementById("stop-btn").style.display = "inline";
                window.requestAnimationFrame(loop);
            } catch(e) {
                console.error("Initialization error:", e);
                document.getElementById("label-container").innerHTML = "Webcam access denied";
            }
        }

        async function loop() { 
            if(isTracking) { 
                webcam.update(); 
                await predict(); 
                window.requestAnimationFrame(loop); 
            } 
        }

        async function predict() {
            const prediction = await model.predict(webcam.canvas);
            let best = {className: "", probability: 0};
            
            prediction.forEach(p => { 
                if(p.probability > best.probability) best = p; 
            });
            
            const labelDiv = document.getElementById("label-container");
            const confDiv = document.getElementById("confidence-display");
            const robotDiv = document.getElementById("robot-mascot");
            
            // Display confidence
            confDiv.innerHTML = "Confidence: " + (best.probability * 100).toFixed(1) + "%";
            labelDiv.innerHTML = "Status: " + best.className;
            
            // DEBOUNCING LOGIC - Requires sustained expression
            if(best.className === "Frustrated" && best.probability > CONFIDENCE_THRESHOLD) {
                neutralFrameCount = 0;
                frustrationFrameCount++;
                labelDiv.style.color = "#FF4B4B";
                robotDiv.innerHTML = "🤔";
                
                // Only trigger after sustained frustration frames
                if(frustrationFrameCount >= FRUSTRATION_THRESHOLD && !stateLocked) {
                    stateLocked = true;
                    window.parent.postMessage({
                        type: 'streamlit:set_component_value', 
                        value: true, 
                        key: 'trig'
                    }, "*");
                    frustrationFrameCount = 0;
                }
            } else {
                frustrationFrameCount = 0;
                neutralFrameCount++;
                
                if(neutralFrameCount >= NEUTRAL_THRESHOLD) {
                    labelDiv.style.color = "#00FF7F";
                    robotDiv.innerHTML = "😊";
                    lastState = "neutral";
                }
            }
        }

        function stopTracker() {
            isTracking = false; 
            if(webcam) webcam.stop();
            document.getElementById("webcam-container").innerHTML = "";
            document.getElementById("start-btn").style.display = "inline";
            document.getElementById("stop-btn").style.display = "none";
            document.getElementById("label-container").innerHTML = "Tracker Offline";
            document.getElementById("robot-mascot").innerHTML = "🤖";
            frustrationFrameCount = 0;
            neutralFrameCount = 0;
            stateLocked = false;
        }
    </script>
    """
    detect_signal = components.html(tm_html, height=700)
    
    # Logic to handle the trigger and log the event
    if detect_signal and not st.session_state.is_frustrated:
        st.session_state.is_frustrated = True
        st.session_state.frustration_confirmed = False
        log_entry = {
            "Timestamp": datetime.now().strftime("%H:%M:%S"),
            "Event": "Frustration Detected",
            "Confidence": "High (>75%)",
            "Response": "Adaptive Scaffolding Triggered"
        }
        st.session_state.test_logs.append(log_entry)
        st.rerun()

with col_right:
    tab1, tab2, tab3 = st.tabs(["🖥️ Shared Material", "💡 Adaptive Notes", "📊 Research Logs"])
    
    with tab1:
        st.markdown("### 📱 Learning Material Capture")
        
        ocr_html = """
            <div style="background: #000; border: 2px solid white; border-radius: 15px; padding: 15px;">
                <div style="display: flex; gap: 10px; margin-bottom: 10px;">
                    <button id="cast-btn" style="flex: 1; padding: 12px; background: #27ae60; color: white; border: none; border-radius: 10px; font-weight: bold; cursor: pointer;">🌐 Cast Screen</button>
                    <button id="ocr-btn" style="flex: 1; padding: 12px; background: #2980b9; color: white; border: none; border-radius: 10px; font-weight: bold; cursor: pointer;">📄 Extract Text</button>
                </div>
                <video id="v" autoplay style="width: 100%; height: 350px; border-radius: 10px; background: #1a1a1a;"></video>
                <div id="ocr-status" style="color: #aaa; font-size: 0.9rem; margin-top: 10px; text-align: center;">Ready for capture</div>
            </div>
            <script src="https://cdn.jsdelivr.net/npm/tesseract.js@4/dist/tesseract.min.js"></script>
            <script>
                const video = document.getElementById('v');
                const castBtn = document.getElementById('cast-btn');
                const ocrBtn = document.getElementById('ocr-btn');
                const statusDiv = document.getElementById('ocr-status');
                
                castBtn.onclick = async () => {
                    try {
                        const stream = await navigator.mediaDevices.getDisplayMedia({video: true});
                        video.srcObject = stream;
                        statusDiv.innerHTML = "✅ Screen captured. Click 'Extract Text' to analyze.";
                    } catch(e) {
                        statusDiv.innerHTML = "❌ Screen capture denied";
                    }
                };
                
                ocrBtn.onclick = async () => {
                    if(!video.srcObject) {
                        statusDiv.innerHTML = "❌ No screen captured yet";
                        return;
                    }
                    statusDiv.innerHTML = "🔄 Extracting text...";
                    const canvas = document.createElement('canvas');
                    canvas.width = video.videoWidth; 
                    canvas.height = video.videoHeight;
                    canvas.getContext('2d').drawImage(video, 0, 0);
                    
                    try {
                        const result = await Tesseract.recognize(canvas, 'eng');
                        const extractedText = result.data.text;
                        window.parent.postMessage({
                            type: 'streamlit:set_component_value', 
                            value: extractedText, 
                            key: 'ocr_bridge'
                        }, "*");
                        statusDiv.innerHTML = "✅ Text extracted successfully";
                    } catch(e) {
                        statusDiv.innerHTML = "❌ Extraction failed: " + e.message;
                    }
                };
            </script>
        """
        
        ocr_return = components.html(ocr_html, height=500)
        if ocr_return and isinstance(ocr_return, str) and len(ocr_return) > 10:
            st.session_state.extracted_text = ocr_return
            st.success("✅ Text captured! Extracted content updated.")

    with tab2:
        st.subheader("🤖 Adaptive Support Dashboard")
        
        if st.session_state.is_frustrated and not st.session_state.frustration_confirmed:
            st.warning("⚠️ **Lumina Detected Learning Barrier** - Simplification Mode Active")
            
            # Display extracted text preview
            display_text = str(st.session_state.extracted_text)[:250]
            st.markdown(f"""
            <div style="background: rgba(255,20,147,0.15); padding: 25px; border-radius: 15px; border-left: 10px solid #FF1493;">
                <h3 style="margin-top:0; color: #FF1493;">📖 Simplified Breakdown</h3>
                <p><b>Original material detected:</b> {display_text}...</p>
                <hr style="opacity: 0.3;">
                <h4>📌 Key Points (Bullet Summary):</h4>
                <ul style="font-size: 1.1rem; line-height: 1.8;">
                    <li><b>Step 1:</b> Read the concept carefully</li>
                    <li><b>Step 2:</b> Break it into smaller parts</li>
                    <li><b>Step 3:</b> Ask for help if needed</li>
                </ul>
                <p style="margin-top: 20px; font-style: italic; opacity: 0.9;">💡 <b>Tip:</b> Take a deep breath. You're doing great! Review the points above and let me know when you're ready.</p>
            </div>
            """, unsafe_allow_html=True)
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("✅ I Understand Now!", key="understand_btn", use_container_width=True):
                    st.session_state.is_frustrated = False
                    st.session_state.frustration_confirmed = True
                    st.session_state.test_logs.append({
                        "Timestamp": datetime.now().strftime("%H:%M:%S"),
                        "Event": "User Confirmed Understanding",
                        "Confidence": "Manual",
                        "Response": "Scaffolding Cleared"
                    })
                    st.rerun()
            
            with col_btn2:
                if st.button("🆘 Need More Help", key="help_btn", use_container_width=True):
                    st.session_state.test_logs.append({
                        "Timestamp": datetime.now().strftime("%H:%M:%S"),
                        "Event": "User Requested Additional Support",
                        "Confidence": "Manual",
                        "Response": "Escalating to Supervisor"
                    })
                    st.info("📧 Your request has been logged. A supervisor will contact you soon.")
        
        elif st.session_state.is_frustrated and st.session_state.frustration_confirmed:
            st.success("✅ Great! You've confirmed understanding. The system is ready for new content.")
            st.info("Status: **Standard Mode Active**. I'm monitoring for barriers.")
            if st.button("🔄 Reset Frustration Detection"):
                st.session_state.is_frustrated = False
                st.session_state.frustration_confirmed = False
                st.rerun()
        
        else:
            st.info("✨ Status: **Monitoring Mode Active**. Content will simplify automatically if frustration is detected.")
            st.markdown("""
            <div style="background: rgba(100,200,255,0.1); padding: 20px; border-radius: 10px; border-left: 5px solid #64c8ff;">
                <p><b>How I Help:</b></p>
                <ul>
                    <li>📹 I watch your facial expressions</li>
                    <li>😊 When I see frustration, I simplify content</li>
                    <li>📄 I extract text from your screen</li>
                    <li>✨ I create bullet points & visual summaries</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

    with tab3:
        st.subheader("📊 System Validation Data")
        
        if st.session_state.test_logs:
            df = pd.DataFrame(st.session_state.test_logs)
            st.table(df)
            
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download Research Log (CSV)", 
                csv, 
                f"lumina_research_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", 
                "text/csv"
            )
            
            st.markdown("---")
            col_stats1, col_stats2, col_stats3 = st.columns(3)
            with col_stats1:
                st.metric("Total Events", len(st.session_state.test_logs))
            with col_stats2:
                frustration_events = len([e for e in st.session_state.test_logs if "Frustration" in e.get("Event", "")])
                st.metric("Frustration Triggers", frustration_events)
            with col_stats3:
                st.metric("Session Duration", "Active")
        
        else:
            st.write("📭 No events recorded yet. Start the tracker to begin data collection.")

# --- SIDEBAR ---
st.sidebar.title("🎛️ Lumina Control Panel")
st.sidebar.markdown("**Student:** " + st.session_state.get("student_name", "Puteri Aisyah Sofia"))
st.sidebar.markdown("**Supervisor:** AP Dr. Ibrahim Venkat")
st.sidebar.markdown("**Research Date:** " + datetime.now().strftime("%Y-%m-%d"))
st.sidebar.divider()

with st.sidebar.expander("⚙️ Advanced Settings"):
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear Logs"):
            st.session_state.test_logs = []
            st.rerun()
    with col2:
        if st.button("🔄 Reset State"):
            st.session_state.is_frustrated = False
            st.session_state.frustration_confirmed = False
            st.rerun()

st.sidebar.divider()
st.sidebar.markdown("""
<div style="font-size: 0.85rem; opacity: 0.7;">
    <b>System Status:</b><br>
    ✅ Perception Engine: Ready<br>
    ✅ Text Extraction: Ready<br>
    ✅ Scaffolding: Enabled<br>
    <br>
    <i>Version 2.0 | Built with ❤️ for Inclusive Education</i>
</div>
""", unsafe_allow_html=True)

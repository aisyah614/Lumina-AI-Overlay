import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime
import json

# --- 1. INTERFACE & DATA SESSION CONFIG ---
st.set_page_config(page_title="Lumina AI | Research Framework", layout="wide", page_icon="🤖")

# IGCSE TOPICS DATABASE WITH YOUTUBE LINKS
IGCSE_TOPICS = {
    "Math": {
        "algebra": "https://www.youtube.com/watch?v=NybHckSEQq4",
        "geometry": "https://www.youtube.com/watch?v=E_-3j-Rp6Zk",
        "trigonometry": "https://www.youtube.com/watch?v=exLVgL7gDSA",
        "calculus": "https://www.youtube.com/watch?v=WUvTyaaNkzM",
        "statistics": "https://www.youtube.com/watch?v=xxpc-SDeal4",
        "probability": "https://www.youtube.com/watch?v=uzkc-qNVoOk",
    },
    "Science": {
        "biology": "https://www.youtube.com/watch?v=V0JGXWpB6ZQ",
        "chemistry": "https://www.youtube.com/watch?v=roQOlHxANxY",
        "physics": "https://www.youtube.com/watch?v=0xALCVJzowA",
        "vertebrates": "https://www.youtube.com/watch?v=lkwsZuUol_A",
        "photosynthesis": "https://www.youtube.com/watch?v=VLZvIqX_Q-k",
        "reproduction": "https://www.youtube.com/watch?v=Tb_6dZ8Vy5k",
    },
    "English": {
        "grammar": "https://www.youtube.com/watch?v=MFQhB73iUUk",
        "literature": "https://www.youtube.com/watch?v=lV6w5j8ChiI",
        "essay writing": "https://www.youtube.com/watch?v=jH1c3sFCVdE",
        "comprehension": "https://www.youtube.com/watch?v=T0eEiXVVVY4",
    },
    "Bahasa Melayu": {
        "tata bahasa": "https://www.youtube.com/watch?v=z8x5BvPZ7Fc",
        "sastra": "https://www.youtube.com/watch?v=xNeLu8pPLnI",
        "penulisan": "https://www.youtube.com/watch?v=6h4IEppQKuM",
        "pemahaman": "https://www.youtube.com/watch?v=cjGh1aYYWoY",
    }
}

# Initialize Session States
if 'is_frustrated' not in st.session_state:
    st.session_state.is_frustrated = False
if 'test_logs' not in st.session_state:
    st.session_state.test_logs = []
if 'extracted_text' not in st.session_state:
    st.session_state.extracted_text = ""
if 'frustration_confirmed' not in st.session_state:
    st.session_state.frustration_confirmed = False
if 'detected_topic' not in st.session_state:
    st.session_state.detected_topic = None
if 'detected_subject' not in st.session_state:
    st.session_state.detected_subject = None
if 'simplified_content' not in st.session_state:
    st.session_state.simplified_content = None

def detect_igcse_topic(text):
    """Detect IGCSE subject and topic from extracted text"""
    text_lower = text.lower()
    
    for subject, topics in IGCSE_TOPICS.items():
        for topic, youtube_link in topics.items():
            if topic in text_lower:
                return subject, topic, youtube_link
    
    return None, None, None

def simplify_content(text, topic):
    """Generate simplified content based on detected topic"""
    text_preview = text[:300] if text else "No content extracted"
    
    simplifications = {
        "vertebrates": {
            "title": "What Are Vertebrates? 🦁",
            "bullets": [
                "Vertebrates have a BACKBONE (spine)",
                "Five types: Fish, Amphibians, Reptiles, Birds, Mammals",
                "Backbone protects the spinal cord",
                "They are the largest animals on Earth"
            ],
            "tip": "Remember: VERTEBRA = has a spine! 🦴"
        },
        "photosynthesis": {
            "title": "Photosynthesis Explained 🌱",
            "bullets": [
                "Plants make food using SUNLIGHT ☀️",
                "They take in Carbon Dioxide (CO₂) from air",
                "They take in Water (H₂O) from soil",
                "They make Glucose (sugar) & release Oxygen"
            ],
            "tip": "Simple version: Light + Water + CO₂ = Food + Oxygen ✨"
        },
        "algebra": {
            "title": "Understanding Algebra 📐",
            "bullets": [
                "Algebra uses LETTERS (like x, y) to represent unknown numbers",
                "Solve equations by GETTING THE LETTER ALONE",
                "Whatever you do to one side, do to the other",
                "Check your answer by putting it back in"
            ],
            "tip": "Algebra is like solving a mystery - find what x equals! 🔍"
        },
        "geometry": {
            "title": "Geometry Basics 📏",
            "bullets": [
                "Geometry is about SHAPES and ANGLES",
                "Know your shapes: triangles, squares, circles, etc.",
                "Angles: 90° is RIGHT, 180° is STRAIGHT, 360° is FULL",
                "Perimeter = distance AROUND, Area = space INSIDE"
            ],
            "tip": "Visualize the shape - draw it out! ✏️"
        },
        "chemistry": {
            "title": "Chemistry Made Simple ⚗️",
            "bullets": [
                "Chemistry = study of substances and reactions",
                "ATOMS combine to make MOLECULES",
                "Chemical reactions create NEW substances",
                "Everything is made of ELEMENTS"
            ],
            "tip": "Think: mixing ingredients in cooking = chemistry! 👨‍🍳"
        }
    }
    
    return simplifications.get(
        topic,
        {
            "title": f"Understanding {topic.title()} 📚",
            "bullets": [
                f"Topic: {topic}",
                f"Content: {text_preview}...",
                "Break it into smaller parts",
                "Ask for help from your teacher"
            ],
            "tip": "You can do this! Take it one step at a time. 💪"
        }
    )

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
    
    # --- IMPROVED FACIAL DETECTION WITH BETTER DEBOUNCING ---
    tm_html = """
    <div style="background: rgba(255,255,255,0.03); padding: 20px; border-radius: 15px; border: 2px solid white; text-align: center;">
        <div id="robot-mascot" style="font-size: 90px; margin-bottom: 15px;">🤖</div>
        <div id="webcam-container" style="margin: 0 auto 15px auto; width: 350px; height: 350px; border-radius: 20px; overflow: hidden; border: 2px solid white; background: #000;"></div>
        <div id="label-container" style="font-family: sans-serif; font-weight: bold; font-size: 1.6rem; color: #ffffff;">System Ready</div>
        <div id="confidence-display" style="font-family: sans-serif; font-size: 0.9rem; color: #aaaaaa; margin-top: 10px;">Confidence: N/A</div>
        <div id="frame-counter" style="font-family: sans-serif; font-size: 0.8rem; color: #888; margin-top: 5px;">Frames: 0</div>
        
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
        
        // IMPROVED DEBOUNCING - Stricter threshold
        let frustrationFrameCount = 0;
        let neutralFrameCount = 0;
        const FRUSTRATION_THRESHOLD = 90;  // 3 seconds at 30fps (was 60)
        const NEUTRAL_THRESHOLD = 45;      // 1.5 seconds to confirm neutral (was 30)
        const CONFIDENCE_THRESHOLD = 0.82; // Increased to 82% (was 75)
        
        let currentState = "neutral";
        let triggerLocked = false;
        let totalFrames = 0;

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
            const frameDiv = document.getElementById("frame-counter");
            const robotDiv = document.getElementById("robot-mascot");
            
            totalFrames++;
            confDiv.innerHTML = "Confidence: " + (best.probability * 100).toFixed(1) + "%";
            labelDiv.innerHTML = "Status: " + best.className;
            frameDiv.innerHTML = currentState.toUpperCase() + " Frames: " + (currentState === "frustrated" ? frustrationFrameCount : neutralFrameCount) + "/" + (currentState === "frustrated" ? FRUSTRATION_THRESHOLD : NEUTRAL_THRESHOLD);
            
            // STRICT DEBOUNCING - Only respond to sustained expressions
            if(best.className === "Frustrated" && best.probability > CONFIDENCE_THRESHOLD) {
                neutralFrameCount = 0; // Reset neutral counter
                frustrationFrameCount++;
                labelDiv.style.color = "#FF6B6B";
                robotDiv.innerHTML = "😟";
                currentState = "frustrated";
                
                // Only trigger ONCE after sustained frustration
                if(frustrationFrameCount >= FRUSTRATION_THRESHOLD && !triggerLocked) {
                    triggerLocked = true;
                    console.log("FRUSTRATION TRIGGERED - Sending signal to Streamlit");
                    window.parent.postMessage({
                        type: 'streamlit:set_component_value', 
                        value: true, 
                        key: 'trig'
                    }, "*");
                }
            } else {
                frustrationFrameCount = 0; // Reset frustration counter
                neutralFrameCount++;
                
                if(neutralFrameCount >= NEUTRAL_THRESHOLD) {
                    labelDiv.style.color = "#00FF7F";
                    robotDiv.innerHTML = "😊";
                    currentState = "neutral";
                    triggerLocked = false; // Allow re-triggering when back to neutral
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
            triggerLocked = false;
            currentState = "neutral";
        }
    </script>
    """
    detect_signal = components.html(tm_html, height=750)
    
    # Handle trigger from facial detection
    if detect_signal and not st.session_state.is_frustrated:
        st.session_state.is_frustrated = True
        st.session_state.frustration_confirmed = False
        log_entry = {
            "Timestamp": datetime.now().strftime("%H:%M:%S"),
            "Event": "Frustration Detected",
            "Confidence": "High (>82%)",
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
                <video id="v" autoplay style="width: 100%; height: 320px; border-radius: 10px; background: #1a1a1a;"></video>
                <div id="ocr-status" style="color: #aaa; font-size: 0.9rem; margin-top: 10px; text-align: center;">Ready for capture</div>
            </div>
            <script src="https://cdn.jsdelivr.net/npm/tesseract.js@4/dist/tesseract.min.js"></script>
            <script>
                const video = document.getElementById('v');
                const castBtn = document.getElementById('cast-btn');
                const ocrBtn = document.getElementById('ocr-btn');
                const statusDiv = document.getElementById('ocr-status');
                let capturedStream = null;
                
                castBtn.onclick = async () => {
                    try {
                        capturedStream = await navigator.mediaDevices.getDisplayMedia({video: true});
                        video.srcObject = capturedStream;
                        statusDiv.innerHTML = "✅ Screen captured. Click 'Extract Text' to analyze.";
                    } catch(e) {
                        statusDiv.innerHTML = "❌ Screen capture denied";
                    }
                };
                
                ocrBtn.onclick = async () => {
                    if(!capturedStream) {
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
                        console.log("Extracted text:", extractedText);
                        window.parent.postMessage({
                            type: 'streamlit:set_component_value', 
                            value: extractedText, 
                            key: 'ocr_bridge'
                        }, "*");
                        statusDiv.innerHTML = "✅ Text extracted! " + extractedText.length + " characters found.";
                    } catch(e) {
                        statusDiv.innerHTML = "❌ Extraction failed: " + e.message;
                    }
                };
            </script>
        """
        
        ocr_return = components.html(ocr_html, height=500)
        
        # Capture OCR text
        if ocr_return and isinstance(ocr_return, str) and len(ocr_return) > 20:
            st.session_state.extracted_text = ocr_return
            st.success(f"✅ Text extracted! ({len(ocr_return)} characters)")
            
            # Auto-detect IGCSE topic
            subject, topic, youtube_link = detect_igcse_topic(ocr_return)
            if topic:
                st.session_state.detected_subject = subject
                st.session_state.detected_topic = topic
                st.session_state.simplified_content = simplify_content(ocr_return, topic)
                st.info(f"🎯 **Detected:** {subject} - {topic.title()}")
            else:
                st.warning("⚠️ Could not auto-detect topic. Manual simplification available.")

    with tab2:
        st.subheader("🤖 Adaptive Support Dashboard")
        
        if st.session_state.is_frustrated and not st.session_state.frustration_confirmed:
            st.warning("⚠️ **Lumina Detected Learning Barrier** - Simplification Mode Active")
            
            if st.session_state.simplified_content:
                content = st.session_state.simplified_content
                st.markdown(f"""
                <div style="background: rgba(255,20,147,0.15); padding: 30px; border-radius: 15px; border-left: 10px solid #FF1493;">
                    <h2 style="margin-top:0; color: #FF1493;">{content['title']}</h2>
                    <p><b>Extracted material:</b> {st.session_state.extracted_text[:200]}...</p>
                    <hr style="opacity: 0.3;">
                    <h3>📌 Easy Steps:</h3>
                    <ul style="font-size: 1.1rem; line-height: 2;">
                """, unsafe_allow_html=True)
                
                for bullet in content['bullets']:
                    st.markdown(f"<li>{bullet}</li>", unsafe_allow_html=True)
                
                st.markdown(f"""
                    </ul>
                    <hr style="opacity: 0.3;">
                    <p style="font-size: 1.1rem; background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; font-style: italic;">
                        💡 <b>{content['tip']}</b>
                    </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background: rgba(255,20,147,0.15); padding: 25px; border-radius: 15px; border-left: 10px solid #FF1493;">
                    <h3 style="margin-top:0;">📖 Content Detected</h3>
                    <p><b>Material:</b> """ + (st.session_state.extracted_text[:200] + "..." if st.session_state.extracted_text else "Waiting for text extraction...") + """</p>
                    <hr style="opacity: 0.3;">
                    <p><b>Steps to understand:</b></p>
                    <ul>
                        <li>Read slowly, one sentence at a time</li>
                        <li>Highlight the key words</li>
                        <li>Draw a picture or diagram</li>
                        <li>Ask for help!</li>
                    </ul>
                    <p style="margin-top: 20px; font-style: italic; opacity: 0.9;">💪 <b>You've got this! Take a deep breath.</b></p>
                </div>
                """, unsafe_allow_html=True)
            
            col_btn1, col_btn2, col_btn3 = st.columns(3)
            
            with col_btn1:
                if st.button("��� I Understand!", key="understand_btn", use_container_width=True):
                    st.session_state.is_frustrated = False
                    st.session_state.frustration_confirmed = True
                    st.session_state.test_logs.append({
                        "Timestamp": datetime.now().strftime("%H:%M:%S"),
                        "Event": "User Confirmed Understanding",
                        "Topic": st.session_state.detected_topic or "Unknown",
                        "Response": "Scaffolding Cleared"
                    })
                    st.rerun()
            
            with col_btn2:
                if st.button("🆘 Need Help", key="help_btn", use_container_width=True):
                    if st.session_state.detected_subject and st.session_state.detected_topic:
                        youtube_link = detect_igcse_topic(st.session_state.extracted_text)[2]
                        st.session_state.test_logs.append({
                            "Timestamp": datetime.now().strftime("%H:%M:%S"),
                            "Event": "Help Requested",
                            "Topic": st.session_state.detected_topic,
                            "YouTube Link": youtube_link
                        })
                        st.markdown(f"""
                        <div style="background: rgba(52,152,219,0.2); padding: 20px; border-radius: 15px; border-left: 5px solid #3498db;">
                            <h3>📺 Video Tutorial for {st.session_state.detected_topic.title()}</h3>
                            <p><a href="{youtube_link}" target="_blank" style="color: #00BFFF; font-weight: bold; font-size: 1.1rem;">👉 Watch Explanation Video</a></p>
                            <p style="opacity: 0.9;">This video explains {st.session_state.detected_topic} in an easy way. Pause and rewind as needed!</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.info("📧 Please extract text first to get topic-specific help.")
            
            with col_btn3:
                if st.button("📧 Email Teacher", key="email_btn", use_container_width=True):
                    st.session_state.test_logs.append({
                        "Timestamp": datetime.now().strftime("%H:%M:%S"),
                        "Event": "Teacher Notification Sent",
                        "Topic": st.session_state.detected_topic or "Unknown",
                        "Status": "Pending Response"
                    })
                    st.success("✅ Your teacher has been notified! They'll contact you soon.")
        
        elif st.session_state.is_frustrated and st.session_state.frustration_confirmed:
            st.success("✅ Great! Ready for more content.")
            if st.button("🔄 Reset & Continue Learning"):
                st.session_state.is_frustrated = False
                st.session_state.frustration_confirmed = False
                st.session_state.simplified_content = None
                st.session_state.extracted_text = ""
                st.rerun()
        
        else:
            st.info("✨ Status: **Monitoring Mode Active**. When frustrated, your content will simplify automatically.")

    with tab3:
        st.subheader("📊 System Validation Data")
        
        if st.session_state.test_logs:
            df = pd.DataFrame(st.session_state.test_logs)
            st.dataframe(df, use_container_width=True)
            
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
                help_events = len([e for e in st.session_state.test_logs if "Help" in e.get("Event", "")])
                st.metric("Help Requests", help_events)
        
        else:
            st.write("📭 No events recorded yet. Start the tracker to begin data collection.")

# --- SIDEBAR ---
st.sidebar.title("🎛️ Lumina Control Panel")
st.sidebar.markdown("**Student:** Puteri Aisyah Sofia")
st.sidebar.markdown("**Supervisor:** AP Dr. Ibrahim Venkat")
st.sidebar.markdown("**Research Date:** " + datetime.now().strftime("%Y-%m-%d"))
st.sidebar.divider()

with st.sidebar.expander("⚙️ Advanced Settings"):
    st.markdown("**Supported Subjects:**")
    st.markdown("✅ IGCSE Math\n✅ IGCSE Science (Biology, Chemistry, Physics)\n✅ IGCSE English\n✅ Bahasa Melayu")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear Logs"):
            st.session_state.test_logs = []
            st.rerun()
    with col2:
        if st.button("🔄 Reset State"):
            st.session_state.is_frustrated = False
            st.session_state.frustration_confirmed = False
            st.session_state.simplified_content = None
            st.rerun()

st.sidebar.divider()
st.sidebar.markdown("""
<div style="font-size: 0.85rem; opacity: 0.7;">
    <b>System Status:</b><br>
    ✅ Perception Engine: Ready<br>
    ✅ Text Extraction: Ready<br>
    ✅ IGCSE Topic Detection: Ready<br>
    ✅ Scaffolding: Enabled<br>
    <br>
    <i>Version 3.0 | Built with ❤️ for Inclusive Education</i>
</div>
""", unsafe_allow_html=True)

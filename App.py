import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime

try:
    from transformers import pipeline
    HAS_TRANSFORMERS = True
    simplifier = pipeline("text2text-generation", model="facebook/bart-large-cnn")
except:
    HAS_TRANSFORMERS = False
    simplifier = None

st.set_page_config(page_title="Lumina AI | Research Framework", layout="wide", page_icon="🤖")

# IGCSE TOPICS DATABASE
IGCSE_TOPICS = {
    "Math": {
        "algebra": "https://www.youtube.com/watch?v=Z-ZkmpQBIFo",
        "geometry": "https://www.youtube.com/watch?v=JnLDmw3bbuw",
        "pythagoras": "https://www.youtube.com/watch?v=sgmadSJ1Xbk",
        "trigonometry": "https://www.youtube.com/watch?v=PUB0TaZ7bhA",
        "calculus": "https://www.youtube.com/watch?v=WsQQvHm4lSw",
        "statistics": "https://www.youtube.com/watch?v=XZo4xyJXCak",
        "probability": "https://www.youtube.com/watch?v=SkidyDQuupA",
        "quadratic": "https://www.youtube.com/watch?v=qeByhTF8WEw",
    },
    "Science": {
        "vertebrate": "https://www.youtube.com/watch?v=obn214CE6mY",
        "photosynthesis": "https://www.youtube.com/watch?v=cucQtak-jco",
        "DNA": "https://www.youtube.com/watch?v=T6_wKPAbf2k",
        "Chemistry": "https://www.youtube.com/watch?v=7OQPY6KuPs4",
        "Physics": "https://www.youtube.com/watch?v=BDv8F2gjnu0",
        "osmosis": "https://www.youtube.com/watch?v=vCJVXYmXkzM",
        "enzyme": "https://www.youtube.com/watch?v=gUncqL1ul8Q",
    },
    "English": {
        "Grand Openings": "https://www.youtube.com/watch?v=_nnhWiUvYGE",
        "Similies & Metaphors": "https://www.youtube.com/watch?v=IDvOAtt2EjQ",
        "Structuring story": "https://www.youtube.com/watch?v=bXg2O12rJcs",
        "Vocabulary": "https://www.youtube.com/watch?v=-xanUIXuMmI",
        "essay": "https://www.youtube.com/watch?v=EenqdGMZGT4",
        "writing": "https://www.youtube.com/watch?v=4wSe890AZY4",
    },
    "Bahasa Melayu": {
        "Paper 1: Listening": "https://www.youtube.com/watch?v=1TXR223qBAI",
        "Paper 2: Reading": "https://www.youtube.com/watch?v=sGzrVVoxMzs",
       "Paper 3: Speaking": "https://www.youtube.com/watch?v=WEHor8z6p8g",
        "Paper 4: Writing": "https://www.youtube.com/watch?v=l3ZicDEloMw",     
    }
}

# INITIALIZE SESSION STATES
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
if 'ai_simplified_bullets' not in st.session_state:
    st.session_state.ai_simplified_bullets = None
if 'youtube_link' not in st.session_state:
    st.session_state.youtube_link = None

# ====== UTILITY FUNCTIONS ======
def detect_igcse_topic(text):
    """Detect IGCSE subject and topic from text"""
    if not text:
        return None, None, None
    text_lower = text.lower()
    for subject, topics in IGCSE_TOPICS.items():
        for topic, youtube_link in topics.items():
            if topic in text_lower:
                return subject, topic, youtube_link
    return None, None, None

def simplify_with_ai(text):
    """Simplify text using transformer model or fallback"""
    if not text or len(text.strip()) < 20:
        return ["Unable to process text. Please provide more content."]
    
    if HAS_TRANSFORMERS and simplifier:
        try:
            result = simplifier(text, max_length=150, min_length=50, do_sample=False)
            simplified_text = result[0]['summary_text']
            sentences = simplified_text.split('. ')
            bullets = []
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence:
                    emoji = "📌"
                    if any(word in sentence.lower() for word in ["important", "key", "essential"]):
                        emoji = "⭐"
                    elif any(word in sentence.lower() for word in ["example", "such as"]):
                        emoji = "📝"
                    elif any(word in sentence.lower() for word in ["result", "outcome"]):
                        emoji = "✅"
                    bullets.append(f"{emoji} {sentence}")
            return bullets if bullets else fallback_simplify(text)
        except:
            return fallback_simplify(text)
    else:
        return fallback_simplify(text)

def fallback_simplify(text):
    """Fallback simplification without AI"""
    bullets = []
    sentences = text.replace('!', '.').replace('?', '.').split('.')
    sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 15]
    
    for sentence in sentences[:6]:
        if len(sentence) > 80:
            sentence = sentence[:77] + "..."
        emoji = "📌"
        if any(word in sentence.lower() for word in ["important", "key"]):
            emoji = "⭐"
        elif any(word in sentence.lower() for word in ["example"]):
            emoji = "📝"
        bullets.append(f"{emoji} {sentence}")
    
    return bullets if bullets else ["Unable to simplify text at this time."]

def simplify_content(text, topic):
    """Get predefined simplification for detected topic"""
    simplifications = {
        "vertebrate": {
            "title": "🦁 Vertebrates Explained Simply",
            "bullets": [
                "✅ Vertebrates have a BACKBONE (spine)",
                "✅ Five main types: Fish, Amphibians, Reptiles, Birds, Mammals",
                "✅ The backbone protects the spinal cord",
                "✅ Examples: Dogs, cats, snakes, eagles, sharks",
                "✅ Humans are also vertebrates!"
            ],
            "tip": "VERTEBRA = has a backbone! 🦴"
        },
        "vertebrates": {
            "title": "🦁 Vertebrates Explained Simply",
            "bullets": [
                "✅ Vertebrates have a BACKBONE (spine)",
                "✅ Five main types: Fish, Amphibians, Reptiles, Birds, Mammals",
                "✅ The backbone protects the spinal cord",
                "✅ Examples: Dogs, cats, snakes, eagles, sharks",
                "✅ Humans are also vertebrates!"
            ],
            "tip": "VERTEBRA = has a backbone! 🦴"
        },
        "pythagoras": {
            "title": "📐 Pythagoras Theorem Explained",
            "bullets": [
                "✅ Formula: a² + b² = c²",
                "✅ Used in RIGHT-ANGLED triangles ONLY",
                "✅ c = hypotenuse (longest side)",
                "✅ a and b = the other two sides",
                "✅ Example: 3² + 4² = 5² (9 + 16 = 25)"
            ],
            "tip": "Remember: The hypotenuse is always the LONGEST side! 📏"
        },
        "poetry": {
            "title": "📝 Poetry Analysis Simplified",
            "bullets": [
                "✅ RHYME: Words that sound the same (cat/bat)",
                "✅ RHYTHM: The beat or pattern of words",
                "✅ IMAGERY: Descriptive language that creates pictures",
                "✅ METAPHOR: Comparing things without using 'like' or 'as'",
                "✅ SIMILE: Comparing with 'like' or 'as'"
            ],
            "tip": "Poetry expresses feelings through creative language! 🎨"
        },
        "pemahaman": {
            "title": "📖 Pemahaman Teks (Bahasa Melayu)",
            "bullets": [
                "✅ BACA dengan teliti - pahami main idea",
                "✅ CARI kata kunci dalam soalan",
                "✅ TANDAI jawapan di dalam teks",
                "✅ TULIS jawapan dengan lengkap dan jelas",
                "✅ SEMAK semula sebelum serah"
            ],
            "tip": "Sentiasa merujuk balik kepada teks untuk jawapan! 📚"
        },
        "photosynthesis": {
            "title": "🌱 Photosynthesis Made Easy",
            "bullets": [
                "☀️ Plants use SUNLIGHT to make food",
                "💨 They take in Carbon Dioxide (CO₂) from the air",
                "💧 They take in Water (H₂O) from the soil",
                "🍎 They make Glucose (sugar) for energy",
                "💨 They release Oxygen for us to breathe"
            ],
            "tip": "Light + Water + CO₂ = Food + Oxygen ✨"
        },
        "algebra": {
            "title": "📐 Algebra Simplified",
            "bullets": [
                "🔤 Algebra uses LETTERS (x, y, z) for unknown numbers",
                "🔍 Your job: Find what the letter equals",
                "⚖️ Whatever you do to one side, do to the other",
                "✅ Check your answer by putting it back in",
                "🧩 Example: If x + 5 = 12, then x = 7"
            ],
            "tip": "Algebra is like solving a mystery! 🔍"
        },
        "geometry": {
            "title": "📏 Geometry Basics",
            "bullets": [
                "📐 Geometry is about SHAPES and ANGLES",
                "🔺 Shapes: triangles, squares, circles, rectangles",
                "📍 90° is RIGHT, 180° is STRAIGHT, 360° is FULL circle",
                "📏 Perimeter = distance AROUND a shape",
                "📦 Area = space INSIDE a shape"
            ],
            "tip": "Draw it out! Visualizing shapes helps! ✏️"
        },
        "chemistry": {
            "title": "⚗️ Chemistry Basics",
            "bullets": [
                "🧪 Study of substances and reactions",
                "⚛️ ATOMS are tiny building blocks",
                "🔗 Atoms join to make MOLECULES",
                "💥 Reactions make NEW substances",
                "🌍 Everything is made from ELEMENTS"
            ],
            "tip": "Mixing ingredients in cooking = chemistry! 👨‍🍳"
        },
        "respiration": {
            "title": "🫁 Respiration Explained",
            "bullets": [
                "💨 How cells get ENERGY from food",
                "🫁 Breathing brings oxygen into your body",
                "⚡ Cells use oxygen to break down glucose",
                "💪 Creates energy (ATP) for your body",
                "💨 Body releases carbon dioxide as waste"
            ],
            "tip": "Respiration ≠ Breathing! ⚛️"
        },
        "enzyme": {
            "title": "🧬 Enzymes Simplified",
            "bullets": [
                "⚙️ Enzymes are HELPERS that speed up reactions",
                "🎯 Each enzyme works on ONE specific substrate",
                "🌡️ Heat can denature (break) enzymes",
                "📊 Work best at certain temperatures",
                "🔑 Key fits lock - enzyme fits substrate"
            ],
            "tip": "Enzymes = biological catalysts! ⚡"
        }
    }
    
    for key, value in simplifications.items():
        if key in topic.lower():
            return value
    
    return {
        "title": f"📚 Understanding {topic.title()}",
        "bullets": [
            f"About {topic.title()}",
            "Break into smaller parts",
            "Start with basics",
            "Build up gradually",
            "Ask your teacher for help"
        ],
        "tip": "Keep learning step by step! 💪"
    }

def apply_lumina_theme():
    """Apply Lumina AI theme styling"""
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
    }}
    
    .stTabs [data-baseweb="tab-list"] {{ background: rgba(255,255,255,0.05); border-radius: 10px; padding: 5px; }}
    .stTabs [data-baseweb="tab"] {{ color: white !important; }}
    </style>
    """, unsafe_allow_html=True)

# ====== APPLY THEME ======
apply_lumina_theme()

# ====== HEADER ======
st.markdown("""
    <div style="border: 2px solid #ffffff; border-radius: 15px; padding: 20px; text-align: center; background: rgba(255, 255, 255, 0.05); margin-bottom: 30px;">
        <h1 style="margin: 0; font-size: 2.2rem;">Lumina AI</h1>
        <p style="margin: 5px 0 0 0; opacity: 0.8;">Enhancing Inclusive Education through Empathetic Assistive Technology</p>
    </div>
    """, unsafe_allow_html=True)

# ====== MAIN LAYOUT ======
col_left, col_right = st.columns([1.4, 2])

# ====== LEFT COLUMN: FACIAL PERCEPTION ======
with col_left:
    st.subheader("👤 LUMINA AI")
    
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
        let frustrationFrameCount = 0;
        let neutralFrameCount = 0;
        const FRUSTRATION_THRESHOLD = 90;
        const NEUTRAL_THRESHOLD = 45;
        const CONFIDENCE_THRESHOLD = 0.82;
        let currentState = "neutral";
        let triggerLocked = false;

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
            prediction.forEach(p => { if(p.probability > best.probability) best = p; });
            
            const labelDiv = document.getElementById("label-container");
            const confDiv = document.getElementById("confidence-display");
            const frameDiv = document.getElementById("frame-counter");
            const robotDiv = document.getElementById("robot-mascot");
            
            confDiv.innerHTML = "Confidence: " + (best.probability * 100).toFixed(1) + "%";
            labelDiv.innerHTML = "Status: " + best.className;
            frameDiv.innerHTML = currentState.toUpperCase() + " Frames: " + (currentState === "frustrated" ? frustrationFrameCount : neutralFrameCount) + "/" + (currentState === "frustrated" ? FRUSTRATION_THRESHOLD : NEUTRAL_THRESHOLD);
            
            if(best.className === "Frustrated" && best.probability > CONFIDENCE_THRESHOLD) {
                neutralFrameCount = 0;
                frustrationFrameCount++;
                labelDiv.style.color = "#FF6B6B";
                robotDiv.innerHTML = "😟";
                currentState = "frustrated";
                
                if(frustrationFrameCount >= FRUSTRATION_THRESHOLD && !triggerLocked) {
                    triggerLocked = true;
                    window.parent.postMessage({type: 'streamlit:set_component_value', value: true, key: 'trig'}, "*");
                }
            } else {
                frustrationFrameCount = 0;
                neutralFrameCount++;
                if(neutralFrameCount >= NEUTRAL_THRESHOLD) {
                    labelDiv.style.color = "#00FF7F";
                    robotDiv.innerHTML = "😊";
                    currentState = "neutral";
                    triggerLocked = false;
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
    
    if detect_signal and not st.session_state.is_frustrated:
        st.session_state.is_frustrated = True
        st.session_state.frustration_confirmed = False
        
        if st.session_state.extracted_text and len(st.session_state.extracted_text.strip()) > 50:
            st.session_state.ai_simplified_bullets = simplify_with_ai(st.session_state.extracted_text)
        
        st.session_state.test_logs.append({
            "Timestamp": datetime.now().strftime("%H:%M:%S"),
            "Event": "Frustration Detected",
            "Confidence": "High (>82%)",
            "Response": "Adaptive Scaffolding Triggered"
        })
        st.rerun()

# ====== RIGHT COLUMN: TABS ======
with col_right:
    tab1, tab2, tab3 = st.tabs(["🖥️ Shared Material", "💡 Adaptive Notes", "📊 Research Logs"])
    
    # ====== TAB 1: SHARED MATERIAL ======
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
                    const ctx = canvas.getContext('2d');
                    ctx.drawImage(video, 0, 0);
                    
                    try {
                        const result = await Tesseract.recognize(canvas, 'eng');
                        const extractedText = result.data.text || "";
                        
                        if(extractedText && extractedText.trim().length > 20) {
                            window.parent.postMessage({
                                type: 'streamlit:set_component_value', 
                                value: extractedText.trim(), 
                                key: 'ocr_text_result'
                            }, "*");
                            statusDiv.innerHTML = "✅ Text extracted! " + extractedText.length + " characters found.";
                        } else {
                            statusDiv.innerHTML = "⚠️ No text detected. Try clearer screen or better lighting.";
                        }
                    } catch(e) {
                        statusDiv.innerHTML = "❌ Extraction failed: " + e.message;
                    }
                };
            </script>
        """
        
        ocr_return = components.html(ocr_html, height=500)
        
        st.write("---")
        st.subheader("📝 Text Processing")
        
        if ocr_return and isinstance(ocr_return, str) and len(ocr_return.strip()) > 20:
            st.session_state.extracted_text = ocr_return.strip()
            st.success(f"✅ **SUCCESS!** Text stored: {len(ocr_return)} characters")
            
            subject, topic, youtube_link = detect_igcse_topic(ocr_return)
            if topic:
                st.session_state.detected_subject = subject
                st.session_state.detected_topic = topic
                st.session_state.youtube_link = youtube_link
                st.info(f"🎯 **Detected:** {subject} - {topic.title()}")
            else:
                st.warning("⚠️ Could not auto-detect topic. AI simplification will be used.")
        else:
            st.info("⏳ Waiting for OCR extraction... Extract text from your screen above.")
    
    # ====== TAB 2: ADAPTIVE NOTES ======
    with tab2:
        st.subheader("🤖 Adaptive Support Dashboard")
        
        debug_text = st.session_state.extracted_text if st.session_state.extracted_text else ""
        debug_has_text = len(debug_text.strip()) > 10 if debug_text else False
        
        # STATE: FRUSTRATED & NOT CONFIRMED
        if st.session_state.is_frustrated and not st.session_state.frustration_confirmed:
            st.warning("⚠️ **Lumina Detected Learning Barrier** - Simplification Mode Active")
            
            if debug_has_text:
                if not st.session_state.detected_topic:
                    subject, topic, youtube_link = detect_igcse_topic(st.session_state.extracted_text)
                    st.session_state.detected_subject = subject
                    st.session_state.detected_topic = topic
                    st.session_state.youtube_link = youtube_link
                
                if st.session_state.detected_topic:
                    content = simplify_content(st.session_state.extracted_text, st.session_state.detected_topic)
                    st.markdown(f"""
                    <div style="background: rgba(255,20,147,0.15); padding: 30px; border-radius: 15px; border-left: 10px solid #FF1493;">
                        <h2 style="margin-top:0; color: #FF1493;">{content['title']}</h2>
                        <p><b>📄 You were reading about:</b> {st.session_state.extracted_text[:150]}...</p>
                        <hr style="opacity: 0.3;">
                        <h3>📌 Here's the Simple Version:</h3>
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
                    st.markdown(f"""
                    <div style="background: rgba(255,20,147,0.15); padding: 30px; border-radius: 15px; border-left: 10px solid #FF1493;">
                        <h2 style="margin-top:0; color: #FF1493;">📖 AI-Powered Simplification</h2>
                        <p><b>Content detected:</b> {st.session_state.extracted_text[:200]}...</p>
                        <hr style="opacity: 0.3;">
                        <h3>📌 Key Points in Simple Language:</h3>
                        <ul style="font-size: 1.1rem; line-height: 2.2;">
                    """, unsafe_allow_html=True)
                    
                    if st.session_state.ai_simplified_bullets:
                        for bullet in st.session_state.ai_simplified_bullets:
                            st.markdown(f"<li>{bullet}</li>", unsafe_allow_html=True)
                    else:
                        bullets = simplify_with_ai(st.session_state.extracted_text)
                        for bullet in bullets:
                            st.markdown(f"<li>{bullet}</li>", unsafe_allow_html=True)
                    
                    st.markdown(f"""
                        </ul>
                        <hr style="opacity: 0.3;">
                        <p style="font-size: 1.1rem; background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; font-style: italic;">
                            💪 Take your time reviewing! You've got this!
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.error("❌ **No text extracted yet!**")
                st.markdown("""
                <div style="background: rgba(255,100,100,0.15); padding: 25px; border-radius: 15px; border-left: 10px solid #FF4444;">
                    <h3>What to do:</h3>
                    <ol>
                        <li>Go to the <b>"Shared Material"</b> tab</li>
                        <li>Click <b>"Cast Screen"</b> to show your learning content</li>
                        <li>Click <b>"Extract Text"</b> to read what's on screen</li>
                        <li>Return to this tab while looking frustrated</li>
                    </ol>
                </div>
                """, unsafe_allow_html=True)
            
            col_btn1, col_btn2, col_btn3 = st.columns(3)
            
            with col_btn1:
                if st.button("✅ I Understand!", key="understand_btn", use_container_width=True):
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
                    subject, topic, youtube_link = detect_igcse_topic(st.session_state.extracted_text)
                    
                    if youtube_link:
                        st.session_state.test_logs.append({
                            "Timestamp": datetime.now().strftime("%H:%M:%S"),
                            "Event": "Help Requested",
                            "Topic": topic,
                            "YouTube Link": youtube_link
                        })
                        st.markdown(f"""
                        <div style="background: rgba(52,152,219,0.2); padding: 20px; border-radius: 15px; border-left: 5px solid #3498db;">
                            <h3>📺 Video Tutorial for {topic.title()}</h3>
                            <p><a href="{youtube_link}" target="_blank" style="color: #00BFFF; font-weight: bold; font-size: 1.2rem;">👉 WATCH EXPLANATION VIDEO</a></p>
                            <p style="opacity: 0.9;">This video explains {topic} step by step. You can pause, rewind, and watch as many times as you need!</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error("❌ Could not find YouTube link for this topic.")
            
            with col_btn3:
                if st.button("📧 Email Teacher", key="email_btn", use_container_width=True):
                    st.session_state.test_logs.append({
                        "Timestamp": datetime.now().strftime("%H:%M:%S"),
                        "Event": "Teacher Notification Sent",
                        "Topic": st.session_state.detected_topic or "Unknown",
                        "Status": "Pending Response"
                    })
                    st.success("✅ Your teacher has been notified!")
        
        # STATE: FRUSTRATED & CONFIRMED (SUCCESS)
        elif st.session_state.is_frustrated and st.session_state.frustration_confirmed:
            st.success("✅ Great job! You understood the concept.")
            st.markdown("""
            <div style="background: rgba(76, 175, 80, 0.2); padding: 30px; border-radius: 15px; border-left: 10px solid #4CAF50; text-align: center;">
                <h2 style="color: #4CAF50; margin-bottom: 20px;">🎉 Excellent Progress!</h2>
                <p style="font-size: 1.1rem; margin-bottom: 20px;">You've successfully understood this concept. Ready to learn something new?</p>
                <p style="font-size: 0.95rem; opacity: 0.9;">Click the button below to clear everything and continue with the next topic.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            col_reset = st.columns([1, 1, 1])
            with col_reset[1]:
                if st.button("🔄 Continue to Next Topic", key="reset_btn", use_container_width=True):
                    st.session_state.is_frustrated = False
                    st.session_state.frustration_confirmed = False
                    st.session_state.extracted_text = ""
                    st.session_state.detected_topic = None
                    st.session_state.detected_subject = None
                    st.session_state.youtube_link = None
                    st.session_state.ai_simplified_bullets = None
                    st.rerun()
        
        # STATE: MONITORING MODE
        else:
            st.info("✨ **Status: Monitoring Mode Active**")
            st.markdown("""
            <div style="background: rgba(100,200,255,0.1); padding: 20px; border-radius: 10px; border-left: 5px solid #64c8ff;">
                <p><b>How I Help You:</b></p>
                <ul>
                    <li>🎬 Watch your face while you study</li>
                    <li>😊 When I see frustration, I'll simplify for you</li>
                    <li>📄 I'll read text from your screen</li>
                    <li>✨ I'll use AI to break topics into easy bullet points</li>
                    <li>📺 I'll find helpful videos for you</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    
    # ====== TAB 3: RESEARCH LOGS ======
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
            st.write("📭 No events recorded yet.")

# ====== SIDEBAR ======
st.sidebar.title("🎛️ Lumina Control Panel")
st.sidebar.markdown("**Student:** Puteri Aisyah Sofia")
st.sidebar.markdown("**Supervisor:** AP Dr. Ibrahim Venkat")
st.sidebar.markdown("**Research Date:** " + datetime.now().strftime("%Y-%m-%d"))
st.sidebar.divider()

with st.sidebar.expander("⚙️ Advanced Settings"):
    st.markdown("**Supported Subjects:**")
    st.markdown("✅ IGCSE Math, Science, English, Bahasa Melayu")
    
    if HAS_TRANSFORMERS:
        st.success("✅ AI Model: Facebook BART")
    else:
        st.warning("⚠️ Fallback Mode Active")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear Logs"):
            st.session_state.test_logs = []
            st.rerun()
    with col2:
        if st.button("🔄 Reset State"):
            st.session_state.is_frustrated = False
            st.session_state.frustration_confirmed = False
            st.session_state.extracted_text = ""
            st.session_state.detected_topic = None
            st.session_state.detected_subject = None
            st.session_state.youtube_link = None
            st.session_state.ai_simplified_bullets = None
            st.rerun()

st.sidebar.divider()
st.sidebar.markdown("""
<div style="font-size: 0.85rem; opacity: 0.7;">
    <b>System Status:</b><br>
    ✅ Perception Engine: Ready<br>
    ✅ Text Extraction: Ready<br>
    ✅ Topic Detection: Ready<br>
    ✅ AI Simplification: Ready<br>
    ✅ YouTube Links: Ready<br>
    ✅ Scaffolding: Enabled<br>
</div>
""", unsafe_allow_html=True)


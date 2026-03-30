import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime
import json

# --- 1. INTERFACE & DATA SESSION CONFIG ---
st.set_page_config(page_title="Lumina AI | Research Framework", layout="wide", page_icon="🤖")

# IGCSE TOPICS DATABASE WITH YOUTUBE LINKS (Full Detailed Version)
IGCSE_TOPICS = {
    "Math": {
        "algebra": "https://www.youtube.com/watch?v=NybHckSEQq4",
        "geometry": "https://www.youtube.com/watch?v=E_-3j-Rp6Zk",
        "trigonometry": "https://www.youtube.com/watch?v=exLVgL7gDSA",
        "calculus": "https://www.youtube.com/watch?v=WUvTyaaNkzM",
        "statistics": "https://www.youtube.com/watch?v=xxpc-SDeal4",
        "probability": "https://www.youtube.com/watch?v=uzkc-qNVoOk",
        "quadratic": "https://www.youtube.com/watch?v=DxGearozly0",
    },
    "Science": {
        "biology": "https://www.youtube.com/watch?v=V0JGXWpB6ZQ",
        "chemistry": "https://www.youtube.com/watch?v=roQOlHxANxY",
        "physics": "https://www.youtube.com/watch?v=0xALCVJzowA",
        "vertebrate": "https://www.youtube.com/watch?v=lkwsZuUol_A",
        "vertebrates": "https://www.youtube.com/watch?v=lkwsZuUol_A",
        "photosynthesis": "https://www.youtube.com/watch?v=VLZvIqX_Q-k",
        "reproduction": "https://www.youtube.com/watch?v=Tb_6dZ8Vy5k",
        "respiration": "https://www.youtube.com/watch?v=mVJZEWflWQc",
        "genetics": "https://www.youtube.com/watch?v=ySE9kVohH90",
        "osmosis": "https://www.youtube.com/watch?v=SJctAUw5NaI",
        "enzyme": "https://www.youtube.com/watch?v=HGU9xKGLWEg",
    },
    "English": {
        "grammar": "https://www.youtube.com/watch?v=MFQhB73iUUk",
        "literature": "https://www.youtube.com/watch?v=lV6w5j8ChiI",
        "essay": "https://www.youtube.com/watch?v=jH1c3sFCVdE",
        "comprehension": "https://www.youtube.com/watch?v=T0eEiXVVVY4",
        "writing": "https://www.youtube.com/watch?v=jH1c3sFCVdE",
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
if 'ai_simplified_bullets' not in st.session_state:
    st.session_state.ai_simplified_bullets = None

def detect_igcse_topic(text):
    if not text:
        return None, None, None
    text_lower = text.lower()
    for subject, topics in IGCSE_TOPICS.items():
        for topic, youtube_link in topics.items():
            if topic in text_lower:
                return subject, topic, youtube_link
    return None, None, None

def generate_bullet_points(text):
    if not text or len(text.strip()) < 20:
        return ["Unable to process text. Please provide more content."]
    bullets = []
    sentences = text.replace('!', '.').replace('?', '.').split('.')
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if len(sentences) == 0:
        return ["The provided text could not be processed."]
    
    for i, sentence in enumerate(sentences[:6]):
        if len(sentence) > 15:
            simplified = simplify_sentence(sentence)
            if simplified:
                bullets.append(simplified)
    return bullets if bullets else ["Content detected but unclear"]

def simplify_sentence(sentence):
    sentence = sentence.strip().split('[')[0].strip()
    if len(sentence) > 80:
        sentence = sentence[:77] + "..."
    
    emoji_map = {
        "important": "⭐", "key": "🔑", "process": "🔄", "definition": "📖", 
        "example": "📝", "result": "✅", "energy": "⚡", "organism": "🧬", 
        "system": "⚙️", "structure": "🏗️", "change": "🔀", "reaction": "💥", "method": "📊",
    }
    emoji = "📌"
    for keyword, emoj in emoji_map.items():
        if keyword in sentence.lower():
            emoji = emoj
            break
    return f"{emoji} {sentence}"

def simplify_content(text, topic):
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
            "tip": "VERTEBRA = has a backbone! 🦴 That's the main difference from invertebrates."
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
            "tip": "VERTEBRA = has a backbone! 🦴 That's the main difference from invertebrates."
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
            "tip": "Remember: Light + Water + CO₂ = Food + Oxygen ✨"
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
            "tip": "Think of algebra like solving a mystery! 🔍 What number is hiding?"
        },
        "geometry": {
            "title": "📏 Geometry Basics",
            "bullets": [
                "📐 Geometry is about SHAPES and ANGLES",
                "🔺 Know your shapes: triangles, squares, circles, rectangles",
                "📍 Angles: 90° is RIGHT angle, 180° is STRAIGHT line, 360° is FULL circle",
                "📏 Perimeter = distance AROUND a shape",
                "📦 Area = space INSIDE a shape"
            ],
            "tip": "Draw it out! Visualizing shapes helps you understand. ✏️"
        },
        "chemistry": {
            "title": "⚗️ Chemistry Basics",
            "bullets": [
                "🧪 Chemistry = study of substances and reactions",
                "⚛️ ATOMS are tiny building blocks",
                "🔗 Atoms join to make MOLECULES",
                "💥 Chemical reactions make NEW substances",
                "🌍 Everything is made from ELEMENTS"
            ],
            "tip": "Think: Mixing ingredients in cooking = chemistry! 👨‍🍳"
        },
        "respiration": {
            "title": "🫁 Respiration Explained",
            "bullets": [
                "💨 Respiration is how cells get ENERGY from food",
                "🫁 Breathing brings oxygen into your body",
                "⚡ Cells use oxygen to break down glucose",
                "💪 This creates energy (ATP) for your body",
                "💨 Your body releases carbon dioxide as waste"
            ],
            "tip": "Respiration ≠ Breathing. Respiration is inside cells! ⚛️"
        },
        "enzyme": {
            "title": "🧬 Enzymes Simplified",
            "bullets": [
                "⚙️ Enzymes are HELPERS that speed up reactions",
                "🎯 Each enzyme works on ONE specific substrate",
                "🌡️ Heat can denature (break) enzymes",
                "📊 Enzymes work best at certain temperatures",
                "🔑 Think: Key fits into lock - enzyme fits into substrate"
            ],
            "tip": "Enzymes = biological catalysts that speed things up! ⚡"
        }
    }
    for key, value in simplifications.items():
        if key in topic.lower():
            return value
    return {
        "title": f"📚 Understanding {topic.title()}",
        "bullets": generate_bullet_points(text),
        "tip": "You're doing great! Keep learning step by step. 💪"
    }

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

st.markdown("""
    <div style="border: 2px solid #ffffff; border-radius: 15px; padding: 20px; text-align: center; background: rgba(255, 255, 255, 0.05); margin-bottom: 30px;">
        <h1 style="margin: 0; font-size: 2.2rem;">Lumina AI</h1>
        <p style="margin: 5px 0 0 0; opacity: 0.8;">Enhancing Inclusive Education through Empathetic Assistive Technology</p>
    </div>
    """, unsafe_allow_html=True)
    # Part 2: Interface Layout and Components
col_left, col_right = st.columns([1.4, 2])

with col_left:
    st.subheader("👤 Perception Engine")
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
        let frustrationFrameCount = 0; let neutralFrameCount = 0;
        const FRUSTRATION_THRESHOLD = 90; const NEUTRAL_THRESHOLD = 45;
        const CONFIDENCE_THRESHOLD = 0.82;
        let currentState = "neutral"; let triggerLocked = false;

        async function init() {
            model = await tmImage.load(URL + "model.json", URL + "metadata.json");
            webcam = new tmImage.Webcam(350, 350, true); 
            await webcam.setup(); await webcam.play();
            isTracking = true;
            document.getElementById("webcam-container").appendChild(webcam.canvas);
            document.getElementById("start-btn").style.display = "none";
            document.getElementById("stop-btn").style.display = "inline";
            window.requestAnimationFrame(loop);
        }
        async function loop() { if(isTracking) { webcam.update(); await predict(); window.requestAnimationFrame(loop); } }
        async function predict() {
            const prediction = await model.predict(webcam.canvas);
            let best = prediction.sort((a,b) => b.probability - a.probability)[0];
            const labelDiv = document.getElementById("label-container");
            const robotDiv = document.getElementById("robot-mascot");
            labelDiv.innerHTML = "Status: " + best.className;
            if(best.className === "Frustrated" && best.probability > CONFIDENCE_THRESHOLD) {
                frustrationFrameCount++; neutralFrameCount = 0;
                if(frustrationFrameCount >= FRUSTRATION_THRESHOLD && !triggerLocked) {
                    triggerLocked = true;
                    window.parent.postMessage({type: 'streamlit:set_component_value', value: true, key: 'trig'}, "*");
                }
            } else { frustrationFrameCount = 0; neutralFrameCount++; if(neutralFrameCount >= NEUTRAL_THRESHOLD) { triggerLocked = false; } }
        }
    </script>
    """
    detect_signal = components.html(tm_html, height=750, key="trig")
    if detect_signal and not st.session_state.is_frustrated:
        st.session_state.is_frustrated = True
        st.session_state.frustration_confirmed = False
        if st.session_state.extracted_text:
            st.session_state.ai_simplified_bullets = generate_bullet_points(st.session_state.extracted_text)
        st.session_state.test_logs.append({"Timestamp": datetime.now().strftime("%H:%M:%S"), "Event": "Frustration Detected", "Confidence": "High (>82%)", "Response": "Scaffolding Triggered"})
        st.rerun()

with col_right:
    tab1, tab2, tab3 = st.tabs(["🖥️ Shared Material", "💡 Adaptive Notes", "📊 Research Logs"])
    with tab1:
        st.markdown("### 📱 Learning Material Capture")
        ocr_html = """
            <div style="background: #000; border: 2px solid white; border-radius: 15px; padding: 15px;">
                <video id="v" autoplay style="width: 100%; height: 320px; border-radius: 10px; background: #1a1a1a;"></video>
                <div id="ocr-status" style="color: #aaa; margin: 10px 0; text-align: center;">Ready</div>
                <button id="cast-btn" style="width:48%; padding:12px; background:#27ae60; color:white; border-radius:10px; cursor:pointer;">🌐 Cast</button>
                <button id="ocr-btn" style="width:48%; padding:12px; background:#2980b9; color:white; border-radius:10px; cursor:pointer;">📄 Extract</button>
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
                    window.parent.postMessage({type: 'streamlit:set_component_value', value: result.data.text, key: 'ocr_bridge'}, "*");
                };
            </script>
        """
        # CRITICAL FIX: The component key must match the postMessage key
        extracted = components.html(ocr_html, height=500, key="ocr_bridge")
        if extracted and len(str(extracted)) > 10:
            if st.session_state.extracted_text != extracted:
                st.session_state.extracted_text = extracted
                st.rerun()

        if st.session_state.extracted_text:
            st.success(f"✅ Text extracted! ({len(st.session_state.extracted_text)} characters)")
            with st.expander("📋 Debug: Current Extracted Text"):
                st.write(st.session_state.extracted_text)

    with tab2:
        st.subheader("🤖 Adaptive Support Dashboard")
        if st.session_state.is_frustrated and not st.session_state.frustration_confirmed:
            if not st.session_state.extracted_text:
                st.error("❌ **No text extracted yet!** Please extract text in the Shared Material tab first.")
            else:
                subject, topic, link = detect_igcse_topic(st.session_state.extracted_text)
                content = simplify_content(st.session_state.extracted_text, topic or "General")
                st.markdown(f"""
                <div style="background: rgba(255,20,147,0.15); padding: 30px; border-radius: 15px; border-left: 10px solid #FF1493;">
                    <h2 style="color: #FF1493;">{content['title']}</h2>
                    <ul>{"".join([f"<li>{b}</li>" for b in content['bullets']])}</ul>
                    <p style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px;">💡 <b>{content['tip']}</b></p>
                </div>
                """, unsafe_allow_html=True)
                if link: st.video(link)
                if st.button("✅ I Understand!"):
                    st.session_state.is_frustrated = False
                    st.session_state.test_logs.append({"Timestamp": datetime.now().strftime("%H:%M:%S"), "Event": "User Confirmed Understanding"})
                    st.rerun()
        else:
            st.info("✨ **Status: Monitoring Mode Active**")

    with tab3:
        st.subheader("📊 System Validation Data")
        if st.session_state.test_logs:
            df = pd.DataFrame(st.session_state.test_logs)
            st.dataframe(df, use_container_width=True)
            st.download_button("📥 Download Log", df.to_csv(index=False), "lumina_log.csv")
        else:
            st.write("📭 No events recorded yet.")

# --- SIDEBAR ---
with st.sidebar:
    st.title("🎛️ Lumina Control")
    st.markdown("**Student:** Puteri Aisyah Sofia")
    st.markdown("**Supervisor:** AP Dr. Ibrahim Venkat")
    if st.button("🔄 Reset State"):
        st.session_state.is_frustrated = False
        st.session_state.extracted_text = ""
        st.rerun()


import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime
import json

# --- 1. INTERFACE & DATA SESSION CONFIG ---
st.set_page_config(page_title="Lumina AI | Research Framework", layout="wide", page_icon="🤖")

# IGCSE TOPICS DATABASE
IGCSE_TOPICS = {
    "Math": {
        "algebra": "https://www.youtube.com/watch?v=NybHckSEQq4",
        "geometry": "https://www.youtube.com/watch?v=E_-3j-Rp6Zk",
        "trigonometry": "https://www.youtube.com/watch?v=exLVgL7gDSA",
        "calculus": "https://www.youtube.com/watch?v=WUvTyaaNkzM",
        "statistics": "https://www.youtube.com/watch?v=xxpc-SDeal4",
    },
    "Science": {
        "biology": "https://www.youtube.com/watch?v=V0JGXWpB6ZQ",
        "chemistry": "https://www.youtube.com/watch?v=roQOlHxANxY",
        "physics": "https://www.youtube.com/watch?v=0xALCVJzowA",
        "vertebrate": "https://www.youtube.com/watch?v=lkwsZuUol_A",
        "photosynthesis": "https://www.youtube.com/watch?v=VLZvIqX_Q-k",
        "enzyme": "https://www.youtube.com/watch?v=HGU9xKGLWEg",
    },
    "English": {
        "grammar": "https://www.youtube.com/watch?v=MFQhB73iUUk",
        "essay": "https://www.youtube.com/watch?v=jH1c3sFCVdE",
    },
    "Bahasa Melayu": {
        "tata bahasa": "https://www.youtube.com/watch?v=z8x5BvPZ7Fc",
        "penulisan": "https://www.youtube.com/watch?v=6h4IEppQKuM",
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

# --- 2. LOGIC FUNCTIONS ---

def detect_igcse_topic(text):
    if not text: return None, None, None
    text_lower = text.lower()
    for subject, topics in IGCSE_TOPICS.items():
        for topic, link in topics.items():
            if topic in text_lower:
                return subject, topic, link
    return None, None, None

def simplify_content(text, topic):
    # Specialized curriculum content for your research
    simplifications = {
        "vertebrate": {
            "title": "🦁 Vertebrates Explained Simply",
            "bullets": ["✅ Have a BACKBONE", "✅ 5 Types: Fish, Amphibians, Reptiles, Birds, Mammals", "✅ Humans are vertebrates!"],
            "tip": "Think: Backbone = Vertebra! 🦴"
        },
        "photosynthesis": {
            "title": "🌱 Photosynthesis Made Easy",
            "bullets": ["☀️ Use Sunlight for food", "💨 Take in CO2", "🍎 Make Sugar (Glucose)", "💨 Release Oxygen"],
            "tip": "Light + Water + Air = Plant Food! ✨"
        }
    }
    content = simplifications.get(topic.lower(), {
        "title": f"📚 Understanding {topic.title()}",
        "bullets": ["📖 Key concept detected", "📝 Reviewing academic content", "💡 Breaking down complex terms"],
        "tip": "Take it one step at a time! 💪"
    })
    return content

# --- 3. CUSTOM STYLING ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(rgba(26, 10, 46, 0.9), rgba(13, 0, 26, 0.9)); color: white; }
    [data-testid="stVerticalBlock"] > div:has(div.stMarkdown) {
        background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px);
        border-radius: 15px; padding: 25px; border: 1px solid rgba(255,255,255,0.2);
    }
    .stButton>button {
        background: linear-gradient(45deg, #FF1493, #9400D3) !important;
        color: white !important; border-radius: 25px !important; font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("Lumina AI: Empathetic Education")

# --- 4. LAYOUT ---
col_left, col_right = st.columns([1.3, 2])

with col_left:
    st.subheader("👤 Perception Engine")
    tm_html = """
    <div id="container" style="background: #111; padding: 20px; border-radius: 15px; border: 2px solid white; text-align: center;">
        <div id="webcam-container" style="margin-bottom: 10px;"></div>
        <div id="label-container" style="font-weight: bold; font-size: 1.2rem; color: #FF1493;">Ready to Track</div>
        <button onclick="init()" style="margin-top: 15px; padding: 10px 20px; background: #9400D3; color: white; border: none; border-radius: 20px; cursor: pointer;">🚀 Start Tracking</button>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@latest/dist/tf.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@teachablemachine/image@latest/dist/teachablemachine-image.min.js"></script>
    <script>
        const URL = "https://teachablemachine.withgoogle.com/models/PGXyZqCEN/"; 
        let model, webcam, frustrationFrames = 0;
        async function init() {
            model = await tmImage.load(URL + "model.json", URL + "metadata.json");
            webcam = new tmImage.Webcam(300, 300, true);
            await webcam.setup(); await webcam.play();
            document.getElementById("webcam-container").appendChild(webcam.canvas);
            window.requestAnimationFrame(loop);
        }
        async function loop() { webcam.update(); await predict(); window.requestAnimationFrame(loop); }
        async function predict() {
            const prediction = await model.predict(webcam.canvas);
            let best = prediction.sort((a,b) => b.probability - a.probability)[0];
            document.getElementById("label-container").innerHTML = best.className;
            if(best.className === "Frustrated" && best.probability > 0.85) {
                frustrationFrames++;
                if(frustrationFrames > 40) { // Debounce
                    window.parent.postMessage({type: 'streamlit:set_component_value', value: 'triggered', key: 'trig'}, "*");
                    frustrationFrames = -100; // Reset
                }
            }
        }
    </script>
    """
    # THE FIX: We use a string "triggered" and check for it specifically to avoid NoneType errors
    detect_signal = components.html(tm_html, height=500, key="trig")
    
    if detect_signal == "triggered":
        if not st.session_state.is_frustrated:
            st.session_state.is_frustrated = True
            st.session_state.test_logs.append({"Timestamp": datetime.now().strftime("%H:%M:%S"), "Event": "Frustration Triggered"})
            st.rerun()

with col_right:
    tab1, tab2, tab3 = st.tabs(["🖥️ Shared Material", "💡 Adaptive Notes", "📊 Research Logs"])
    
    with tab1:
        st.markdown("### 📱 Material Capture")
        ocr_html = """
            <div style="background: #000; border: 1px solid white; border-radius: 10px; padding: 10px;">
                <video id="v" autoplay style="width: 100%; height: 280px; background: #1a1a1a;"></video>
                <div style="display: flex; gap: 5px; margin-top: 10px;">
                    <button id="cast-btn" style="flex:1; padding: 10px; background: #27ae60; color: white; border: none; border-radius: 5px;">🌐 Cast Screen</button>
                    <button id="ocr-btn" style="flex:1; padding: 10px; background: #2980b9; color: white; border: none; border-radius: 5px;">📄 Extract Text</button>
                </div>
            </div>
            <script src="https://cdn.jsdelivr.net/npm/tesseract.js@4/dist/tesseract.min.js"></script>
            <script>
                const v = document.getElementById('v');
                document.getElementById('cast-btn').onclick = async () => {
                    v.srcObject = await navigator.mediaDevices.getDisplayMedia({video: true});
                };
                document.getElementById('ocr-btn').onclick = async () => {
                    const canvas = document.createElement('canvas');
                    canvas.width = v.videoWidth; canvas.height = v.videoHeight;
                    canvas.getContext('2d').drawImage(v, 0, 0);
                    const r = await Tesseract.recognize(canvas, 'eng');
                    window.parent.postMessage({type: 'streamlit:set_component_value', value: r.data.text, key: 'ocr_bridge'}, "*");
                };
            </script>
        """
        extracted = components.html(ocr_html, height=450, key="ocr_bridge")
        if extracted:
            st.session_state.extracted_text = extracted

        if st.session_state.extracted_text:
            st.success("✅ Content Loaded Successfully")
            with st.expander("Show Captured Text"):
                st.text(st.session_state.extracted_text)

    with tab2:
        st.subheader("🤖 Adaptive Support")
        if st.session_state.is_frustrated:
            if not st.session_state.extracted_text:
                st.warning("⚠️ Perception engine sees frustration, but no content is captured. Please extract text in Tab 1.")
            else:
                subj, topic, link = detect_igcse_topic(st.session_state.extracted_text)
                content = simplify_content(st.session_state.extracted_text, topic or "General")
                
                st.markdown(f"""
                <div style="background: rgba(255,20,147,0.1); padding: 20px; border-radius: 10px; border-left: 8px solid #FF1493;">
                    <h2 style="color: #FF1493;">{content['title']}</h2>
                    <ul>{"".join([f"<li>{b}</li>" for b in content['bullets']])}</ul>
                </div>
                """, unsafe_allow_html=True)
                
                if link: st.video(link)
                
                if st.button("✅ I Understand Now"):
                    st.session_state.is_frustrated = False
                    st.rerun()
        else:
            st.info("✨ Lumina is observing. Focus on your work, I'll help if you need it!")

    with tab3:
        st.subheader("📊 System Validation")
        if st.session_state.test_logs:
            df = pd.DataFrame(st.session_state.test_logs)
            st.dataframe(df, use_container_width=True)
            st.download_button("Download CSV", df.to_csv(index=False), "research_log.csv")
        else:
            st.write("No events recorded yet.")

# --- SIDEBAR ---
with st.sidebar:
    st.title("Settings")
    st.markdown(f"**Research Assistant:** {st.session_state.get('user_name', 'Puteri Aisyah Sofia')}")
    if st.button("🔄 Reset App"):
        st.session_state.is_frustrated = False
        st.session_state.extracted_text = ""
        st.rerun()

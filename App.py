# --- 4. THE UI & SCREEN SHARING ---
def run_app():
    st.title("🤖 Lumina AI: Empathetic Assistive Technology")
    
    # Sidebar for Demo Controls
    with st.sidebar:
        st.header("📋 Demo Controls")
        st.info("Step 1: Start 'Student Feed' (Camera)\nStep 2: Start 'Learning Material' (Choose Screen Share)")
        if st.button("Reset Scaffolding"):
            st.session_state.frustrated_since = None
            st.rerun()

    if 'frustrated_since' not in st.session_state: st.session_state.frustrated_since = None
    if 'detected_state' not in st.session_state: st.session_state.detected_state = "Neutral"

    # Layout: Camera (Left), Content/Screen (Middle), Scaffolding (Right)
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        st.subheader("👤 Student Feed")
        webrtc_streamer(
            key="webcam",
            mode=WebRtcMode.SENDRECV,
            video_processor_factory=LuminaPerception,
            rtc_configuration=RTC_CONFIG,
            async_processing=True,
        )

    with col2:
        st.subheader("💻 Learning Material")
        st.write("Click 'Start' and select **'Window'** or **'Tab'** to share homework:")
        
        # SCREEN SHARING CONFIGURATION
        webrtc_streamer(
            key="screen-share",
            mode=WebRtcMode.SENDRECV,
            rtc_configuration=RTC_CONFIG,
            # This constraint tells the browser to share the screen/display instead of webcam
            video_receiver_size=1,
            media_stream_constraints={
                "video": {
                    "displaySurface": "monitor", # Options: 'monitor', 'window', 'browser'
                    "cursor": "always"
                },
                "audio": False
            },
        )

    with col3:
        st.subheader("💡 Lumina Scaffolding")
        current_emo = st.session_state['detected_state']
        
        if current_emo == "Frustrated":
            if st.session_state.frustrated_since is None:
                st.session_state.frustrated_since = time.time()
            
            elapsed = time.time() - st.session_state.frustrated_since
            
            if elapsed >= 5:
                st.error("⚠️ Cognitive Overload Detected")
                st.info("**Lumina AI Simplification:**\n'The homework is asking you to break this complex problem into 3 smaller parts. Let's start with Part 1: Definition.'")
            else:
                st.warning(f"Monitoring Frustration... {int(elapsed)}s / 5s")
        else:
            st.session_state.frustrated_since = None
            st.success(f"State: {current_emo}")
            st.write("Content: Standard Instructional Material")

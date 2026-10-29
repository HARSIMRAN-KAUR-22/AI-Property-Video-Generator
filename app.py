import streamlit as st
import os
from video_engine import build_property_video

# Page configuration
st.set_page_config(
    page_title="AI Property Video Generator",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Executive CSS Styling
st.markdown("""
    <style>
    /* Main Background & Fonts */
    .main {
        background-color: #f8fafc;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    
    /* Header Container Styling */
    .header-container {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 2rem 2.5rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
    }
    .header-title {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        color: #ffffff;
    }
    .header-subtitle {
        font-size: 1rem;
        color: #94a3b8;
        font-weight: 400;
    }
    
    /* Section Cards */
    .card-box {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
    }
    
    /* Form Section Badges */
    .step-badge {
        display: inline-block;
        background-color: #2563eb;
        color: white;
        font-size: 0.8rem;
        font-weight: 600;
        padding: 0.25rem 0.6rem;
        border-radius: 20px;
        margin-right: 0.5rem;
        text-transform: uppercase;
    }
    
    /* Custom Button Styling */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: white;
        font-weight: 600;
        font-size: 1rem;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        border: none;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
        box-shadow: 0 6px 16px rgba(37, 99, 235, 0.35);
        transform: translateY(-1px);
    }
    </style>
""", unsafe_allow_html=True)

# Header Section
st.markdown("""
    <div class="header-container">
        <div class="header-title">🏢 AI Property Video Studio</div>
        <div class="header-subtitle">Transform property listings into broadcast-ready promotional videos automatically using AI narration & automated scenes.</div>
    </div>
""", unsafe_allow_html=True)

# Main Two-Column Layout
col1, col2 = st.columns([1.1, 0.9], gap="large")

with col1:
    st.markdown("### <span class='step-badge'>Step 1</span> Listing Information", unsafe_allow_html=True)
    st.caption("Fill in the property details to generate personalized scene text and AI voiceover.")
    
    with st.container():
        prop_name = st.text_input("Property Title", "Skyline Luxury Villa", help="The primary title displayed on scene 1.")
        
        c1, c2 = st.columns(2)
        with c1:
            location = st.text_input("Location / City", "Sector 62, Gurgaon")
        with c2:
            price = st.text_input("Listing Price", "₹2.5 Cr")
            
        c3, c4 = st.columns(2)
        with c3:
            prop_type = st.selectbox("Property Type", ["4 BHK Villa", "3 BHK Apartment", "Commercial Space", "Penthouse", "Plot/Land"])
        with c4:
            contact = st.text_input("Contact CTA", "Call +91-9876543210")
            
        features_input = st.text_area("Key Features (Comma Separated)", "Private Pool, Garden View, 24/7 Security, Modular Kitchen", help="Each feature will be formatted into a distinct feature scene.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### <span class='step-badge'>Step 2</span> Upload Media Assets", unsafe_allow_html=True)
    st.caption("Provide 2-8 high-resolution photos for scene compositions.")
    uploaded_files = st.file_uploader("Upload Property Photos", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

with col2:
    st.markdown("### <span class='step-badge'>Step 3</span> Production & Preview", unsafe_allow_html=True)
    st.caption("Click generate to render voiceovers, captions, and 1080p vertical video.")
    
    generate_btn = st.button("🚀 Render Promotional Video", type="primary")
    
    if generate_btn:
        if not uploaded_files:
            st.error("⚠️ Please upload at least 1 image before generating.")
        elif not prop_name or not location:
            st.error("⚠️ Please fill in at least the Property Title and Location.")
        else:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                status_text.text("📁 Saving uploaded media assets...")
                progress_bar.progress(20)
                
                os.makedirs("temp_uploads", exist_ok=True)
                saved_img_paths = []
                for idx, file in enumerate(uploaded_files):
                    file_path = os.path.join("temp_uploads", f"upload_{idx}.png")
                    with open(file_path, "wb") as f:
                        f.write(file.getbuffer())
                    saved_img_paths.append(file_path)
                
                status_text.text("🎙️ Writing script & synthesizing AI narration audio...")
                progress_bar.progress(50)
                
                features_list = [f.strip() for f in features_input.split(",") if f.strip()]
                prop_data = {
                    "name": prop_name,
                    "location": location,
                    "price": price,
                    "type": prop_type,
                    "features": features_list,
                    "contact": contact
                }
                
                status_text.text("🎬 Compositing scenes, overlays, and rendering MP4...")
                progress_bar.progress(80)
                
                output_path = build_property_video(prop_data, saved_img_paths, "promo_output.mp4")
                st.session_state["generated_video"] = output_path
                
                progress_bar.progress(100)
                status_text.text("✅ Render complete!")
                st.success("Your property promotional video is ready!")
                
            except Exception as e:
                progress_bar.empty()
                status_text.empty()
                st.error(f"❌ Video Generation Failed: {str(e)}")

    # Display video output and metrics if session state contains a valid video
    if "generated_video" in st.session_state and os.path.exists(st.session_state["generated_video"]):
        st.video(st.session_state["generated_video"])
        
        st.markdown("<br>", unsafe_allow_html=True)
        with open(st.session_state["generated_video"], "rb") as video_file:
            st.download_button(
                label="📥 Download HD Video File (MP4)",
                data=video_file,
                file_name=f"{prop_name.lower().replace(' ', '_')}_promo.mp4",
                mime="video/mp4"
            )

# Sidebar Information
st.sidebar.title("ℹ️ Studio Specs")
st.sidebar.info("""
- **Resolution:** 1080 x 1920 (9:16 Vertical)
- **Audio:** gTTS Voiceover Synthesizer
- **Bitrate:** 5000 kbps (High Definition)
- **Engine:** MoviePy v2.0+ & Pillow
""")
import streamlit as st
import os
import sys
from PIL import Image
import io
from typing import Dict, Any
import time
import tempfile
from pathlib import Path
import json

# Add current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set page config
st.set_page_config(
    page_title="Sketch2Answer - AI Design Analysis",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import our modules with better error handling
try:
    from src.vision_processor import SketchVisionProcessor
    from src.rag_system import Sketch2AnswerRAG
    from complete_pipeline import Sketch2DesignPipeline
except ImportError as e:
    st.error(f"❌ Import Error: {e}")
    st.info("💡 Trying alternative import method...")
    try:
        # Alternative import method
        import src.vision_processor
        import src.rag_system
        import complete_pipeline
        SketchVisionProcessor = src.vision_processor.SketchVisionProcessor
        Sketch2AnswerRAG = src.rag_system.Sketch2AnswerRAG
        Sketch2DesignPipeline = complete_pipeline.Sketch2DesignPipeline
        st.success("✅ Successfully imported using alternative method!")
    except ImportError as e2:
        st.error(f"❌ Still can't import: {e2}")
        st.error("Please ensure the src modules are properly installed and accessible.")
        st.info("🔧 Try running: `python -c 'from src.vision_processor import SketchVisionProcessor; print(\"Import works!\")'`")
        st.stop()

# Custom CSS for better UI
st.markdown("""
<style>
    /* Main container */
    .main .block-container {
        padding: 2rem;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #1E1E1E;
        margin-bottom: 1rem;
    }
    
    /* Feature cards */
    .feature-card {
        background: transparent;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    
    .feature-card h3 {
        color: #2E7D32;
        margin-bottom: 0.5rem;
    }
    
    .feature-card p {
        color: #666;
        margin-bottom: 0;
    }
    
    /* Result containers */
    .result-container {
        background: transparent;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1.5rem;
        margin-top: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* File uploader */
    .stFileUploader {
        border: 2px dashed #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
    }
    
    /* Buttons */
    .stButton button {
        width: 100%;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        min-width: 100px;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        padding: 1rem;
    }
    
    .sidebar .stButton button {
        margin-top: 0.5rem;
        margin-bottom: 1rem;
    }
    
    /* Text area */
    .stTextArea textarea {
        border-radius: 5px;
        margin-bottom: 0.5rem;
    }
    
    /* Select slider */
    .stSelectSlider {
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables."""
    if 'pipeline' not in st.session_state:
        st.session_state.pipeline = None
    if 'system_ready' not in st.session_state:
        st.session_state.system_ready = False
    if 'uploaded_image' not in st.session_state:
        st.session_state.uploaded_image = None
    if 'results' not in st.session_state:
        st.session_state.results = None

def initialize_system():
    """Initialize the Sketch2Answer system components."""
    if not st.session_state.get('system_ready', False):
        with st.spinner("🚀 Initializing Sketch2Answer system..."):
            try:
                st.session_state.pipeline = Sketch2DesignPipeline()
                st.session_state.system_ready = True
                st.success("✅ System initialized successfully!")
            except Exception as e:
                st.error(f"❌ Failed to initialize system: {str(e)}")
                st.session_state.system_ready = False

def display_header():
    """Display the main header."""
    st.markdown("""
    <div class="main-header">
        <h1>🎨 Sketch2Answer</h1>
        <p>AI-Powered Design Analysis from Hand-Drawn Sketches</p>
    </div>
    """, unsafe_allow_html=True)

def display_features():
    """Display feature overview."""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>👁️ Vision Analysis</h3>
            <p>Upload hand-drawn sketches, wireframes, or UI mockups. Gemini Vision analyzes and identifies components, layouts, and design patterns.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>📚 Smart Retrieval</h3>
            <p>RAG system searches through GitHub repos, Figma docs, and design guidelines to find relevant information and best practices.</p>
        </div>
        """, unsafe_allow_html=True)

def sidebar_configuration():
    """Configure sidebar options."""
    with st.sidebar:
        st.title("⚙️ Configuration")
        
        # Question input with submit button in a cleaner layout
        st.subheader("Ask a Question")
        question = st.text_area(
            "What would you like to know about the sketch?",
            key="question_input",
            help="Type your question and press Ctrl+Enter or click Submit"
        )
        
        # Submit button with proper styling
        if st.button("Submit", use_container_width=True, type="primary"):
            st.session_state.question_submitted = True
        
        # Analysis depth selection
        st.subheader("Analysis Settings")
        analysis_depth = st.select_slider(
            "Analysis Depth",
            options=["Basic", "Detailed", "Comprehensive"],
            value="Detailed",
            help="Choose how detailed you want the analysis to be"
        )
        
        # Demo mode toggle
        st.subheader("Demo Mode")
        demo_mode = st.toggle("Use Demo Sketch", value=False, help="Use a pre-loaded sketch for testing")
        
        # Handle Ctrl+Enter submission
        if st.session_state.get('question_input') and (st.session_state.get('question_submitted') or st.session_state.get('_submit_question')):
            st.session_state._submit_question = True
            return question, analysis_depth, demo_mode
        else:
            st.session_state._submit_question = False
            return "", analysis_depth, demo_mode

def display_results(results):
    """Display the processing results."""
    if not results:
        return
    
    # Analysis results
    st.subheader("📊 Analysis Results")
    
    analysis = results.get('analysis', {})
    sketch_analysis = analysis.get('sketch_analysis', {})
    components = sketch_analysis.get('components_identified', [])
    
    if components:
        st.markdown("**Components Found:**")
        components_html = "".join([f'<span class="component-tag">{comp}</span>' for comp in components])
        st.markdown(components_html, unsafe_allow_html=True)
    
    # RAG suggestions
    if 'rag_suggestions' in analysis:
        with st.expander("🧠 AI Design Suggestions", expanded=True):
            st.write(analysis['rag_suggestions'])

def process_sketch(uploaded_file, image, question, analysis_depth):
    """Process uploaded sketch through the pipeline."""
    with st.spinner("🔄 Processing your sketch..."):
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                image.save(tmp_file.name)
                temp_path = tmp_file.name
            
            # Process through pipeline
            results = st.session_state.pipeline.process_sketch_to_designs(
                temp_path, question, analysis_depth
            )
            
            # Clean up temp file
            os.unlink(temp_path)
            
            # Store results
            st.session_state.results = results
            
            st.success("✅ Sketch processed successfully!")
            
        except Exception as e:
            st.error(f"❌ Error processing sketch: {str(e)}")

def run_demo_mode(question, analysis_depth):
    """Run demo mode with sample data."""
    with st.spinner("🎬 Running demo..."):
        try:
            # Create sample sketch analysis
            sample_sketch_analysis = {
                'components_identified': ['button', 'form', 'input', 'navigation', 'header'],
                'analysis_type': 'component_analysis',
                'raw_response': 'This sketch shows a login form with header navigation, input fields for username/password, and a submit button.',
                'structured_data': {
                    'layout': 'vertical form layout with header',
                    'interactions': ['login form', 'navigation menu'],
                    'design_patterns': ['form pattern', 'authentication flow']
                }
            }
            
            # Get RAG suggestions
            search_queries = ["login form design", "button components", "navigation patterns"]
            relevant_docs = st.session_state.pipeline.rag_system.search_relevant_docs(search_queries)
            rag_answer = st.session_state.pipeline.rag_system.generate_answer(
                question, sample_sketch_analysis, relevant_docs
            )
            
            # Create mock results
            results = {
                'input': {'image_path': 'demo_sketch', 'question': question},
                'analysis': {
                    'sketch_analysis': sample_sketch_analysis,
                    'rag_suggestions': rag_answer
                }
            }
            
            st.session_state.results = results
            st.success("✅ Demo completed successfully!")
            
        except Exception as e:
            st.error(f"❌ Demo failed: {str(e)}")

def main():
    """Main application function."""
    initialize_session_state()
    display_header()
    
    # Initialize system
    initialize_system()
    
    if not st.session_state.get('system_ready', False):
        st.error("❌ System not ready. Please check your configuration.")
        st.info("💡 Make sure your GOOGLE_API_KEY is set in the .env file")
        return
    
    # Sidebar configuration
    question, analysis_depth, demo_mode = sidebar_configuration()
    
    # Main content with adjusted column widths
    col1, col2 = st.columns([1, 1.5])
    
    with col1:
        st.header("📤 Upload Your Sketch")
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Choose an image file",
            type=['png', 'jpg', 'jpeg', 'bmp', 'gif'],
            help="Upload a hand-drawn sketch or wireframe"
        )
        
        if uploaded_file is not None:
            # Display uploaded image
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Sketch", use_column_width=True)
            
            # Process button - only show if we have both an image and a question
            if question and st.session_state.get('_submit_question'):
                if st.button("🚀 Analyze Sketch", type="primary"):
                    process_sketch(uploaded_file, image, question, analysis_depth)
            elif not question:
                st.info("👆 Enter a question in the sidebar and press Submit or Ctrl+Enter")
        
        # Demo button
        if st.button("🎬 Run Demo with Sample"):
            run_demo_mode(question or "How can I improve this UI design?", analysis_depth)
        
        # Show features if no results yet
        if not st.session_state.get('results'):
            st.markdown("---")
            display_features()
    
    with col2:
        st.header("📊 Analysis Results")
        
        # Display results if they exist
        if st.session_state.get('results'):
            display_results(st.session_state.results)
        else:
            st.info("👈 Upload a sketch and ask a question to see analysis results here!")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
        <h4>🚀 Sketch2Answer System</h4>
        <p>Powered by AI Vision and RAG</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 
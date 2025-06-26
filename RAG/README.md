# 🎨 Sketch2Answer - Draw-to-RAG Interface

> Upload hand-drawn sketches, wireframes, or UI mockups and get intelligent answers using Google Gemini Vision and Retrieval-Augmented Generation (RAG).

![Sketch2Answer Demo](https://img.shields.io/badge/AI-Gemini%20Vision-blue) ![RAG](https://img.shields.io/badge/RAG-ChromaDB-green) ![Framework](https://img.shields.io/badge/UI-Streamlit-red)

## ✨ Features

### 🔍 **Vision Analysis**
- **Sketch Recognition**: Upload hand-drawn sketches, whiteboard photos, or wireframes
- **Component Detection**: Automatically identify UI components (buttons, forms, navigation, etc.)
- **Layout Analysis**: Understand grid structures, spacing, and visual hierarchy
- **Design Pattern Recognition**: Detect common UI/UX patterns

### 📚 **Smart Retrieval (RAG)**
- **Multi-Source Integration**: Search through Figma docs, dev notes, and design guidelines
- **Contextual Search**: Generate relevant queries based on sketch analysis
- **Vector Database**: ChromaDB for efficient similarity search
- **Document Management**: Automatic ingestion and chunking of documentation

### 🤖 **Intelligent Q&A**
- **Natural Language Queries**: Ask questions in plain English
- **Contextual Answers**: Responses based on both sketch analysis and documentation
- **Predefined Templates**: Quick questions for common scenarios
- **Follow-up Suggestions**: AI-powered question recommendations

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.8+
- Google Gemini API key
- Required packages (see `requirements.txt`)

### 2. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd sketch2answer

# Create and activate virtual environment
# For Windows:
python -m venv sketch2answer_env
.\sketch2answer_env\Scripts\activate

# For macOS/Linux:
python3 -m venv sketch2answer_env
source sketch2answer_env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp config.env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

### 3. Get Google Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Create a new API key
3. Add it to your `.env` file:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

### 4. Run the Application

```bash
# Make sure your virtual environment is activated
# For Windows:
.\sketch2answer_env\Scripts\activate

# For macOS/Linux:
source sketch2answer_env/bin/activate

# Run the application
streamlit run app.py
```

Navigate to `http://localhost:8501` in your browser.

### 5. Virtual Environment Management

#### Activating the Environment
```bash
# Windows
.\sketch2answer_env\Scripts\activate

# macOS/Linux
source sketch2answer_env/bin/activate
```

#### Deactivating the Environment
```bash
deactivate
```

#### Troubleshooting Virtual Environment

1. **If activation fails:**
```bash
# Remove old environment
rm -rf sketch2answer_env

# Create new environment
python -m venv sketch2answer_env

# Activate and install dependencies
.\sketch2answer_env\Scripts\activate  # Windows
source sketch2answer_env/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

2. **If packages are missing:**
```bash
# Activate environment first, then:
pip install -r requirements.txt
```

3. **To update packages:**
```bash
pip install --upgrade -r requirements.txt
```

## 📖 Usage Guide

### Basic Workflow

1. **Upload Sketch**: Drag and drop or browse for your sketch/wireframe image
2. **Choose Analysis Type**: 
   - 🔍 Component Analysis
   - ❓ Missing Elements  
   - 📋 Design Guidelines
3. **Ask Questions**: Use predefined questions or type your own
4. **Get Answers**: Receive intelligent responses with relevant documentation

### Example Questions

#### Component Analysis
- "Which component is missing from this design?"
- "What UI components are present in this sketch?"
- "How should these components be implemented?"

#### Design Guidelines
- "Which part matches our UI guidelines?"
- "What design patterns are used here?"
- "Does this follow accessibility best practices?"

#### Implementation
- "How would you code this interface?"
- "What CSS grid/flexbox structure is needed?"
- "How to make this responsive?"

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit UI  │───▶│  Sketch2Answer  │───▶│   Gemini API    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                               │
                               ▼
                    ┌─────────────────┐    ┌─────────────────┐
                    │   RAG System    │───▶│    ChromaDB     │
                    └─────────────────┘    └─────────────────┘
                               │
                               ▼
                    ┌─────────────────┐
                    │  Documentation  │
                    │  (Figma, GitHub │
                    │   Local docs)   │
                    └─────────────────┘
```

### Core Components

1. **Vision Processor** (`src/vision_processor.py`)
   - Interfaces with Gemini Vision API
   - Analyzes sketches for components and patterns
   - Generates structured data from visual input

2. **RAG System** (`src/rag_system.py`)
   - Document ingestion and chunking
   - Vector embeddings with ChromaDB
   - Similarity search and retrieval

3. **Main Controller** (`src/sketch2answer.py`)
   - Orchestrates vision analysis and RAG
   - Generates intelligent answers
   - Manages question suggestions

4. **Web Interface** (`app.py`)
   - Streamlit-based UI
   - Image upload and display
   - Interactive Q&A interface

## 📁 Project Structure

```
sketch2answer/
├── src/
│   ├── __init__.py
│   ├── sketch2answer.py      # Main orchestrator
│   ├── vision_processor.py   # Gemini Vision integration
│   └── rag_system.py        # RAG implementation
├── docs/                    # Local documentation files
├── chroma_db/              # Vector database (auto-created)
├── app.py                  # Streamlit web interface
├── requirements.txt        # Python dependencies
├── config.env.example      # Environment variables template
└── README.md              # This file
```

## ⚙️ Configuration

### Environment Variables

```bash
# Required
GOOGLE_API_KEY=your_google_gemini_api_key_here

# Optional - for external integrations
FIGMA_TOKEN=your_figma_token_here
GITHUB_TOKEN=your_github_token_here

# RAG Settings
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RESULTS=5
CHROMA_PERSIST_DIR=./chroma_db
```

### Analysis Types

- **Component Analysis**: Identifies UI components and layout structure
- **Missing Elements**: Suggests what's missing for complete UX
- **Design Guidelines**: Evaluates against design principles

## 🔧 Customization

### Adding New Document Sources

1. **Local Documents**: Add `.txt` files to the `docs/` directory
2. **Figma Integration**: Set `FIGMA_TOKEN` and implement API calls
3. **GitHub Integration**: Set `GITHUB_TOKEN` for repository docs

### Custom Prompts

Modify analysis prompts in `vision_processor.py`:

```python
self.analysis_prompts = {
    'custom_analysis': """
    Your custom analysis prompt here...
    """
}
```

### UI Customization

Update Streamlit interface in `app.py`:
- Custom CSS styles
- Additional sidebar options
- New question categories

## 🎯 Example Use Cases

### 1. Design Review
Upload a wireframe and ask:
- "What accessibility improvements are needed?"
- "Does this match our design system?"
- "What's missing for mobile responsiveness?"

### 2. Component Planning
Upload a sketch and ask:
- "Which React components should I create?"
- "How should I structure the CSS?"
- "What state management is needed?"

### 3. UX Audit
Upload a user flow and ask:
- "What user feedback mechanisms are missing?"
- "How can navigation be improved?"
- "What loading states should be added?"

## 🚀 Advanced Features

### Batch Processing
```python
from src.sketch2answer import Sketch2Answer

s2a = Sketch2Answer()
results = s2a.batch_analyze_sketches([
    {'image': image1, 'question': 'What components are missing?'},
    {'image': image2, 'question': 'How to implement this layout?'}
])
```

### Custom RAG Sources
```python
# Add your own document ingestion
s2a.rag_system.ingest_documents('custom_source')
```

### API Integration
Extend for programmatic access:
```python
result = s2a.ask_question(
    image=sketch_image,
    question="How should this be coded?",
    analysis_type="component_analysis"
)
```

## 🛠️ Troubleshooting

### Common Issues

1. **API Key Errors**
   - Ensure `GOOGLE_API_KEY` is set correctly
   - Check API quota and billing

2. **Module Import Errors**
   - Verify all dependencies are installed
   - Check Python path and virtual environment

3. **ChromaDB Issues**
   - Delete `chroma_db/` folder to reset database
   - Ensure sufficient disk space

4. **Memory Issues**
   - Reduce `CHUNK_SIZE` in configuration
   - Process smaller images

### Performance Tips

- Use smaller images for faster processing
- Limit document collection size
- Adjust embedding model for speed vs accuracy

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable  
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Google Gemini for vision capabilities
- ChromaDB for vector storage
- Streamlit for the web interface
- LangChain for RAG components

---

**🎨 Start sketching and get intelligent answers today!** 
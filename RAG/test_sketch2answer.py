#!/usr/bin/env python3
"""
Test script for Sketch2Answer system
Demonstrates how the knowledge base works without external tokens
"""

import os
from PIL import Image, ImageDraw
from src.sketch2answer import Sketch2Answer

def create_sample_sketch():
    """Create a simple sketch for testing."""
    # Create a simple wireframe sketch
    img = Image.new('RGB', (400, 300), 'white')
    draw = ImageDraw.Draw(img)
    
    # Draw a simple UI mockup
    # Header
    draw.rectangle([10, 10, 390, 50], outline='black', width=2)
    draw.text((20, 25), "Header / Navigation", fill='black')
    
    # Main content area
    draw.rectangle([10, 60, 390, 200], outline='black', width=2)
    draw.text((20, 75), "Main Content Area", fill='black')
    
    # Buttons
    draw.rectangle([20, 100, 100, 130], outline='blue', width=2)
    draw.text((25, 110), "Button 1", fill='blue')
    
    draw.rectangle([120, 100, 200, 130], outline='blue', width=2)
    draw.text((125, 110), "Button 2", fill='blue')
    
    # Form fields
    draw.rectangle([20, 150, 200, 170], outline='gray', width=1)
    draw.text((25, 155), "Input Field", fill='gray')
    
    # Footer
    draw.rectangle([10, 210, 390, 250], outline='black', width=2)
    draw.text((20, 225), "Footer", fill='black')
    
    return img

def test_knowledge_base():
    """Test what knowledge is available in the system."""
    print("🔍 Initializing Sketch2Answer system...")
    
    try:
        # Initialize the system
        s2a = Sketch2Answer()
        
        # Check system status
        status = s2a.get_system_status()
        print(f"✅ System Status: {status}")
        
        # Show available knowledge sources
        if s2a.rag_system:
            stats = s2a.rag_system.get_collection_stats()
            print(f"📚 Knowledge Base: {stats['total_documents']} documents loaded")
            print(f"🔧 Sources: {stats['sources_configured']}")
        
        print("\n📋 Available Question Categories:")
        questions = s2a.get_predefined_questions()
        for category, q_list in questions.items():
            print(f"  • {category}: {len(q_list)} questions")
        
        return s2a
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_sketch_analysis(s2a):
    """Test sketch analysis with a sample image."""
    print("\n🎨 Testing Sketch Analysis...")
    
    # Create a sample sketch
    sketch = create_sample_sketch()
    sketch.save("sample_sketch.png")
    print("✅ Created sample sketch: sample_sketch.png")
    
    # Test different question types
    test_questions = [
        ("Which component is missing from this design?", "missing_elements"),
        ("What UI components are present in this sketch?", "component_analysis"),
        ("Does this follow accessibility best practices?", "design_guidelines")
    ]
    
    for question, analysis_type in test_questions:
        print(f"\n❓ Question: {question}")
        print(f"🔍 Analysis Type: {analysis_type}")
        
        try:
            result = s2a.ask_question(sketch, question, analysis_type)
            
            if 'error' in result:
                print(f"❌ Error: {result['error']}")
            else:
                print(f"🎯 Components Found: {result['sketch_analysis']['components_identified']}")
                print(f"🔎 Search Queries: {len(result['search_queries'])} generated")
                print(f"📚 Relevant Docs: {len(result['relevant_docs'])} found")
                print(f"🤖 Answer: {result['answer'][:200]}...")
                
        except Exception as e:
            print(f"❌ Error processing question: {e}")

def show_knowledge_samples():
    """Show what knowledge is in the system."""
    print("\n📚 Sample Knowledge Base Content:")
    
    knowledge_files = [
        "docs/ui_patterns.txt",
        "docs/component_specs.txt", 
        "docs/accessibility_guidelines.txt"
    ]
    
    for file_path in knowledge_files:
        if os.path.exists(file_path):
            print(f"\n📄 {file_path}:")
            with open(file_path, 'r') as f:
                content = f.read()[:300]  # First 300 characters
                print(f"   {content}...")

if __name__ == "__main__":
    print("🎨 Sketch2Answer Test Suite")
    print("=" * 50)
    
    # Test 1: Knowledge Base
    s2a = test_knowledge_base()
    
    if s2a:
        # Test 2: Show available knowledge
        show_knowledge_samples()
        
        # Test 3: Sketch analysis (only if system works)
        test_sketch_analysis(s2a)
        
        print("\n✅ Test completed! Check the web app at: http://localhost:8501")
    else:
        print("❌ System initialization failed. Check your GOOGLE_API_KEY in config.env") 
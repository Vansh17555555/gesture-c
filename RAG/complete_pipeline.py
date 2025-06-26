#!/usr/bin/env python3
"""
Sketch Analysis Pipeline
Processes sketches through vision analysis and RAG suggestions
"""

import os
from pathlib import Path
from PIL import Image
from typing import Dict, Any, List, Optional
import json

from src.vision_processor import SketchVisionProcessor
from src.rag_system import Sketch2AnswerRAG

class Sketch2DesignPipeline:
    """
    Pipeline: Sketch → Analysis → RAG Suggestions
    """
    
    def __init__(self):
        """Initialize the pipeline components."""
        self.vision_processor = SketchVisionProcessor()
        self.rag_system = Sketch2AnswerRAG()
        
        # Initialize RAG system with documents
        self.rag_system.ingest_documents()
    
    def process_sketch_to_designs(
        self,
        image_path: str,
        question: str,
        analysis_depth: str = "Detailed"
    ) -> Dict[str, Any]:
        """
        Process a sketch through the pipeline.
        
        Args:
            image_path: Path to the sketch image
            question: User's question about the sketch
            analysis_depth: Level of analysis detail ("Basic", "Detailed", "Comprehensive")
            
        Returns:
            Dictionary containing analysis results and suggestions
        """
        try:
            # 1. Analyze sketch using vision model
            image = Image.open(image_path)
            sketch_analysis = self.vision_processor.process_sketch(
                image,
                analysis_type='component_analysis'
            )
            
            # 2. Generate search queries based on analysis
            search_queries = self._generate_search_queries(sketch_analysis)
            
            # 3. Search for relevant documents
            relevant_docs = self.rag_system.search_relevant_docs(search_queries)
            
            # 4. Generate answer using RAG
            rag_answer = self.rag_system.generate_answer(
                question,
                sketch_analysis,
                relevant_docs
            )
            
            # 5. Compile results
            results = {
                'input': {
                    'image_path': image_path,
                    'question': question
                },
                'analysis': {
                    'sketch_analysis': sketch_analysis,
                    'rag_suggestions': rag_answer
                }
            }
            
            return results
            
        except Exception as e:
            raise Exception(f"Pipeline processing failed: {str(e)}")
    
    def _generate_search_queries(self, sketch_analysis: Dict[str, Any]) -> list:
        """Generate search queries based on sketch analysis."""
        queries = []
        
        # Add queries based on identified components
        components = sketch_analysis.get('components_identified', [])
        for component in components:
            queries.append(f"{component} design pattern")
            queries.append(f"{component} best practices")
        
        # Add queries based on analysis type
        analysis_type = sketch_analysis.get('analysis_type', '')
        if analysis_type:
            queries.append(f"{analysis_type} design guidelines")
        
        # Add queries based on structured data
        structured_data = sketch_analysis.get('structured_data', {})
        if 'layout' in structured_data:
            queries.append(f"{structured_data['layout']} layout patterns")
        if 'design_patterns' in structured_data:
            for pattern in structured_data['design_patterns']:
                queries.append(f"{pattern} implementation")
        
        return queries

def demo_with_sample_sketch():
    """Create a demo with a sample sketch description."""
    print("🎬 Running Sketch Analysis Demo\n")
    
    # Create a sample sketch description
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
    
    # Initialize pipeline components
    rag_system = Sketch2AnswerRAG()
    
    # Ensure RAG has some data
    print("📚 Checking RAG system...")
    stats = rag_system.get_collection_stats()
    if stats['total_documents'] < 3:
        print("   Populating with local documentation...")
        rag_system.ingest_documents('local_docs')
    
    # Generate RAG suggestions
    print("💡 Getting design suggestions...")
    search_queries = ["login form design", "button components", "navigation patterns"]
    relevant_docs = rag_system.search_relevant_docs(search_queries)
    rag_answer = rag_system.generate_answer(
        "How can I improve this login form design?", 
        sample_sketch_analysis, 
        relevant_docs
    )
    
    print("\n" + "="*60)
    print("🎉 DEMO RESULTS")
    print("="*60)
    
    print(f"\n📊 Analysis Results:")
    print(f"   Components found: {', '.join(sample_sketch_analysis['components_identified'])}")
    print(f"   RAG documents used: {len(relevant_docs)}")
    
    print(f"\n💡 RAG Suggestions Preview:")
    print(f"   {rag_answer[:200]}...")
    
    print("\n🚀 Pipeline demo complete!")

if __name__ == "__main__":
    # Run the demo
    demo_with_sample_sketch() 
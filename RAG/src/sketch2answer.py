from typing import Dict, List, Any, Optional
from PIL import Image
import io
import base64
from .vision_processor import SketchVisionProcessor
from .rag_system import Sketch2AnswerRAG

class Sketch2Answer:
    """
    Main class that orchestrates the Sketch2Answer system:
    1. Processes sketches with vision model
    2. Generates search queries based on analysis
    3. Retrieves relevant documents via RAG
    4. Generates intelligent answers
    """
    
    def __init__(self, persist_directory: str = "./chroma_db", initialize_rag: bool = True):
        """
        Initialize the Sketch2Answer system.
        
        Args:
            persist_directory: Directory for vector database persistence
            initialize_rag: Whether to initialize RAG system immediately
        """
        # Initialize vision processor
        self.vision_processor = SketchVisionProcessor()
        
        # Initialize RAG system
        if initialize_rag:
            self.rag_system = Sketch2AnswerRAG(persist_directory)
            self._ensure_documents_ingested()
        else:
            self.rag_system = None
    
    def _ensure_documents_ingested(self):
        """Ensure documents are ingested into the RAG system."""
        try:
            stats = self.rag_system.get_collection_stats()
            if stats.get('total_documents', 0) == 0:
                print("No documents found in vector database. Ingesting sample documents...")
                self.rag_system.ingest_documents('all')
                print("Document ingestion completed.")
        except Exception as e:
            print(f"Error checking document ingestion: {e}")
    
    def analyze_sketch(self, 
                      image: Image.Image, 
                      analysis_type: str = 'component_analysis') -> Dict[str, Any]:
        """
        Analyze a sketch using the vision processor.
        
        Args:
            image: PIL Image object of the sketch
            analysis_type: Type of analysis ('component_analysis', 'missing_elements', 'design_guidelines')
            
        Returns:
            Analysis results from vision processor
        """
        return self.vision_processor.process_sketch(image, analysis_type)
    
    def ask_question(self, 
                    image: Image.Image, 
                    question: str,
                    analysis_type: str = 'component_analysis') -> Dict[str, Any]:
        """
        Ask a question about a sketch and get an intelligent answer.
        
        Args:
            image: PIL Image object of the sketch
            question: Question about the sketch
            analysis_type: Type of analysis to perform on the sketch
            
        Returns:
            Dictionary containing analysis, search results, and final answer
        """
        # Step 1: Analyze the sketch
        print("🔍 Analyzing sketch with Gemini Vision...")
        sketch_analysis = self.analyze_sketch(image, analysis_type)
        
        if 'error' in sketch_analysis:
            return {
                'error': sketch_analysis['error'],
                'question': question,
                'analysis_type': analysis_type
            }
        
        # Step 2: Generate search queries
        print("🔎 Generating search queries...")
        search_queries = self.vision_processor.create_search_queries(sketch_analysis)
        
        # Add the user's question as a search query
        search_queries.insert(0, question)
        
        # Step 3: Search for relevant documents
        if self.rag_system:
            print("📚 Searching relevant documentation...")
            relevant_docs = self.rag_system.search_relevant_docs(search_queries)
            
            # Step 4: Generate final answer
            print("🤖 Generating intelligent answer...")
            answer = self.rag_system.generate_answer(question, sketch_analysis, relevant_docs)
        else:
            relevant_docs = []
            answer = "RAG system not initialized. Only sketch analysis is available."
        
        return {
            'question': question,
            'analysis_type': analysis_type,
            'sketch_analysis': sketch_analysis,
            'search_queries': search_queries,
            'relevant_docs': relevant_docs,
            'answer': answer,
            'success': True
        }
    
    def batch_analyze_sketches(self, 
                              images_and_questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze multiple sketches with questions in batch.
        
        Args:
            images_and_questions: List of dicts with 'image', 'question', and optional 'analysis_type'
            
        Returns:
            List of analysis results
        """
        results = []
        
        for i, item in enumerate(images_and_questions):
            print(f"Processing sketch {i+1}/{len(images_and_questions)}...")
            
            image = item['image']
            question = item['question']
            analysis_type = item.get('analysis_type', 'component_analysis')
            
            result = self.ask_question(image, question, analysis_type)
            result['batch_index'] = i
            results.append(result)
        
        return results
    
    def get_predefined_questions(self) -> Dict[str, List[str]]:
        """
        Get predefined questions organized by category.
        
        Returns:
            Dictionary of question categories and their questions
        """
        return {
            'Component Analysis': [
                "Which component is missing from this design?",
                "What UI components are present in this sketch?",
                "How should these components be implemented?",
                "What's the layout structure of this design?"
            ],
            'Design Guidelines': [
                "Which part matches our UI guidelines?",
                "What design patterns are used here?",
                "How can this design be improved?",
                "Does this follow accessibility best practices?"
            ],
            'Implementation': [
                "How would you code this interface?",
                "What CSS grid/flexbox structure is needed?",
                "What React components would you create?",
                "How to make this responsive?"
            ],
            'UX Review': [
                "What's missing for good user experience?",
                "How can navigation be improved?",
                "What interactions should be added?",
                "Are there any usability issues?"
            ]
        }
    
    def suggest_questions(self, sketch_analysis: Dict[str, Any]) -> List[str]:
        """
        Suggest relevant questions based on sketch analysis.
        
        Args:
            sketch_analysis: Analysis result from vision processor
            
        Returns:
            List of suggested questions
        """
        suggestions = []
        components = sketch_analysis.get('components_identified', [])
        
        # Component-specific suggestions
        if 'button' in components:
            suggestions.append("How should these buttons be styled according to our design system?")
        if 'form' in components or 'input' in components:
            suggestions.append("What validation and error handling should be added to this form?")
        if 'navigation' in components or 'nav' in components:
            suggestions.append("How can this navigation be made more accessible?")
        if 'card' in components:
            suggestions.append("What information hierarchy should these cards follow?")
        
        # General suggestions based on analysis type
        analysis_type = sketch_analysis.get('analysis_type', '')
        if analysis_type == 'missing_elements':
            suggestions.extend([
                "What essential UI components are missing?",
                "How can user feedback be improved?",
                "What accessibility features should be added?"
            ])
        elif analysis_type == 'design_guidelines':
            suggestions.extend([
                "Does this follow our design system?",
                "What spacing and typography improvements are needed?",
                "How does this compare to modern UI patterns?"
            ])
        
        # Default suggestions if none generated
        if not suggestions:
            suggestions = [
                "What components are present in this sketch?",
                "How should this design be implemented?",
                "What improvements would you suggest?"
            ]
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def ingest_new_documents(self, source_type: str = 'all'):
        """
        Ingest new documents into the RAG system.
        
        Args:
            source_type: 'figma', 'github', 'local_docs', or 'all'
        """
        if self.rag_system:
            self.rag_system.ingest_documents(source_type)
        else:
            print("RAG system not initialized.")
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get status of the Sketch2Answer system.
        
        Returns:
            Dictionary with system status information
        """
        status = {
            'vision_processor': 'initialized',
            'rag_system': 'initialized' if self.rag_system else 'not initialized'
        }
        
        if self.rag_system:
            status['rag_stats'] = self.rag_system.get_collection_stats()
        
        return status
    
    @staticmethod
    def prepare_image_from_upload(uploaded_file) -> Optional[Image.Image]:
        """
        Prepare image from uploaded file for processing.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            PIL Image object or None if error
        """
        try:
            # Read uploaded file
            image_bytes = uploaded_file.read()
            
            # Create PIL Image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA'):
                # Create white background
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'RGBA':
                    background.paste(image, mask=image.split()[-1])
                else:
                    background.paste(image, mask=image.split()[-1])
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            return image
            
        except Exception as e:
            print(f"Error processing uploaded image: {e}")
            return None
    
    @staticmethod
    def image_to_base64(image: Image.Image) -> str:
        """
        Convert PIL Image to base64 string for display.
        
        Args:
            image: PIL Image object
            
        Returns:
            Base64 encoded image string
        """
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f"data:image/png;base64,{img_str}" 
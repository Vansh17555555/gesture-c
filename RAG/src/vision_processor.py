import google.generativeai as genai
import os
from PIL import Image
import io
import base64
from typing import Dict, List, Any
from dotenv import load_dotenv

load_dotenv()

class SketchVisionProcessor:
    """
    Processes hand-drawn sketches using Google Gemini Vision to extract
    structured information about UI components, layouts, and design elements.
    """
    
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        genai.configure(api_key=self.api_key)
        self.vision_model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Prompt templates for different analysis types
        self.analysis_prompts = {
            'component_analysis': """
            Analyze this hand-drawn sketch/wireframe and identify:
            1. UI components (buttons, forms, navigation, cards, etc.)
            2. Layout structure (grid, flexbox, sections)
            3. Interactive elements (clickable areas, input fields)
            4. Text content and labels
            5. Visual hierarchy and spacing
            
            Return a structured JSON with:
            {
                "components": [list of identified UI components],
                "layout": "description of layout structure",
                "interactions": [list of interactive elements],
                "text_content": [list of text/labels found],
                "design_patterns": [list of design patterns used]
            }
            """,
            
            'missing_elements': """
            Analyze this sketch as a UI design and identify what might be missing for a complete user interface:
            1. Essential UI components that should be present
            2. Accessibility considerations
            3. Navigation elements
            4. User feedback mechanisms
            5. Data display components
            
            Focus on common UI/UX best practices and return suggestions in JSON format.
            """,
            
            'design_guidelines': """
            Evaluate this sketch against modern UI/UX design guidelines:
            1. Visual hierarchy and spacing
            2. Component consistency
            3. User flow and navigation
            4. Accessibility considerations
            5. Mobile responsiveness indicators
            
            Provide specific feedback on what matches or violates design principles.
            """
        }
    
    def process_sketch(self, image: Image.Image, analysis_type: str = 'component_analysis') -> Dict[str, Any]:
        """
        Process a sketch image and return structured analysis.
        
        Args:
            image: PIL Image object of the sketch
            analysis_type: Type of analysis to perform
            
        Returns:
            Dictionary containing structured analysis results
        """
        try:
            # Get appropriate prompt
            prompt = self.analysis_prompts.get(analysis_type, self.analysis_prompts['component_analysis'])
            
            # Generate response using Gemini Vision
            response = self.vision_model.generate_content([prompt, image])
            
            # Extract structured information
            analysis_result = {
                'raw_response': response.text,
                'analysis_type': analysis_type,
                'components_identified': self._extract_components(response.text),
                'structured_data': self._parse_structured_response(response.text)
            }
            
            return analysis_result
            
        except Exception as e:
            return {
                'error': str(e),
                'analysis_type': analysis_type,
                'components_identified': [],
                'structured_data': {}
            }
    
    def _extract_components(self, response_text: str) -> List[str]:
        """Extract UI components mentioned in the response."""
        # Simple keyword extraction for components
        components_keywords = [
            'button', 'form', 'input', 'navigation', 'nav', 'header', 'footer',
            'sidebar', 'card', 'modal', 'dropdown', 'menu', 'search', 'filter',
            'table', 'list', 'grid', 'chart', 'graph', 'image', 'video',
            'text field', 'checkbox', 'radio button', 'slider', 'toggle'
        ]
        
        found_components = []
        response_lower = response_text.lower()
        
        for component in components_keywords:
            if component in response_lower:
                found_components.append(component)
        
        return list(set(found_components))  # Remove duplicates
    
    def _parse_structured_response(self, response_text: str) -> Dict[str, Any]:
        """Attempt to parse JSON from the response or create structured data."""
        import json
        import re
        
        # Try to find JSON in the response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        # If no valid JSON, create basic structure from text
        return {
            'summary': response_text[:500] + '...' if len(response_text) > 500 else response_text,
            'key_points': self._extract_key_points(response_text)
        }
    
    def _extract_key_points(self, text: str) -> List[str]:
        """Extract key points from text response."""
        # Look for numbered lists or bullet points
        import re
        
        # Find numbered points (1., 2., etc.)
        numbered_points = re.findall(r'\d+\.\s*([^\n\r]+)', text)
        if numbered_points:
            return numbered_points[:10]  # Limit to 10 points
        
        # Find bullet points or lines starting with -
        bullet_points = re.findall(r'[-*•]\s*([^\n\r]+)', text)
        if bullet_points:
            return bullet_points[:10]
        
        # Fallback: split by sentences and take first few
        sentences = text.split('. ')
        return sentences[:5] if sentences else [text[:200]]

    def create_search_queries(self, analysis_result: Dict[str, Any]) -> List[str]:
        """
        Generate search queries based on the sketch analysis for RAG retrieval.
        
        Args:
            analysis_result: Result from process_sketch
            
        Returns:
            List of search queries for RAG system
        """
        queries = []
        
        # Add component-based queries
        components = analysis_result.get('components_identified', [])
        for component in components:
            queries.append(f"{component} component design guidelines")
            queries.append(f"{component} UI implementation best practices")
        
        # Add general design queries
        queries.extend([
            "UI component library design patterns",
            "wireframe to code implementation",
            "design system components",
            "user interface accessibility guidelines",
            "responsive design principles"
        ])
        
        # Add specific queries based on structured data
        structured_data = analysis_result.get('structured_data', {})
        if isinstance(structured_data, dict):
            if 'design_patterns' in structured_data:
                for pattern in structured_data['design_patterns']:
                    queries.append(f"{pattern} design pattern implementation")
        
        return queries[:10]  # Limit to top 10 queries 
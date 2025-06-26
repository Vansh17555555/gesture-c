"""
Design Generator - Convert RAG suggestions into visual designs
Supports: HTML/CSS generation, SVG wireframes, and AI image prompts
"""

import os
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class DesignGenerator:
    """
    Generates visual designs from RAG suggestions and sketch analysis.
    Supports multiple output formats: HTML/CSS, SVG, AI prompts.
    """
    
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_API_KEY')
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.llm = genai.GenerativeModel('gemini-1.5-flash')
        
        self.output_dir = Path('./generated_designs')
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_design_from_analysis(self, 
                                    sketch_analysis: Dict[str, Any], 
                                    rag_suggestions: str,
                                    output_format: str = 'html') -> Dict[str, Any]:
        """
        Generate a visual design based on sketch analysis and RAG suggestions.
        
        Args:
            sketch_analysis: Result from vision processor
            rag_suggestions: Generated answer from RAG system
            output_format: 'html', 'svg', or 'prompt'
            
        Returns:
            Generated design data with file paths and metadata
        """
        # Extract components and requirements
        components = sketch_analysis.get('components_identified', [])
        
        if output_format == 'html':
            return self._generate_html_css(sketch_analysis, rag_suggestions)
        elif output_format == 'svg':
            return self._generate_svg_wireframe(sketch_analysis, rag_suggestions)
        elif output_format == 'prompt':
            return self._generate_ai_prompt(sketch_analysis, rag_suggestions)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
    
    def _generate_html_css(self, sketch_analysis: Dict[str, Any], rag_suggestions: str) -> Dict[str, Any]:
        """Generate functional HTML/CSS code from suggestions."""
        components = sketch_analysis.get('components_identified', [])
        
        prompt = f"""
        Based on this sketch analysis and design guidelines, generate a complete, functional HTML page with CSS:
        
        Sketch Components: {', '.join(components)}
        Design Guidelines: {rag_suggestions}
        
        Requirements:
        1. Create a modern, responsive HTML page
        2. Include all identified components
        3. Use the design guidelines provided
        4. Add proper semantic HTML
        5. Include beautiful, modern CSS styling
        6. Make it mobile-responsive
        7. Use CSS Grid/Flexbox for layout
        8. Include hover effects and transitions
        
        Generate ONLY the complete HTML file with embedded CSS (no separate files).
        Make it production-ready and visually appealing.
        """
        
        try:
            response = self.llm.generate_content(prompt)
            html_content = response.text
            
            # Clean up the response (remove markdown formatting if present)
            if '```html' in html_content:
                html_content = html_content.split('```html')[1].split('```')[0].strip()
            elif '```' in html_content:
                html_content = html_content.split('```')[1].strip()
            
            # Save to file
            filename = f"design_{len(list(self.output_dir.glob('*.html'))) + 1}.html"
            file_path = self.output_dir / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return {
                'type': 'html',
                'file_path': str(file_path),
                'content': html_content,
                'components': components,
                'preview_url': f"file://{file_path.absolute()}"
            }
            
        except Exception as e:
            return {'error': f"HTML generation failed: {str(e)}"}
    
    def _generate_svg_wireframe(self, sketch_analysis: Dict[str, Any], rag_suggestions: str) -> Dict[str, Any]:
        """Generate SVG wireframe from suggestions."""
        components = sketch_analysis.get('components_identified', [])
        
        prompt = f"""
        Generate a clean SVG wireframe based on this analysis:
        
        Components: {', '.join(components)}
        Guidelines: {rag_suggestions}
        
        Create a professional wireframe SVG (800x600) that shows:
        1. Layout structure with rectangles for components
        2. Proper spacing and hierarchy
        3. Labels for each component
        4. Clean, minimalist design
        5. Standard wireframe styling (gray boxes, simple lines)
        
        Generate ONLY the SVG code, no explanations.
        """
        
        try:
            response = self.llm.generate_content(prompt)
            svg_content = response.text
            
            # Clean up the response
            if '```svg' in svg_content:
                svg_content = svg_content.split('```svg')[1].split('```')[0].strip()
            elif '```' in svg_content:
                svg_content = svg_content.split('```')[1].strip()
            
            # Save to file
            filename = f"wireframe_{len(list(self.output_dir.glob('*.svg'))) + 1}.svg"
            file_path = self.output_dir / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(svg_content)
            
            return {
                'type': 'svg',
                'file_path': str(file_path),
                'content': svg_content,
                'components': components
            }
            
        except Exception as e:
            return {'error': f"SVG generation failed: {str(e)}"}
    
    def _generate_ai_prompt(self, sketch_analysis: Dict[str, Any], rag_suggestions: str) -> Dict[str, Any]:
        """Generate optimized prompt for AI image generators like DALL-E or Midjourney."""
        components = sketch_analysis.get('components_identified', [])
        
        prompt = f"""
        Create an optimized prompt for AI image generation (DALL-E/Midjourney) based on:
        
        Components: {', '.join(components)}
        Design Guidelines: {rag_suggestions}
        
        Generate a detailed, specific prompt that would create a beautiful UI design image.
        Include:
        1. Visual style (modern, minimalist, etc.)
        2. Color scheme
        3. Layout description
        4. Component details
        5. Overall aesthetic
        
        Make it suitable for AI image generators.
        """
        
        try:
            response = self.llm.generate_content(prompt)
            ai_prompt = response.text.strip()
            
            # Save to file
            filename = f"ai_prompt_{len(list(self.output_dir.glob('*_prompt.txt'))) + 1}.txt"
            file_path = self.output_dir / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(ai_prompt)
            
            return {
                'type': 'ai_prompt',
                'file_path': str(file_path),
                'prompt': ai_prompt,
                'components': components,
                'suggested_tools': ['DALL-E 3', 'Midjourney', 'Stable Diffusion']
            }
            
        except Exception as e:
            return {'error': f"AI prompt generation failed: {str(e)}"}
    
    def generate_component_library(self, rag_suggestions: str) -> Dict[str, Any]:
        """Generate a complete component library based on RAG suggestions."""
        prompt = f"""
        Based on these design guidelines, create a complete HTML component library:
        
        {rag_suggestions}
        
        Generate an HTML page that showcases:
        1. Button variants (primary, secondary, outline, etc.)
        2. Form components (inputs, selects, checkboxes)
        3. Navigation components
        4. Card components
        5. Typography examples
        6. Color palette
        7. Spacing examples
        
        Make it a beautiful, interactive component showcase with embedded CSS.
        Include documentation for each component.
        """
        
        try:
            response = self.llm.generate_content(prompt)
            html_content = response.text
            
            # Clean up the response
            if '```html' in html_content:
                html_content = html_content.split('```html')[1].split('```')[0].strip()
            elif '```' in html_content:
                html_content = html_content.split('```')[1].strip()
            
            # Save to file
            filename = "component_library.html"
            file_path = self.output_dir / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return {
                'type': 'component_library',
                'file_path': str(file_path),
                'preview_url': f"file://{file_path.absolute()}",
                'content': html_content
            }
            
        except Exception as e:
            return {'error': f"Component library generation failed: {str(e)}"}
    
    def create_design_variations(self, base_design: Dict[str, Any], num_variations: int = 3) -> List[Dict[str, Any]]:
        """Create multiple design variations from a base design."""
        variations = []
        
        for i in range(num_variations):
            style_prompts = [
                "modern and minimalist with lots of white space",
                "bold and colorful with strong visual hierarchy",
                "elegant and sophisticated with subtle shadows"
            ]
            
            style = style_prompts[i % len(style_prompts)]
            
            # Generate variation based on original but with different style
            if base_design.get('type') == 'html':
                variation_prompt = f"""
                Take this design concept and create a {style} variation:
                
                Original components: {base_design.get('components', [])}
                
                Create a new HTML page with the same components but {style} styling.
                Make it completely different visually while maintaining functionality.
                """
                
                try:
                    response = self.llm.generate_content(variation_prompt)
                    html_content = response.text
                    
                    if '```html' in html_content:
                        html_content = html_content.split('```html')[1].split('```')[0].strip()
                    elif '```' in html_content:
                        html_content = html_content.split('```')[1].strip()
                    
                    filename = f"variation_{i+1}_{len(list(self.output_dir.glob('variation_*.html')))}.html"
                    file_path = self.output_dir / filename
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    
                    variations.append({
                        'type': 'html_variation',
                        'style': style,
                        'file_path': str(file_path),
                        'preview_url': f"file://{file_path.absolute()}"
                    })
                    
                except Exception as e:
                    variations.append({'error': f"Variation {i+1} failed: {str(e)}"})
        
        return variations 
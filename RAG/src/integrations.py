"""
Real GitHub and Figma integrations for Sketch2Answer
These replace the placeholder methods in rag_system.py
"""

import os
import requests
import json
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class GitHubIntegration:
    """
    Fetches documentation, README files, and code examples from GitHub repos.
    Useful for: component libraries, design systems, implementation guides
    """
    
    def __init__(self):
        self.token = os.getenv('GITHUB_TOKEN')
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }
    
    def fetch_repo_docs(self, repo_url: str) -> List[Dict[str, Any]]:
        """
        Fetch documentation from a GitHub repository.
        
        Args:
            repo_url: GitHub repo URL (e.g., 'owner/repo-name')
            
        Returns:
            List of documents with content and metadata
        """
        if not self.token:
            return []
        
        documents = []
        
        try:
            # Get README files
            readme_content = self._get_readme(repo_url)
            if readme_content:
                documents.append({
                    'content': readme_content,
                    'title': f'{repo_url} README',
                    'type': 'readme',
                    'source': 'github',
                    'repo': repo_url
                })
            
            # Get documentation files
            docs = self._get_docs_folder(repo_url)
            documents.extend(docs)
            
            # Get component examples (if it's a UI library)
            components = self._get_component_examples(repo_url)
            documents.extend(components)
            
        except Exception as e:
            print(f"Error fetching GitHub docs: {e}")
        
        return documents
    
    def _get_readme(self, repo_url: str) -> Optional[str]:
        """Get README.md content from repository."""
        url = f"https://api.github.com/repos/{repo_url}/readme"
        
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            content = response.json()
            # Decode base64 content
            import base64
            return base64.b64decode(content['content']).decode('utf-8')
        return None
    
    def _get_docs_folder(self, repo_url: str) -> List[Dict[str, Any]]:
        """Get documentation files from docs/ folder."""
        documents = []
        
        # Common documentation paths
        doc_paths = ['docs', 'documentation', 'wiki', '.github']
        
        for path in doc_paths:
            url = f"https://api.github.com/repos/{repo_url}/contents/{path}"
            
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                files = response.json()
                
                for file in files:
                    if file['name'].endswith(('.md', '.txt', '.rst')):
                        content = self._get_file_content(file['download_url'])
                        if content:
                            documents.append({
                                'content': content,
                                'title': f"{repo_url}/{path}/{file['name']}",
                                'type': 'documentation',
                                'source': 'github',
                                'repo': repo_url,
                                'file_path': file['path']
                            })
        
        return documents
    
    def _get_component_examples(self, repo_url: str) -> List[Dict[str, Any]]:
        """Get component examples and stories."""
        documents = []
        
        # Look for Storybook stories, component examples
        example_paths = [
            'src/components',
            'components',
            'stories',
            'examples'
        ]
        
        for path in example_paths:
            url = f"https://api.github.com/repos/{repo_url}/contents/{path}"
            
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                try:
                    files = response.json()
                    for file in files:
                        if file['name'].endswith(('.stories.js', '.example.jsx', '.md')):
                            content = self._get_file_content(file['download_url'])
                            if content:
                                documents.append({
                                    'content': content,
                                    'title': f"Component: {file['name']}",
                                    'type': 'component_example',
                                    'source': 'github',
                                    'repo': repo_url,
                                    'component': file['name'].split('.')[0]
                                })
                except:
                    continue
        
        return documents
    
    def _get_file_content(self, download_url: str) -> Optional[str]:
        """Download file content from GitHub."""
        try:
            response = requests.get(download_url)
            if response.status_code == 200:
                return response.text
        except:
            pass
        return None


class FigmaIntegration:
    """
    Fetches design system documentation and component specs from Figma.
    Useful for: design guidelines, component specifications, style guides
    """
    
    def __init__(self):
        self.token = os.getenv('FIGMA_TOKEN')
        self.headers = {
            'X-Figma-Token': self.token
        }
        self.base_url = 'https://api.figma.com/v1'
    
    def fetch_design_system(self, file_key: str) -> List[Dict[str, Any]]:
        """
        Fetch design system documentation from a Figma file.
        
        Args:
            file_key: Figma file ID from URL (e.g., file/FILE_KEY/Project-Name)
            
        Returns:
            List of design system documents
        """
        if not self.token:
            return []
        
        documents = []
        
        try:
            # Get file information
            file_info = self._get_file_info(file_key)
            if file_info:
                documents.append({
                    'content': self._parse_file_info(file_info),
                    'title': f"Figma Design System: {file_info.get('name', 'Unnamed')}",
                    'type': 'design_system',
                    'source': 'figma',
                    'file_key': file_key
                })
            
            # Get component specifications
            components = self._get_components(file_key)
            documents.extend(components)
            
            # Get styles (colors, typography, etc.)
            styles = self._get_styles(file_key)
            if styles:
                documents.append({
                    'content': styles,
                    'title': 'Design System Styles',
                    'type': 'style_guide',
                    'source': 'figma',
                    'file_key': file_key
                })
            
        except Exception as e:
            print(f"Error fetching Figma data: {e}")
        
        return documents
    
    def _get_file_info(self, file_key: str) -> Optional[Dict]:
        """Get basic file information from Figma."""
        url = f"{self.base_url}/files/{file_key}"
        
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        return None
    
    def _parse_file_info(self, file_info: Dict) -> str:
        """Parse Figma file info into readable documentation."""
        content = f"Design System: {file_info.get('name', 'Unnamed')}\n\n"
        
        if 'document' in file_info and 'children' in file_info['document']:
            content += "Pages:\n"
            for page in file_info['document']['children']:
                content += f"- {page.get('name', 'Unnamed Page')}\n"
                
                # Parse frames (components, screens, etc.)
                if 'children' in page:
                    for frame in page['children']:
                        if frame.get('type') == 'FRAME':
                            content += f"  • {frame.get('name', 'Unnamed Frame')}\n"
        
        return content
    
    def _get_components(self, file_key: str) -> List[Dict[str, Any]]:
        """Get component definitions from Figma file."""
        documents = []
        
        # Get published components
        url = f"{self.base_url}/files/{file_key}/components"
        
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            components = response.json().get('meta', {}).get('components', [])
            
            for component in components:
                content = f"Component: {component.get('name', 'Unnamed')}\n"
                content += f"Description: {component.get('description', 'No description')}\n"
                
                documents.append({
                    'content': content,
                    'title': f"Component: {component.get('name', 'Unnamed')}",
                    'type': 'component_spec',
                    'source': 'figma',
                    'component_id': component.get('key'),
                    'file_key': file_key
                })
        
        return documents
    
    def _get_styles(self, file_key: str) -> Optional[str]:
        """Get style guide (colors, typography) from Figma."""
        url = f"{self.base_url}/files/{file_key}/styles"
        
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            styles = response.json().get('meta', {}).get('styles', [])
            
            content = "Design System Styles:\n\n"
            
            # Group styles by type
            style_types = {}
            for style in styles:
                style_type = style.get('styleType', 'OTHER')
                if style_type not in style_types:
                    style_types[style_type] = []
                style_types[style_type].append(style)
            
            for style_type, type_styles in style_types.items():
                content += f"{style_type}:\n"
                for style in type_styles:
                    content += f"- {style.get('name', 'Unnamed')}: {style.get('description', '')}\n"
                content += "\n"
            
            return content
        
        return None


# Example usage configuration
EXAMPLE_INTEGRATIONS = {
    'github_repos': [
        'microsoft/fluentui',  # Fluent UI components
        'chakra-ui/chakra-ui',  # Chakra UI components
        'mui/material-ui',      # Material-UI components
        'your-org/design-system'  # Your own design system
    ],
    'figma_files': [
        'your-design-system-file-key',  # Your Figma design system
        'component-library-file-key'    # Component specifications
    ]
} 
import os
import chromadb
from chromadb.config import Settings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from typing import List, Dict, Any, Optional
import json
import requests
from pathlib import Path
from dotenv import load_dotenv
from .integrations import GitHubIntegration, FigmaIntegration

load_dotenv()

class Sketch2AnswerRAG:
    """
    RAG system that retrieves relevant information from multiple sources
    (Figma docs, dev notes, codebase) to answer questions about sketches.
    """
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        self.chunk_size = int(os.getenv('CHUNK_SIZE', 1000))
        self.chunk_overlap = int(os.getenv('CHUNK_OVERLAP', 200))
        self.top_k = int(os.getenv('TOP_K_RESULTS', 5))
        
        # Initialize Gemini
        self.api_key = os.getenv('GOOGLE_API_KEY')
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.llm = genai.GenerativeModel('gemini-1.5-flash')
        
        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name="sketch2answer_docs",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Text splitter for documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
        )
        
        # Initialize integrations
        self.github_integration = GitHubIntegration() if os.getenv('GITHUB_TOKEN') else None
        self.figma_integration = FigmaIntegration() if os.getenv('FIGMA_TOKEN') else None
        
        # Data sources configuration
        self.data_sources = {
            'figma': {
                'enabled': bool(os.getenv('FIGMA_TOKEN')),
                'token': os.getenv('FIGMA_TOKEN'),
                'files': os.getenv('FIGMA_FILES', '').split(',') if os.getenv('FIGMA_FILES') else []
            },
            'github': {
                'enabled': bool(os.getenv('GITHUB_TOKEN')),
                'token': os.getenv('GITHUB_TOKEN'),
                'repos': os.getenv('GITHUB_REPOS', '').split(',') if os.getenv('GITHUB_REPOS') else []
            },
            'local_docs': {
                'enabled': True,
                'path': './docs'
            }
        }
    
    def ingest_documents(self, source_type: str = 'all'):
        """
        Ingest documents from various sources into the vector database.
        
        Args:
            source_type: 'figma', 'github', 'local_docs', or 'all'
        """
        if source_type == 'all':
            for source in self.data_sources.keys():
                if self.data_sources[source]['enabled']:
                    self._ingest_source(source)
        else:
            if self.data_sources.get(source_type, {}).get('enabled'):
                self._ingest_source(source_type)
    
    def _ingest_source(self, source_type: str):
        """Ingest documents from a specific source."""
        print(f"Ingesting documents from {source_type}...")
        
        try:
            if source_type == 'figma':
                documents = self._fetch_figma_docs()
            elif source_type == 'github':
                documents = self._fetch_github_docs()
            elif source_type == 'local_docs':
                documents = self._load_local_docs()
            else:
                print(f"Unknown source type: {source_type}")
                return
            
            # Process and store documents
            for doc in documents:
                self._process_and_store_document(doc, source_type)
                
            print(f"Successfully ingested {len(documents)} documents from {source_type}")
            
        except Exception as e:
            print(f"Error ingesting from {source_type}: {str(e)}")
    
    def _fetch_figma_docs(self) -> List[Dict[str, Any]]:
        """Fetch design documentation from Figma API."""
        if not self.figma_integration:
            print("Figma integration not available - token not configured")
            return []
        
        documents = []
        figma_files = self.data_sources['figma']['files']
        
        if not figma_files or figma_files == ['']:
            print("No Figma files configured in FIGMA_FILES environment variable")
            return []
        
        for file_key in figma_files:
            file_key = file_key.strip()
            if file_key:
                try:
                    print(f"Fetching Figma file: {file_key}")
                    docs = self.figma_integration.fetch_design_system(file_key)
                    documents.extend(docs)
                    print(f"Retrieved {len(docs)} documents from Figma file {file_key}")
                except Exception as e:
                    print(f"Error fetching Figma file {file_key}: {e}")
        
        return documents
    
    def _fetch_github_docs(self) -> List[Dict[str, Any]]:
        """Fetch documentation from GitHub repositories."""
        if not self.github_integration:
            print("GitHub integration not available - token not configured")
            return []
        
        documents = []
        github_repos = self.data_sources['github']['repos']
        
        if not github_repos or github_repos == ['']:
            print("No GitHub repos configured in GITHUB_REPOS environment variable")
            return []
        
        for repo in github_repos:
            repo = repo.strip()
            if repo:
                try:
                    print(f"Fetching GitHub repo: {repo}")
                    docs = self.github_integration.fetch_repo_docs(repo)
                    documents.extend(docs)
                    print(f"Retrieved {len(docs)} documents from GitHub repo {repo}")
                except Exception as e:
                    print(f"Error fetching GitHub repo {repo}: {e}")
        
        return documents
    
    def _load_local_docs(self) -> List[Dict[str, Any]]:
        """Load documents from local docs directory."""
        docs_path = Path(self.data_sources['local_docs']['path'])
        documents = []
        
        # Create docs directory if it doesn't exist
        docs_path.mkdir(exist_ok=True)
        
        # Create sample documentation if directory is empty
        if not any(docs_path.iterdir()):
            self._create_sample_docs(docs_path)
        
        # Load all text files from docs directory
        for file_path in docs_path.glob('**/*.txt'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    documents.append({
                        'content': content,
                        'title': file_path.stem,
                        'type': 'local_doc',
                        'source': 'local_docs',
                        'file_path': str(file_path)
                    })
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
        
        return documents
    
    def _create_sample_docs(self, docs_path: Path):
        """Create sample documentation files."""
        sample_docs = {
            'ui_patterns.txt': """
# UI Design Patterns and Best Practices

## Layout Patterns
1. Grid System
   - Use 8px or 4px grid for consistent spacing
   - Maintain visual hierarchy with clear content sections
   - Implement responsive breakpoints for different screen sizes

2. Navigation Patterns
   - Top navigation for main sections
   - Side navigation for complex applications
   - Breadcrumbs for deep hierarchies
   - Mobile-first hamburger menu

3. Content Organization
   - Card-based layouts for content blocks
   - List views for data-heavy interfaces
   - Tabbed interfaces for related content
   - Modal dialogs for focused interactions

## Component Guidelines
1. Buttons
   - Primary actions: Solid, high-contrast buttons
   - Secondary actions: Outlined or ghost buttons
   - Destructive actions: Red or warning colors
   - Consistent padding and border-radius

2. Forms
   - Clear input labels and placeholders
   - Inline validation feedback
   - Error states with helpful messages
   - Success states with confirmation

3. Typography
   - Clear hierarchy with distinct heading sizes
   - Readable body text (16px minimum)
   - Consistent font families
   - Proper line height and letter spacing

## Color and Contrast
1. Color System
   - Primary brand colors
   - Secondary accent colors
   - Semantic colors (success, warning, error)
   - Neutral grays for text and backgrounds

2. Accessibility
   - WCAG 2.1 AA compliance
   - Minimum contrast ratio of 4.5:1
   - Color not as sole indicator
   - Focus states for keyboard navigation

## Interaction Design
1. Feedback
   - Loading states
   - Success/error messages
   - Progress indicators
   - Hover and active states

2. Gestures
   - Swipe for mobile
   - Drag and drop
   - Pinch to zoom
   - Pull to refresh

## Responsive Design
1. Breakpoints
   - Mobile: 320px - 480px
   - Tablet: 481px - 768px
   - Desktop: 769px - 1024px
   - Large Desktop: 1025px+

2. Mobile Considerations
   - Touch targets (minimum 44x44px)
   - Simplified navigation
   - Optimized images
   - Reduced content density
""",
            'accessibility.txt': """
# Web Accessibility Guidelines

## Core Principles
1. Perceivable
   - Text alternatives for non-text content
   - Captions and transcripts for media
   - Content adaptable and distinguishable

2. Operable
   - Keyboard accessible
   - Enough time to read and use
   - No content that causes seizures
   - Navigable and findable

3. Understandable
   - Readable and predictable
   - Input assistance
   - Consistent navigation
   - Error identification

4. Robust
   - Compatible with assistive technologies
   - Valid HTML and CSS
   - ARIA roles and labels
   - Semantic markup

## Implementation Guidelines
1. Semantic HTML
   - Use proper heading hierarchy
   - Landmark regions (header, nav, main, footer)
   - Lists for related items
   - Tables for tabular data

2. ARIA Implementation
   - Roles for custom components
   - Labels for interactive elements
   - Live regions for dynamic content
   - State management

3. Keyboard Navigation
   - Focus management
   - Skip links
   - Logical tab order
   - Keyboard shortcuts

4. Color and Contrast
   - Text contrast ratios
   - Color not as sole indicator
   - Focus indicators
   - High contrast mode support
""",
            'performance.txt': """
# Performance Optimization Guidelines

## Core Web Vitals
1. Largest Contentful Paint (LCP)
   - Optimize hero images
   - Implement lazy loading
   - Use responsive images
   - Optimize server response time

2. First Input Delay (FID)
   - Minimize JavaScript execution
   - Use web workers
   - Implement code splitting
   - Optimize event handlers

3. Cumulative Layout Shift (CLS)
   - Set image dimensions
   - Reserve space for dynamic content
   - Avoid inserting content above existing
   - Use transform animations

## Resource Optimization
1. Images
   - Use modern formats (WebP, AVIF)
   - Implement responsive images
   - Lazy loading
   - Image compression

2. JavaScript
   - Code splitting
   - Tree shaking
   - Minification
   - Async/defer loading

3. CSS
   - Critical CSS
   - Minification
   - Remove unused styles
   - Optimize selectors

4. Fonts
   - Font subsetting
   - Preload critical fonts
   - Use system fonts
   - Implement font-display
""",
            'mobile_design.txt': """
# Mobile Design Guidelines

## Core Principles
1. Touch-First Design
   - Large touch targets (min 44x44px)
   - Adequate spacing between elements
   - Clear touch feedback
   - Gesture support

2. Content Prioritization
   - Progressive disclosure
   - Critical content first
   - Simplified navigation
   - Reduced content density

3. Mobile Navigation
   - Bottom navigation bar
   - Hamburger menu
   - Tab bars
   - Gesture-based navigation

4. Mobile Forms
   - Simplified input fields
   - Native input types
   - Clear validation
   - Easy error correction

## Mobile-Specific Patterns
1. Lists and Cards
   - Swipeable cards
   - Pull to refresh
   - Infinite scroll
   - Skeleton loading

2. Mobile Gestures
   - Swipe actions
   - Pinch to zoom
   - Double tap
   - Long press

3. Mobile Feedback
   - Haptic feedback
   - Visual feedback
   - Sound feedback
   - Loading states

4. Mobile Performance
   - Optimized images
   - Reduced animations
   - Efficient scrolling
   - Battery optimization
""",
            'design_systems.txt': """
# Design System Guidelines

## Core Components
1. Color System
   - Primary colors
   - Secondary colors
   - Semantic colors
   - Neutral palette
   - Dark mode support

2. Typography
   - Type scale
   - Font families
   - Line heights
   - Letter spacing
   - Text styles

3. Spacing
   - Spacing scale
   - Grid system
   - Component spacing
   - Layout spacing
   - Responsive spacing

4. Components
   - Buttons
   - Inputs
   - Cards
   - Navigation
   - Modals
   - Alerts
   - Tables
   - Lists

## Design Tokens
1. Colors
   - Brand colors
   - UI colors
   - State colors
   - Background colors
   - Text colors

2. Typography
   - Font sizes
   - Font weights
   - Line heights
   - Font families
   - Text styles

3. Spacing
   - Base unit
   - Spacing scale
   - Component spacing
   - Layout spacing

4. Breakpoints
   - Mobile
   - Tablet
   - Desktop
   - Large desktop

## Component Guidelines
1. Button System
   - Primary buttons
   - Secondary buttons
   - Tertiary buttons
   - Icon buttons
   - Button states

2. Form Elements
   - Text inputs
   - Select inputs
   - Checkboxes
   - Radio buttons
   - Form validation

3. Navigation
   - Top navigation
   - Side navigation
   - Breadcrumbs
   - Pagination
   - Tabs

4. Feedback
   - Alerts
   - Toasts
   - Progress indicators
   - Loading states
   - Error states
""",
            'interaction_patterns.txt': """
# Interaction Design Patterns

## Navigation Patterns
1. Global Navigation
   - Top navigation bar
   - Side navigation
   - Bottom navigation
   - Breadcrumbs
   - Search

2. Local Navigation
   - Tabs
   - Accordions
   - Tree views
   - Pagination
   - Infinite scroll

3. Contextual Navigation
   - Related links
   - Quick actions
   - Context menus
   - Tooltips
   - Help text

## Input Patterns
1. Form Patterns
   - Single column forms
   - Multi-step forms
   - Inline forms
   - Dynamic forms
   - Form validation

2. Selection Patterns
   - Dropdowns
   - Checkboxes
   - Radio buttons
   - Toggle switches
   - Date pickers

3. Search Patterns
   - Search bars
   - Filters
   - Faceted search
   - Autocomplete
   - Search results

## Feedback Patterns
1. Status Feedback
   - Loading states
   - Progress indicators
   - Success messages
   - Error messages
   - Empty states

2. Action Feedback
   - Hover states
   - Active states
   - Focus states
   - Disabled states
   - Selected states

3. System Feedback
   - Notifications
   - Alerts
   - Toasts
   - Modals
   - Confirmations
""",
            'visual_hierarchy.txt': """
# Visual Hierarchy Guidelines

## Typography Hierarchy
1. Headings
   - H1: Main page title
   - H2: Section headers
   - H3: Subsection headers
   - H4: Card headers
   - H5: Small headers
   - H6: Minor headers

2. Body Text
   - Large body text
   - Regular body text
   - Small body text
   - Caption text
   - Label text

3. Emphasis
   - Bold text
   - Italic text
   - Underlined text
   - Colored text
   - Highlighted text

## Layout Hierarchy
1. Content Sections
   - Hero section
   - Feature section
   - Content section
   - Call-to-action
   - Footer

2. Component Hierarchy
   - Primary components
   - Secondary components
   - Tertiary components
   - Supporting elements
   - Decorative elements

3. Information Architecture
   - Main content
   - Side content
   - Supporting content
   - Navigation
   - Footer content

## Visual Weight
1. Size
   - Large elements
   - Medium elements
   - Small elements
   - Micro elements
   - Icon sizes

2. Color
   - Primary colors
   - Secondary colors
   - Accent colors
   - Neutral colors
   - Semantic colors

3. Contrast
   - High contrast
   - Medium contrast
   - Low contrast
   - Background contrast
   - Text contrast
""",
            'responsive_design.txt': """
# Responsive Design Guidelines

## Breakpoint Strategy
1. Mobile First
   - Base styles
   - Mobile enhancements
   - Tablet breakpoint
   - Desktop breakpoint
   - Large screen breakpoint

2. Content Adaptation
   - Fluid grids
   - Flexible images
   - Media queries
   - Content reordering
   - Component adaptation

3. Layout Patterns
   - Single column
   - Multi-column
   - Grid layout
   - Card layout
   - List layout

## Mobile Considerations
1. Touch Targets
   - Minimum size
   - Spacing
   - Hit areas
   - Touch feedback
   - Gesture support

2. Content Display
   - Progressive disclosure
   - Content prioritization
   - Simplified navigation
   - Reduced content
   - Mobile-specific features

3. Performance
   - Optimized images
   - Reduced animations
   - Efficient scrolling
   - Battery optimization
   - Network optimization

## Desktop Considerations
1. Layout
   - Multi-column
   - Side navigation
   - Complex interactions
   - Rich content
   - Advanced features

2. Interaction
   - Hover states
   - Keyboard navigation
   - Mouse interactions
   - Complex gestures
   - Advanced controls

3. Content
   - Rich media
   - Complex data
   - Advanced features
   - Detailed information
   - Multiple views
""",
            'color_systems.txt': """
# Color System Guidelines

## Color Palette
1. Primary Colors
   - Brand colors
   - Main actions
   - Key elements
   - Brand identity
   - Core UI

2. Secondary Colors
   - Supporting elements
   - Secondary actions
   - Accent elements
   - Highlights
   - Variations

3. Semantic Colors
   - Success
   - Warning
   - Error
   - Info
   - Neutral

## Color Usage
1. Background Colors
   - Primary background
   - Secondary background
   - Surface colors
   - Overlay colors
   - Modal backgrounds

2. Text Colors
   - Primary text
   - Secondary text
   - Disabled text
   - Link text
   - Heading text

3. Border Colors
   - Primary borders
   - Secondary borders
   - Divider colors
   - Focus borders
   - Error borders

## Color Accessibility
1. Contrast Ratios
   - Text contrast
   - UI contrast
   - Icon contrast
   - Border contrast
   - Background contrast

2. Color Blindness
   - Red-green
   - Blue-yellow
   - Monochromatic
   - Color alternatives
   - Pattern usage

3. Dark Mode
   - Dark backgrounds
   - Light text
   - Accent colors
   - Surface colors
   - Contrast adjustments
""",
            'data_visualization.txt': """
# Data Visualization Guidelines

## Chart Types
1. Basic Charts
   - Bar charts
   - Line charts
   - Pie charts
   - Area charts
   - Scatter plots

2. Advanced Charts
   - Heat maps
   - Bubble charts
   - Radar charts
   - Tree maps
   - Sankey diagrams

3. Interactive Charts
   - Zoomable charts
   - Drill-down charts
   - Animated charts
   - Real-time updates
   - Custom interactions

## Data Visualization Principles
1. Clarity
   - Clear labels
   - Consistent scales
   - Proper spacing
   - Readable fonts
   - Appropriate colors

2. Accuracy
   - Correct data representation
   - Proper scaling
   - Accurate proportions
   - Clear data points
   - Valid comparisons

3. Accessibility
   - Color blind friendly
   - Screen reader support
   - Keyboard navigation
   - Alternative text
   - High contrast options

## Implementation Guidelines
1. Responsive Design
   - Mobile-friendly charts
   - Adaptive layouts
   - Touch interactions
   - Responsive scales
   - Dynamic resizing

2. Performance
   - Data optimization
   - Lazy loading
   - Caching strategies
   - Efficient rendering
   - Memory management

3. Interactivity
   - Hover states
   - Click actions
   - Tooltips
   - Filters
   - Sorting options
""",
            'microinteractions.txt': """
# Microinteractions Guidelines

## Core Principles
1. Purpose
   - User feedback
   - Status indication
   - Action confirmation
   - Error prevention
   - Delight moments

2. Design Elements
   - Motion
   - Sound
   - Haptics
   - Visual feedback
   - Timing

3. Implementation
   - Performance
   - Accessibility
   - Consistency
   - Subtlety
   - Responsiveness

## Common Patterns
1. Button States
   - Hover effects
   - Click animations
   - Loading states
   - Success feedback
   - Error states

2. Form Interactions
   - Input focus
   - Validation feedback
   - Auto-complete
   - Character count
   - Password strength

3. Navigation
   - Menu transitions
   - Page transitions
   - Scroll effects
   - Back navigation
   - Progress indicators

## Best Practices
1. Animation
   - Natural motion
   - Appropriate timing
   - Smooth transitions
   - Performance optimization
   - Reduced motion option

2. Feedback
   - Immediate response
   - Clear indication
   - Appropriate intensity
   - Consistent patterns
   - Error prevention

3. Accessibility
   - Keyboard support
   - Screen reader compatibility
   - Reduced motion
   - High contrast
   - Focus management
""",
            'design_psychology.txt': """
# Design Psychology Guidelines

## User Behavior
1. Cognitive Load
   - Information hierarchy
   - Progressive disclosure
   - Chunking content
   - Clear navigation
   - Minimal distractions

2. User Motivation
   - Clear value proposition
   - Progress indicators
   - Achievement markers
   - Social proof
   - Personalization

3. Decision Making
   - Clear choices
   - Default options
   - Guided decisions
   - Risk reduction
   - Trust building

## Emotional Design
1. Visual Appeal
   - Color psychology
   - Typography impact
   - Image selection
   - Layout harmony
   - Brand consistency

2. User Experience
   - Flow states
   - Engagement patterns
   - Emotional triggers
   - Delight moments
   - Trust signals

3. Brand Connection
   - Personality traits
   - Voice and tone
   - Visual identity
   - Interaction style
   - Value alignment

## Implementation
1. User Research
   - User interviews
   - Behavior analysis
   - A/B testing
   - Analytics review
   - Feedback loops

2. Design Process
   - User-centered design
   - Iterative development
   - Continuous testing
   - Data-driven decisions
   - User feedback

3. Evaluation
   - Usability testing
   - Performance metrics
   - User satisfaction
   - Conversion rates
   - Engagement levels
""",
            'design_systems_advanced.txt': """
# Advanced Design System Guidelines

## Component Architecture
1. Atomic Design
   - Atoms
   - Molecules
   - Organisms
   - Templates
   - Pages

2. Component Patterns
   - Composition
   - Inheritance
   - Variants
   - States
   - Behaviors

3. Component Library
   - Documentation
   - Code examples
   - Usage guidelines
   - Best practices
   - Version control

## Design Tokens
1. Foundation
   - Colors
   - Typography
   - Spacing
   - Breakpoints
   - Elevation

2. Components
   - Buttons
   - Forms
   - Cards
   - Navigation
   - Feedback

3. Patterns
   - Layout
   - Grid
   - Motion
   - Interaction
   - Animation

## Implementation
1. Development
   - Component architecture
   - Code organization
   - Testing strategy
   - Documentation
   - Versioning

2. Maintenance
   - Updates
   - Deprecation
   - Migration
   - Performance
   - Security

3. Distribution
   - Package management
   - Version control
   - Documentation
   - Support
   - Updates
""",
            'accessibility_advanced.txt': """
# Advanced Accessibility Guidelines

## WCAG 2.1 Guidelines
1. Perceivable
   - Text alternatives
   - Time-based media
   - Adaptable content
   - Distinguishable content

2. Operable
   - Keyboard accessible
   - Enough time
   - Seizures and physical reactions
   - Navigable
   - Input modalities

3. Understandable
   - Readable
   - Predictable
   - Input assistance

4. Robust
   - Compatible
   - Valid HTML
   - ARIA implementation
   - Screen reader support

## Implementation
1. Semantic HTML
   - Proper structure
   - ARIA roles
   - Landmarks
   - Headings
   - Lists

2. Keyboard Navigation
   - Focus management
   - Tab order
   - Skip links
   - Keyboard shortcuts
   - Focus indicators

3. Screen Readers
   - ARIA labels
   - Live regions
   - Announcements
   - Alternative text
   - Descriptions

## Testing
1. Automated Testing
   - HTML validation
   - ARIA validation
   - Color contrast
   - Keyboard navigation
   - Screen reader testing

2. Manual Testing
   - User testing
   - Screen reader testing
   - Keyboard testing
   - Color blindness testing
   - Mobile testing

3. Documentation
   - Accessibility statement
   - Testing results
   - Implementation guides
   - Best practices
   - Compliance reports
""",
            'performance_optimization.txt': """
# Performance Optimization Guidelines

## Core Web Vitals
1. Loading Performance
   - First Contentful Paint
   - Largest Contentful Paint
   - Time to Interactive
   - First Input Delay
   - Total Blocking Time

2. Visual Stability
   - Cumulative Layout Shift
   - Layout shifts
   - Image dimensions
   - Dynamic content
   - Animation impact

3. Interactivity
   - First Input Delay
   - Time to Interactive
   - Event handling
   - JavaScript execution
   - Main thread blocking

## Optimization Techniques
1. Resource Loading
   - Code splitting
   - Lazy loading
   - Preloading
   - Prefetching
   - Resource hints

2. Asset Optimization
   - Image optimization
   - Font optimization
   - CSS optimization
   - JavaScript optimization
   - Cache strategies

3. Server Optimization
   - CDN usage
   - Compression
   - Caching
   - Server timing
   - Response optimization

## Monitoring
1. Performance Metrics
   - Real User Monitoring
   - Synthetic monitoring
   - Error tracking
   - User experience
   - Business metrics

2. Analysis
   - Performance budgets
   - Bottleneck identification
   - Optimization opportunities
   - Impact assessment
   - ROI calculation

3. Reporting
   - Performance dashboards
   - Alert systems
   - Trend analysis
   - Compliance reporting
   - Optimization tracking
"""
        }
        
        for filename, content in sample_docs.items():
            file_path = docs_path / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content.strip())
    
    def _process_and_store_document(self, document: Dict[str, Any], source_type: str):
        """Process a document and store it in the vector database."""
        # Split document into chunks
        chunks = self.text_splitter.split_text(document['content'])
        
        # Generate embeddings and store
        for i, chunk in enumerate(chunks):
            # Create unique ID
            doc_id = f"{source_type}_{document.get('title', 'untitled')}_{i}"
            
            # Generate embedding
            embedding = self.embeddings.embed_query(chunk)
            
            # Store in ChromaDB
            self.collection.add(
                embeddings=[embedding],
                documents=[chunk],
                metadatas=[{
                    'source': source_type,
                    'title': document.get('title', ''),
                    'type': document.get('type', ''),
                    'chunk_index': i
                }],
                ids=[doc_id]
            )
    
    def search_relevant_docs(self, queries: List[str], top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Search for relevant documents based on multiple queries.
        
        Args:
            queries: List of search queries
            top_k: Number of results to return per query
            
        Returns:
            List of relevant document chunks with metadata
        """
        if top_k is None:
            top_k = self.top_k
        
        all_results = []
        seen_docs = set()
        
        for query in queries:
            # Generate embedding for query
            query_embedding = self.embeddings.embed_query(query)
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            # Process results
            for i in range(len(results['documents'][0])):
                doc_id = results['ids'][0][i]
                if doc_id not in seen_docs:
                    seen_docs.add(doc_id)
                    all_results.append({
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i] if 'distances' in results else 0,
                        'query': query
                    })
        
        # Sort by relevance (distance) and return top results
        all_results.sort(key=lambda x: x['distance'])
        return all_results[:top_k * 2]  # Return more results for better context
    
    def generate_answer(self, question: str, sketch_analysis: Dict[str, Any], relevant_docs: List[Dict[str, Any]]) -> str:
        """
        Generate an answer using Gemini based on the question, sketch analysis, and relevant docs.
        
        Args:
            question: User's question about the sketch
            sketch_analysis: Analysis result from vision processor
            relevant_docs: Relevant documents from RAG search
            
        Returns:
            Generated answer
        """
        # Prepare context
        context_parts = [
            "# Sketch Analysis Results:",
            f"Components identified: {', '.join(sketch_analysis.get('components_identified', []))}",
            f"Analysis type: {sketch_analysis.get('analysis_type', 'general')}",
            "\n# Vision Model Analysis:",
            sketch_analysis.get('raw_response', 'No analysis available'),
            "\n# Relevant Documentation:"
        ]
        
        # Add relevant documents
        for doc in relevant_docs[:5]:  # Limit to top 5 docs
            context_parts.extend([
                f"\n## {doc['metadata'].get('title', 'Document')} ({doc['metadata'].get('source', 'unknown')}):",
                doc['content'][:800] + "..." if len(doc['content']) > 800 else doc['content']
            ])
        
        context = "\n".join(context_parts)
        
        # Create prompt
        prompt = f"""
        You are an expert UI/UX designer and developer assistant. Based on the sketch analysis and relevant documentation, 
        answer the user's question comprehensively and practically.
        
        Context:
        {context}
        
        User Question: {question}
        
        Please provide a detailed, actionable answer that:
        1. Addresses the specific question about the sketch
        2. References relevant design guidelines and best practices
        3. Suggests practical implementation steps if applicable
        4. Considers accessibility and user experience
        
        Answer:
        """
        
        try:
            response = self.llm.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating answer: {str(e)}"
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the document collection."""
        try:
            count = self.collection.count()
            return {
                'total_documents': count,
                'sources_configured': {k: v['enabled'] for k, v in self.data_sources.items()},
                'persist_directory': self.persist_directory
            }
        except Exception as e:
            return {'error': str(e)} 
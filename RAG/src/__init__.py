"""
Sketch2Answer - Draw-to-RAG Interface

A system that combines computer vision with retrieval-augmented generation
to provide intelligent answers about hand-drawn sketches and wireframes.
"""

from .sketch2answer import Sketch2Answer
from .vision_processor import SketchVisionProcessor  
from .rag_system import Sketch2AnswerRAG

__version__ = "1.0.0"
__author__ = "Sketch2Answer Team"

__all__ = [
    "Sketch2Answer",
    "SketchVisionProcessor", 
    "Sketch2AnswerRAG"
] 
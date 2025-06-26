#!/usr/bin/env python3
"""
Populate RAG system with documents from GitHub and Figma
"""

import os
from dotenv import load_dotenv
from src.rag_system import Sketch2AnswerRAG

load_dotenv()

def main():
    print("🚀 Populating Sketch2Answer RAG System\n")
    
    # Initialize RAG system
    rag = Sketch2AnswerRAG()
    
    # Check initial stats
    initial_stats = rag.get_collection_stats()
    print(f"📊 Initial collection stats: {initial_stats['total_documents']} documents")
    
    # Ingest from GitHub
    print("\n📁 Ingesting from GitHub repositories...")
    github_repos = os.getenv('GITHUB_REPOS', '').split(',')
    if github_repos and github_repos != ['']:
        print(f"   Repositories: {', '.join(github_repos)}")
        rag.ingest_documents('github')
    else:
        print("   No GitHub repositories configured")
    
    # Ingest from Figma (if configured)
    print("\n🎨 Checking Figma integration...")
    figma_token = os.getenv('FIGMA_TOKEN')
    figma_files = os.getenv('FIGMA_FILES', '').split(',')
    
    if figma_token and figma_files and figma_files != ['']:
        print(f"   Figma files: {', '.join(figma_files)}")
        rag.ingest_documents('figma')
    elif figma_token:
        print("   ✅ Figma token configured, but no files specified in FIGMA_FILES")
        print("   💡 Add Figma file keys to FIGMA_FILES in config.env to use Figma integration")
    else:
        print("   ❌ Figma not configured")
    
    # Ingest local docs
    print("\n📄 Ingesting local documentation...")
    rag.ingest_documents('local_docs')
    
    # Final stats
    final_stats = rag.get_collection_stats()
    print(f"\n📊 Final collection stats:")
    print(f"   Total documents: {final_stats['total_documents']}")
    print(f"   Sources enabled: {final_stats['sources_configured']}")
    
    added_docs = final_stats['total_documents'] - initial_stats['total_documents']
    if added_docs > 0:
        print(f"\n✅ Successfully added {added_docs} new documents!")
        print("🎉 Your RAG system is ready to answer questions about UI sketches!")
    else:
        print("\n⚠️  No new documents added. Check your configuration.")
    
    # Test search functionality
    print("\n🔍 Testing search functionality...")
    test_queries = ["button component", "navigation design", "form elements"]
    
    for query in test_queries:
        results = rag.search_relevant_docs([query], top_k=2)
        print(f"   Query: '{query}' → Found {len(results)} relevant documents")
    
    print("\n✨ RAG system population complete!")

if __name__ == "__main__":
    main() 
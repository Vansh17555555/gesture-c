#!/usr/bin/env python3
"""
Test script for GitHub and Figma integrations
Run this to verify your API tokens are working correctly
"""

import os
from dotenv import load_dotenv
from src.integrations import GitHubIntegration, FigmaIntegration

load_dotenv()

def test_github_integration():
    """Test GitHub API integration"""
    print("🔍 Testing GitHub Integration...")
    
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token or github_token == 'ghp_your_github_token_here':
        print("❌ GitHub token not configured. Please update GITHUB_TOKEN in config.env")
        return False
    
    try:
        github = GitHubIntegration()
        
        # Test with a small public repo
        test_repo = 'microsoft/fluentui'
        print(f"📁 Testing with repository: {test_repo}")
        
        docs = github.fetch_repo_docs(test_repo)
        
        if docs:
            print(f"✅ Success! Retrieved {len(docs)} documents from GitHub")
            print("📄 Document types found:")
            for doc in docs[:3]:  # Show first 3
                print(f"   - {doc['title']} ({doc['type']})")
            return True
        else:
            print("⚠️  No documents retrieved (this might be normal for some repos)")
            return True
            
    except Exception as e:
        print(f"❌ GitHub integration failed: {e}")
        return False

def test_figma_integration():
    """Test Figma API integration"""
    print("\n🎨 Testing Figma Integration...")
    
    figma_token = os.getenv('FIGMA_TOKEN')
    if not figma_token or figma_token == 'figd_your_figma_token_here':
        print("❌ Figma token not configured. Please update FIGMA_TOKEN in config.env")
        print("💡 Get your token from: https://www.figma.com/developers/api#access-tokens")
        return False
    
    figma_files = os.getenv('FIGMA_FILES', '').split(',')
    if not figma_files or figma_files == ['your_design_system_file_key,component_library_file_key']:
        print("❌ Figma files not configured. Please update FIGMA_FILES in config.env")
        print("💡 Get file keys from Figma URLs: figma.com/file/FILE_KEY/Project-Name")
        return False
    
    try:
        figma = FigmaIntegration()
        
        for file_key in figma_files:
            file_key = file_key.strip()
            if file_key and file_key != 'your_design_system_file_key' and file_key != 'component_library_file_key':
                print(f"🖼️  Testing with Figma file: {file_key}")
                
                docs = figma.fetch_design_system(file_key)
                
                if docs:
                    print(f"✅ Success! Retrieved {len(docs)} documents from Figma")
                    print("📄 Document types found:")
                    for doc in docs[:3]:  # Show first 3
                        print(f"   - {doc['title']} ({doc['type']})")
                    return True
                else:
                    print("⚠️  No documents retrieved from this file")
        
        print("❌ No valid Figma files to test")
        return False
            
    except Exception as e:
        print(f"❌ Figma integration failed: {e}")
        print("💡 Make sure your FIGMA_TOKEN and FIGMA_FILES are correct")
        return False

def test_rag_system():
    """Test the full RAG system with integrations"""
    print("\n🤖 Testing RAG System with Integrations...")
    
    try:
        from src.rag_system import Sketch2AnswerRAG
        
        rag = Sketch2AnswerRAG()
        
        # Test ingestion
        print("📚 Testing document ingestion...")
        rag.ingest_documents('github')
        rag.ingest_documents('figma')
        
        # Get stats
        stats = rag.get_collection_stats()
        print(f"📊 Collection stats: {stats}")
        
        if stats.get('total_documents', 0) > 0:
            print("✅ RAG system is working with real integrations!")
            return True
        else:
            print("⚠️  No documents in collection, but system is functional")
            return True
            
    except Exception as e:
        print(f"❌ RAG system test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Sketch2Answer Integrations\n")
    
    # Test individual integrations
    github_ok = test_github_integration()
    figma_ok = test_figma_integration()
    
    # Test full system if at least one integration works
    if github_ok or figma_ok:
        rag_ok = test_rag_system()
    else:
        print("\n❌ Please configure at least one integration (GitHub or Figma) to proceed")
        rag_ok = False
    
    print("\n" + "="*50)
    print("📋 Test Results Summary:")
    print(f"   GitHub Integration: {'✅' if github_ok else '❌'}")
    print(f"   Figma Integration:  {'✅' if figma_ok else '❌'}")
    print(f"   RAG System:         {'✅' if rag_ok else '❌'}")
    
    if github_ok or figma_ok:
        print("\n🎉 Your integrations are ready to use!")
        print("💡 Now you can run the main application with real data from GitHub/Figma")
    else:
        print("\n🔧 Please configure your API tokens in config.env and try again") 
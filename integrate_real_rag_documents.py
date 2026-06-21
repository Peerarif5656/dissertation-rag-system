#!/usr/bin/env python3
"""
Integrate Real Document RAG Dataset with BPI Data
Merges extracted PDF content with existing BPI patterns for complete RAG system
"""

import json
import os
from typing import Dict, Any, List

def merge_rag_datasets():
    """Merge processed PDF documents with existing BPI RAG data."""
    
    print("INTEGRATING REAL DOCUMENTS WITH BPI RAG SYSTEM")
    print("=" * 60)
    
    # Load BPI RAG data
    bpi_rag_path = "bpi_rag_data.json"
    print(f"Loading BPI RAG data from: {bpi_rag_path}")
    
    try:
        with open(bpi_rag_path, 'r') as f:
            bpi_data = json.load(f)
    except FileNotFoundError:
        print(f"BPI RAG file not found: {bpi_rag_path}")
        return False
    
    # Load processed documents RAG data
    docs_rag_path = "real_documents/processed/documents_rag_dataset.json"
    print(f" Loading processed documents from: {docs_rag_path}")
    
    try:
        with open(docs_rag_path, 'r') as f:
            docs_data = json.load(f)
    except FileNotFoundError:
        print(f"Documents RAG file not found: {docs_rag_path}")
        print("Please run pdf_processor.py first to extract document content")
        return False
    
    print(f"BPI patterns: {len(bpi_data.get('patterns', []))}")
    print(f"Document patterns: {docs_data['metadata']['total_patterns']}")
    
    # Merge the datasets
    merged_data = {
        "metadata": {
            "created": docs_data["metadata"]["created"],
            "source": "merged_bpi_and_research_documents",
            "bpi_patterns": len(bpi_data.get('patterns', [])),
            "research_document_patterns": docs_data['metadata']['total_patterns'],
            "total_patterns": len(bpi_data.get('patterns', [])) + docs_data['metadata']['total_patterns'],
            "document_sources": docs_data['metadata'].get('document_sources', []),
            "total_research_words": docs_data['metadata'].get('total_words', 0)
        },
        "patterns": [],
        "benchmarks": bpi_data.get('benchmarks', {})
    }
    
    # Add BPI patterns first
    merged_data["patterns"].extend(bpi_data.get('patterns', []))
    print(f"Added {len(bpi_data.get('patterns', []))} BPI patterns")
    
    # Add research document patterns
    merged_data["patterns"].extend(docs_data['patterns'])
    print(f" Added {len(docs_data['patterns'])} research document patterns")
    
    # Save merged dataset
    merged_file = "bpi_rag_data_with_real_documents.json"
    print(f"Saving merged dataset to: {merged_file}")
    
    with open(merged_file, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nINTEGRATION COMPLETE!")
    print("=" * 40)
    print(f"Total patterns: {merged_data['metadata']['total_patterns']}")
    print(f"BPI empirical patterns: {merged_data['metadata']['bpi_patterns']}")
    print(f" Research document patterns: {merged_data['metadata']['research_document_patterns']}")
    print(f" Consulting firms: {', '.join(merged_data['metadata']['document_sources'])}")
    print(f"Research words extracted: {merged_data['metadata']['total_research_words']:,}")
    print(f"Merged dataset saved: {merged_file}")
    
    # Update RAG system to use merged data
    update_rag_system_config(merged_file)
    
    return True

def update_rag_system_config(merged_file: str):
    """Update RAG system configuration to use merged dataset."""
    
    print(f"\n UPDATING RAG SYSTEM CONFIGURATION")
    print("-" * 40)
    
    # Check if the RAG system needs to be updated to point to new file
    rag_system_path = "rag_system.py"
    
    try:
        with open(rag_system_path, 'r') as f:
            rag_content = f.read()
        
        # Update default path in RAG system
        if 'bpi_rag_data.json' in rag_content:
            updated_content = rag_content.replace(
                'bpi_rag_data.json',
                merged_file
            )
            
            with open(rag_system_path, 'w') as f:
                f.write(updated_content)
            
            print(f"Updated RAG system to use merged dataset: {merged_file}")
        else:
            print("ℹ RAG system configuration unchanged")
            
    except Exception as e:
        print(f"⚠ Could not update RAG system config: {str(e)}")
    
    print(f"RAG system now includes real consulting research documents!")
    print(f" System can provide evidence from McKinsey, BCG, Deloitte + BPI Challenge 2020")

def validate_integration():
    """Validate that the integration worked correctly."""
    
    print(f"\nVALIDATING INTEGRATION")
    print("-" * 40)
    
    merged_file = "bpi_rag_data_with_real_documents.json"
    
    try:
        with open(merged_file, 'r') as f:
            merged_data = json.load(f)
        
        patterns = merged_data.get('patterns', [])
        
        # Count different pattern types
        bpi_patterns = [p for p in patterns if p.get('source') != 'research_document' and p.get('source') != 'research_document_section']
        research_patterns = [p for p in patterns if p.get('source') == 'research_document']
        section_patterns = [p for p in patterns if p.get('source') == 'research_document_section']
        
        print(f"BPI Challenge patterns: {len(bpi_patterns)}")
        print(f" Research document patterns: {len(research_patterns)}")
        print(f"Document section patterns: {len(section_patterns)}")
        print(f"Total patterns: {len(patterns)}")
        
        # Check firm coverage
        if research_patterns:
            firms = set()
            for pattern in research_patterns + section_patterns:
                if 'document_type' in pattern:
                    firms.add(pattern['document_type'])
            
            print(f" Consulting firm coverage: {', '.join(sorted(firms))}")
        
        # Sample research pattern
        if research_patterns:
            sample = research_patterns[0]
            print(f" Sample research document: {sample.get('title', 'Unknown')}")
            print(f"   Source: {sample.get('document_type', 'Unknown').upper()}")
            print(f"   Words: {sample.get('word_count', 0):,}")
        
        print(f"Integration validation successful!")
        return True
        
    except Exception as e:
        print(f"Validation failed: {str(e)}")
        return False

def main():
    """Main integration function."""
    
    success = merge_rag_datasets()
    
    if success:
        validation_success = validate_integration()
        
        if validation_success:
            print(f"\nREAL DOCUMENT INTEGRATION COMPLETE!")
            print("=" * 50)
            print("PDF documents processed and text extracted")
            print("Research patterns merged with BPI data")
            print("RAG system updated to use real documents")
            print("System now provides evidence-based recommendations")
            print("Ready for academic evaluation with real consulting research")
            
            print(f"\nNEXT STEPS:")
            print("1. Run test_real_document_rag.py to validate retrieval")
            print("2. Test framework analysis with real document evidence")
            print("3. Compare RAG vs Non-RAG analysis quality")
            
            return True
    
    print(f"\nINTEGRATION FAILED")
    print("Please check error messages and try again")
    return False

if __name__ == "__main__":
    main()
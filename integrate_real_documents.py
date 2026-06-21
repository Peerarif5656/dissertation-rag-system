#!/usr/bin/env python3
"""
Integrate Real Documents into RAG System
Combines downloaded research documents with existing BPI RAG data
"""

import json
import os
from datetime import datetime
from typing import Dict, Any

def load_existing_rag_data(file_path: str = "bpi_rag_data.json") -> Dict[str, Any]:
    """Load existing BPI RAG data."""
    
    print(f"Loading existing RAG data from {file_path}...")
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        rag_data = json.load(f)
    
    print(f"Loaded {len(rag_data.get('patterns', []))} existing BPI patterns")
    return rag_data

def load_document_structure(file_path: str = "real_documents/documents_rag_structure.json") -> Dict[str, Any]:
    """Load document RAG structure."""
    
    print(f"Loading document structure from {file_path}...")
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        doc_data = json.load(f)
    
    print(f"Loaded {len(doc_data.get('patterns', []))} document patterns")
    return doc_data

def integrate_real_documents() -> str:
    """Integrate real documents into the RAG system."""
    
    print("INTEGRATING REAL DOCUMENTS INTO RAG SYSTEM")
    print("=" * 60)
    
    # Load existing BPI data
    bpi_data = load_existing_rag_data()
    if not bpi_data:
        print("Could not load BPI data")
        return None
    
    # Load document structure
    doc_data = load_document_structure()
    if not doc_data:
        print("Could not load document structure")
        return None
    
    print("\nCombining datasets...")
    
    # Combine patterns
    combined_patterns = bpi_data["patterns"].copy()
    combined_patterns.extend(doc_data["patterns"])
    
    # Create enhanced RAG data
    enhanced_rag = {
        "metadata": {
            "source": "combined_bpi_and_research_documents",
            "processed_date": bpi_data["metadata"]["processed_date"],
            "last_updated": datetime.now().isoformat(),
            "total_traces": bpi_data["metadata"].get("total_traces", 0),
            "total_patterns": len(combined_patterns),
            "bpi_patterns": len(bpi_data["patterns"]),
            "research_document_patterns": len(doc_data["patterns"]),
            "sources": [
                "bpi_challenge_2020",
                "mckinsey_research_papers",
                "bcg_research_papers", 
                "deloitte_research_papers",
                "academic_research_papers"
            ],
            "consulting_firms": [
                "McKinsey & Company",
                "Boston Consulting Group", 
                "Deloitte"
            ],
            "document_types": [
                "operating_model_transformation",
                "digital_transformation",
                "agile_transformation", 
                "business_process_mining",
                "scaled_agile_frameworks"
            ]
        },
        "patterns": combined_patterns
    }
    
    # Save enhanced RAG data
    output_file = "bpi_rag_data_with_real_documents.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(enhanced_rag, f, indent=2, ensure_ascii=False)
    
    file_size = len(json.dumps(enhanced_rag))
    
    print(f"\nINTEGRATION SUMMARY:")
    print(f"• Original BPI patterns: {len(bpi_data['patterns'])}")
    print(f"• Research document patterns: {len(doc_data['patterns'])}")
    print(f"• Total combined patterns: {len(combined_patterns)}")
    print(f"• Consulting firms included: {len(enhanced_rag['metadata']['consulting_firms'])}")
    print(f"• Enhanced RAG file: {output_file}")
    print(f"• File size: {file_size:,} characters")
    
    print(f"\nINTEGRATION COMPLETE!")
    print("RAG system now includes both empirical BPI data AND real research documents")
    print(" Ready for academic evaluation: RAG vs Non-RAG comparison")
    
    return output_file

def main():
    """Main integration function."""
    
    result = integrate_real_documents()
    
    if result:
        print(f"\nSUCCESS!")
        print("=" * 50)
        print("Real documents integrated into RAG system")
        print("Combined BPI empirical data + consulting research")
        print("System ready for academic evaluation")
        print("Multiple credible sources for evidence-based recommendations")
    else:
        print(f"\nINTEGRATION FAILED")
        print("Please ensure both BPI data and document structure files exist")
    
    return result

if __name__ == "__main__":
    main()
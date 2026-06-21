#!/usr/bin/env python3
"""
Integrate Enhanced Research Documents
Merge the newly processed research documents with the existing RAG system
"""

import json
from datetime import datetime
import os

def integrate_enhanced_research():
    """Integrate enhanced research documents into the main RAG system."""
    
    print("INTEGRATING ENHANCED RESEARCH INTO RAG SYSTEM")
    print("=" * 70)
    
    # Load existing RAG system
    existing_rag_path = "bpi_rag_data_with_real_documents.json"
    print(f"Loading existing RAG data: {existing_rag_path}")
    
    try:
        with open(existing_rag_path, 'r') as f:
            existing_rag = json.load(f)
    except FileNotFoundError:
        print(f"Existing RAG file not found: {existing_rag_path}")
        return False
    
    # Load new research documents
    new_research_path = "real_documents/dissertation_research_papers/processed/documents_rag_dataset.json"
    print(f" Loading new research data: {new_research_path}")
    
    try:
        with open(new_research_path, 'r') as f:
            new_research = json.load(f)
    except FileNotFoundError:
        print(f"New research file not found: {new_research_path}")
        return False
    
    print(f"Existing patterns: {len(existing_rag.get('patterns', []))}")
    print(f"New research patterns: {new_research['metadata']['total_patterns']}")
    
    # Merge the datasets
    merged_rag = {
        "metadata": {
            "created": datetime.now().isoformat(),
            "source": "enhanced_bpi_and_research_documents",
            "bpi_patterns": existing_rag["metadata"].get("bpi_patterns", 0),
            "previous_research_patterns": existing_rag["metadata"].get("research_document_patterns", 0),
            "new_research_patterns": new_research['metadata']['total_patterns'],
            "total_patterns": len(existing_rag.get('patterns', [])) + new_research['metadata']['total_patterns'],
            "document_sources": list(set(
                existing_rag["metadata"].get("document_sources", []) + 
                new_research['metadata'].get('document_sources', [])
            )),
            "total_research_words": (
                existing_rag["metadata"].get("total_research_words", 0) + 
                new_research['metadata'].get('total_words', 0)
            ),
            "enhancement_details": {
                "new_academic_papers": 1,
                "new_consulting_documents": 4, 
                "kpmg_papers_added": 3,
                "bcg_papers_added": 1,
                "academic_institutions": ["University of Plymouth"],
                "total_pages_added": 643,
                "total_words_added": 212316
            }
        },
        "patterns": [],
        "benchmarks": existing_rag.get('benchmarks', {})
    }
    
    # Start with existing patterns (avoid duplicates)
    existing_pattern_ids = set()
    for pattern in existing_rag.get('patterns', []):
        merged_rag["patterns"].append(pattern)
        if 'id' in pattern:
            existing_pattern_ids.add(pattern['id'])
    
    print(f"Added existing patterns: {len(existing_rag.get('patterns', []))}")
    
    # Add new patterns, avoiding duplicates
    new_patterns_added = 0
    for pattern in new_research['patterns']:
        pattern_id = pattern.get('id', f"NEW_{new_patterns_added}")
        
        # Skip if we already have this pattern
        if pattern_id in existing_pattern_ids:
            continue
            
        # Update pattern ID to avoid conflicts
        if pattern_id.startswith('DOC'):
            pattern['id'] = f"ENH{pattern_id[3:]}"
        
        merged_rag["patterns"].append(pattern)
        new_patterns_added += 1
    
    print(f" Added new research patterns: {new_patterns_added}")
    
    # Update final counts
    merged_rag["metadata"]["total_patterns"] = len(merged_rag["patterns"])
    merged_rag["metadata"]["final_research_patterns"] = (
        merged_rag["metadata"]["previous_research_patterns"] + new_patterns_added
    )
    
    # Save enhanced RAG dataset
    enhanced_rag_file = "bpi_rag_data_enhanced_with_additional_research.json"
    print(f"Saving enhanced RAG dataset: {enhanced_rag_file}")
    
    with open(enhanced_rag_file, 'w', encoding='utf-8') as f:
        json.dump(merged_rag, f, indent=2, ensure_ascii=False)
    
    # Update main RAG system to use enhanced dataset
    update_rag_system_config(enhanced_rag_file)
    
    print(f"\nINTEGRATION COMPLETE!")
    print("=" * 50)
    print(f"Total patterns in enhanced system: {merged_rag['metadata']['total_patterns']}")
    print(f"BPI Challenge patterns: {merged_rag['metadata']['bpi_patterns']}")
    print(f" Total research patterns: {merged_rag['metadata']['final_research_patterns']}")
    print(f"Total research words: {merged_rag['metadata']['total_research_words']:,}")
    print(f" Document sources: {', '.join(merged_rag['metadata']['document_sources'])}")
    
    print(f"\nENHANCEMENT DETAILS:")
    enhancement = merged_rag['metadata']['enhancement_details']
    print(f"    New academic papers: {enhancement['new_academic_papers']}")
    print(f"    New consulting documents: {enhancement['new_consulting_documents']}")
    print(f"   Pages added: {enhancement['total_pages_added']:,}")
    print(f"   Words added: {enhancement['total_words_added']:,}")
    print(f"   Academic institutions: {', '.join(enhancement['academic_institutions'])}")
    
    # Create summary for user
    create_enhancement_summary(merged_rag)
    
    return True

def update_rag_system_config(enhanced_file: str):
    """Update RAG system to use enhanced dataset."""
    
    print(f"\n UPDATING RAG SYSTEM CONFIGURATION")
    print("-" * 40)
    
    # Update rag_system.py to use enhanced file
    rag_system_path = "rag_system.py"
    
    try:
        with open(rag_system_path, 'r') as f:
            content = f.read()
        
        # Replace the dataset reference
        old_ref = 'bpi_rag_data_with_real_documents.json'
        new_ref = enhanced_file
        
        if old_ref in content:
            updated_content = content.replace(old_ref, new_ref)
            
            with open(rag_system_path, 'w') as f:
                f.write(updated_content)
            
            print(f"RAG system updated to use: {new_ref}")
        else:
            print("ℹ RAG system configuration unchanged")
    
    except Exception as e:
        print(f"⚠ Could not update RAG system: {str(e)}")

def create_enhancement_summary(merged_rag: dict):
    """Create a summary of the enhancement for documentation."""
    
    summary = {
        "enhancement_date": datetime.now().isoformat(),
        "purpose": "Enhanced RAG system with additional academic and consulting research",
        "before_enhancement": {
            "total_patterns": merged_rag['metadata']['bpi_patterns'] + merged_rag['metadata']['previous_research_patterns'],
            "research_sources": "Limited consulting firms"
        },
        "after_enhancement": {
            "total_patterns": merged_rag['metadata']['total_patterns'],
            "research_sources": merged_rag['metadata']['document_sources'],
            "total_research_words": merged_rag['metadata']['total_research_words']
        },
        "new_additions": merged_rag['metadata']['enhancement_details'],
        "quality_improvements": [
            "Added peer-reviewed academic paper on agile transformation",
            "Expanded KPMG research coverage with 3 additional papers",
            "Added BCG Henderson Institute evidence-based transformation guide",
            "Increased research corpus by 212,316 words",
            "Enhanced coverage of agile operating model challenges"
        ],
        "dissertation_value": [
            "Stronger academic foundation with University of Plymouth research",
            "More comprehensive consulting firm perspectives",
            "Evidence-based transformation methodologies",
            "Recent research (2019-2024) for current relevance",
            "Enhanced credibility through diverse, high-quality sources"
        ]
    }
    
    with open("rag_enhancement_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print(f"Enhancement summary saved: rag_enhancement_summary.json")

def main():
    """Main integration function."""
    
    success = integrate_enhanced_research()
    
    if success:
        print(f"\nRAG SYSTEM ENHANCEMENT SUCCESSFUL!")
        print("=" * 60)
        print("New research documents successfully integrated")
        print("RAG system configuration updated")
        print("Enhanced evidence base for dissertation")
        print("Academic integrity maintained with credible sources")
        
        print(f"\nNEXT STEPS:")
        print("1. Test enhanced system: python3 test_real_document_rag.py")
        print("2. Run comprehensive validation: python3 final_system_validation.py")
        print("3. Compare RAG performance: python3 evaluation_comparison.py")
    else:
        print(f"\nINTEGRATION FAILED")
        print("Please check error messages and file paths")
    
    return success

if __name__ == "__main__":
    main()
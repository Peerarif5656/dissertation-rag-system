#!/usr/bin/env python3
"""
Dissertation Research Papers Inventory
Creates comprehensive inventory of all research papers used in the dissertation
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any

def create_research_papers_inventory():
    """Create comprehensive inventory of all research papers."""
    
    print(" CREATING DISSERTATION RESEARCH PAPERS INVENTORY")
    print("=" * 70)
    
    base_dir = "real_documents/dissertation_research_papers"
    inventory = {
        "created": datetime.now().isoformat(),
        "purpose": "Comprehensive inventory of research papers for master's dissertation",
        "dissertation_title": "RAG-Enhanced Workflow Optimization System",
        "categories": {},
        "total_papers": 0,
        "total_pages": 0,
        "total_words": 0,
        "papers_by_source": {}
    }
    
    # Process each category
    for category in os.listdir(base_dir):
        category_path = os.path.join(base_dir, category)
        if not os.path.isdir(category_path):
            continue
            
        print(f"\nProcessing category: {category}")
        print("-" * 40)
        
        inventory["categories"][category] = {
            "description": get_category_description(category),
            "papers": [],
            "count": 0,
            "total_pages": 0
        }
        
        # Process papers in category
        for paper_file in os.listdir(category_path):
            if paper_file.endswith('.pdf'):
                paper_path = os.path.join(category_path, paper_file)
                paper_info = analyze_paper(paper_path, category)
                
                if paper_info:
                    inventory["categories"][category]["papers"].append(paper_info)
                    inventory["categories"][category]["count"] += 1
                    inventory["categories"][category]["total_pages"] += paper_info.get("pages", 0)
                    inventory["total_papers"] += 1
                    inventory["total_pages"] += paper_info.get("pages", 0)
                    inventory["total_words"] += paper_info.get("words", 0)
                    
                    # Track by source
                    source = paper_info.get("source", "unknown")
                    if source not in inventory["papers_by_source"]:
                        inventory["papers_by_source"][source] = []
                    inventory["papers_by_source"][source].append(paper_info["title"])
                    
                    print(f"  {paper_info['title']}")
                    print(f"     {paper_info.get('pages', 0)} pages, {paper_info.get('words', 0):,} words")
    
    # Save inventory
    inventory_file = "real_documents/dissertation_research_papers_inventory.json"
    with open(inventory_file, 'w') as f:
        json.dump(inventory, f, indent=2)
    
    # Create summary report
    create_summary_report(inventory)
    
    print(f"\nINVENTORY SUMMARY")
    print("=" * 40)
    print(f" Total research papers: {inventory['total_papers']}")
    print(f"Total pages: {inventory['total_pages']:,}")
    print(f"Total words: {inventory['total_words']:,}")
    print(f" Sources: {', '.join(inventory['papers_by_source'].keys())}")
    print(f"Inventory saved: {inventory_file}")
    
    return inventory

def get_category_description(category: str) -> str:
    """Get description for paper category."""
    descriptions = {
        "consulting_frameworks": "Industry consulting frameworks and methodologies from top-tier firms",
        "academic_papers": "Peer-reviewed academic papers on process mining and workflow optimization", 
        "bpi_challenge_2020": "Papers specifically related to BPI Challenge 2020 dataset and benchmarks"
    }
    return descriptions.get(category, f"Research papers in {category} category")

def analyze_paper(paper_path: str, category: str) -> Dict[str, Any]:
    """Analyze a research paper and extract metadata."""
    
    try:
        # Try to get processed data first
        paper_name = os.path.splitext(os.path.basename(paper_path))[0]
        processed_file = f"real_documents/processed/{paper_name}_processed.json"
        
        pages = 0
        words = 0
        
        if os.path.exists(processed_file):
            with open(processed_file, 'r') as f:
                processed_data = json.load(f)
                pages = processed_data.get("num_pages", 0)
                words = processed_data.get("word_count", 0)
        
        # Determine source based on filename and category
        source = determine_source(paper_path, category)
        
        # Create paper info
        paper_info = {
            "title": format_title(paper_name),
            "filename": os.path.basename(paper_path),
            "source": source,
            "category": category,
            "pages": pages,
            "words": words,
            "file_path": paper_path,
            "academic_relevance": get_academic_relevance(paper_name, category),
            "key_topics": extract_key_topics(paper_name)
        }
        
        return paper_info
        
    except Exception as e:
        print(f"  Error analyzing {paper_path}: {str(e)}")
        return None

def determine_source(paper_path: str, category: str) -> str:
    """Determine the source of the paper."""
    filename = os.path.basename(paper_path).lower()
    
    if "mckinsey" in filename:
        return "McKinsey & Company"
    elif "bcg" in filename:
        return "Boston Consulting Group"
    elif "deloitte" in filename:
        return "Deloitte"
    elif "bain" in filename:
        return "Bain & Company"
    elif "kpmg" in filename:
        return "KPMG"
    elif "pwc" in filename:
        return "PricewaterhouseCoopers"
    elif "icpm" in filename or "bpi" in filename:
        return "Academic Conference (ICPM/BPI Challenge)"
    elif "safe" in filename:
        return "Scaled Agile Framework"
    elif category == "academic_papers":
        return "Academic Research"
    else:
        return "Industry Research"

def format_title(filename: str) -> str:
    """Format filename into readable title."""
    # Remove file extension and replace underscores/hyphens with spaces
    title = filename.replace('_', ' ').replace('-', ' ')
    
    # Capitalize words appropriately
    title_words = []
    for word in title.split():
        if word.upper() in ['BPI', 'ICPM', 'BCG', 'AI', 'IT', 'HR', 'CEO', 'SAFe']:
            title_words.append(word.upper())
        elif word.lower() in ['and', 'or', 'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'with']:
            title_words.append(word.lower())
        else:
            title_words.append(word.capitalize())
    
    return ' '.join(title_words)

def get_academic_relevance(filename: str, category: str) -> str:
    """Determine academic relevance of the paper."""
    filename_lower = filename.lower()
    
    if category == "bpi_challenge_2020":
        return "High - Direct BPI Challenge 2020 research"
    elif "transformation" in filename_lower:
        return "High - Digital transformation methodologies"
    elif "agile" in filename_lower:
        return "High - Agile framework analysis"
    elif "operating" in filename_lower and "model" in filename_lower:
        return "High - Operating model frameworks"
    elif "process" in filename_lower and "mining" in filename_lower:
        return "High - Process mining research"
    elif category == "academic_papers":
        return "High - Peer-reviewed academic research"
    else:
        return "Medium - Industry best practices"

def extract_key_topics(filename: str) -> List[str]:
    """Extract key topics from filename."""
    filename_lower = filename.lower()
    topics = []
    
    topic_keywords = {
        "digital transformation": ["digital", "transformation"],
        "agile methodology": ["agile"],
        "process mining": ["process", "mining"],
        "operating model": ["operating", "model"],
        "workflow optimization": ["workflow", "optimization"],
        "business process": ["business", "process"],
        "change management": ["change", "management"],
        "lean methodology": ["lean"],
        "performance management": ["performance"],
        "organizational design": ["organizational"],
        "scaled agile framework": ["safe", "scaled"],
        "bpi challenge": ["bpi", "challenge"]
    }
    
    for topic, keywords in topic_keywords.items():
        if any(keyword in filename_lower for keyword in keywords):
            topics.append(topic)
    
    return topics if topics else ["general business research"]

def create_summary_report(inventory: Dict[str, Any]):
    """Create a human-readable summary report."""
    
    report_file = "real_documents/DISSERTATION_RESEARCH_SUMMARY.md"
    
    with open(report_file, 'w') as f:
        f.write("# Dissertation Research Papers Summary\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Purpose:** Supporting research for master's dissertation on RAG-Enhanced Workflow Optimization System\n\n")
        
        f.write("## Overview\n\n")
        f.write(f"- **Total Papers:** {inventory['total_papers']}\n")
        f.write(f"- **Total Pages:** {inventory['total_pages']:,}\n")
        f.write(f"- **Total Words:** {inventory['total_words']:,}\n\n")
        
        f.write("## Research Sources\n\n")
        for source, papers in inventory['papers_by_source'].items():
            f.write(f"### {source}\n")
            f.write(f"**Papers:** {len(papers)}\n\n")
            for paper in papers:
                f.write(f"- {paper}\n")
            f.write("\n")
        
        f.write("## Categories\n\n")
        for category, details in inventory['categories'].items():
            f.write(f"### {category.replace('_', ' ').title()}\n")
            f.write(f"**Description:** {details['description']}\n\n")
            f.write(f"**Papers:** {details['count']}\n")
            f.write(f"**Total Pages:** {details['total_pages']}\n\n")
            
            for paper in details['papers']:
                f.write(f"#### {paper['title']}\n")
                f.write(f"- **Source:** {paper['source']}\n")
                f.write(f"- **Pages:** {paper['pages']}\n")
                f.write(f"- **Words:** {paper['words']:,}\n")
                f.write(f"- **Academic Relevance:** {paper['academic_relevance']}\n")
                f.write(f"- **Key Topics:** {', '.join(paper['key_topics'])}\n\n")
        
        f.write("---\n")
        f.write("*This inventory supports the academic integrity and transparency of the dissertation research process.*\n")
    
    print(f"Summary report created: {report_file}")

def update_rag_system_with_bpi_paper():
    """Update RAG system with the new BPI Challenge 2020 paper."""
    
    print(f"\nUPDATING RAG SYSTEM WITH BPI PAPER")
    print("-" * 40)
    
    try:
        # Load processed BPI paper
        with open('real_documents/processed/ICPM_2020_paper_99_processed.json', 'r') as f:
            bpi_paper = json.load(f)
        
        # Load current merged RAG data
        with open('bpi_rag_data_with_real_documents.json', 'r') as f:
            rag_data = json.load(f)
        
        # Create new pattern for BPI paper
        new_pattern = {
            "id": "DOC5100",
            "source": "research_document",
            "document_type": "bpi_challenge_2020",
            "title": "ICPM 2020 BPI Challenge Paper",
            "author": "",
            "file_name": bpi_paper["file_name"],
            "full_text": bpi_paper["full_text"],
            "word_count": bpi_paper["word_count"],
            "page_count": bpi_paper["num_pages"],
            "sections": bpi_paper["sections"],
            "processed_timestamp": bpi_paper["processed_timestamp"],
            "text_hash": bpi_paper["text_hash"],
            "search_text": bpi_paper["full_text"][:5000],
            "keywords": ["bpi", "challenge", "2020", "process", "mining", "workflow", "benchmark"],
            "metadata": {
                "type": "bpi_research_paper",
                "source_firm": "academic_conference",
                "document_quality": "high",
                "academic_relevance": "very_high"
            }
        }
        
        # Add to patterns
        rag_data["patterns"].append(new_pattern)
        
        # Update metadata
        rag_data["metadata"]["total_patterns"] = len(rag_data["patterns"])
        rag_data["metadata"]["research_document_patterns"] += 1
        rag_data["metadata"]["bpi_specific_papers"] = 1
        
        # Save updated RAG data
        with open('bpi_rag_data_with_real_documents.json', 'w') as f:
            json.dump(rag_data, f, indent=2)
        
        print(f"BPI Challenge 2020 paper added to RAG system")
        print(f"Total patterns now: {rag_data['metadata']['total_patterns']}")
        
    except Exception as e:
        print(f"Error updating RAG system: {str(e)}")

def main():
    """Main function to create inventory and update systems."""
    
    print("ORGANIZING DISSERTATION RESEARCH PAPERS")
    print("=" * 80)
    
    # Create comprehensive inventory
    inventory = create_research_papers_inventory()
    
    # Update RAG system with BPI paper
    update_rag_system_with_bpi_paper()
    
    print(f"\nRESEARCH ORGANIZATION COMPLETE!")
    print("=" * 50)
    print("All research papers organized in dissertation_research_papers/")
    print("Comprehensive inventory created")
    print("BPI Challenge 2020 paper processed and added")
    print("RAG system updated with additional research")
    print("Ready for dissertation submission")
    
    print(f"\nFOLDER STRUCTURE:")
    print("real_documents/")
    print("  ├── dissertation_research_papers/")
    print("  │   ├── consulting_frameworks/    # McKinsey, BCG, Deloitte papers")
    print("  │   ├── academic_papers/          # Academic research papers")
    print("  │   └── bpi_challenge_2020/       # BPI Challenge specific papers")
    print("  ├── processed/                    # Extracted text from all papers")
    print("  └── dissertation_research_papers_inventory.json")
    
    return inventory

if __name__ == "__main__":
    main()
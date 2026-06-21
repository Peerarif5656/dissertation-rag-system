#!/usr/bin/env python3
"""
Assess and Collect Additional Research Sources
Evaluate and download high-quality sources for RAG enhancement
"""

import requests
import os
from datetime import datetime
from typing import Dict, List, Any
import time

def assess_research_sources():
    """Assess quality and relevance of potential research sources."""
    
    print("ASSESSING POTENTIAL RESEARCH SOURCES")
    print("=" * 70)
    
    sources = {
        "high_priority": [],
        "medium_priority": [],
        "academic_papers": [],
        "skip_reasons": {}
    }
    
    # Academic papers - highest priority for dissertation
    academic_sources = [
        {
            "title": "An exploratory study of a large-scale agile transformation",
            "url": "https://journals.sagepub.com/doi/full/10.1177/02683962231164428",
            "institution": "University of Galway, Lero Irish Software Research Centre",
            "year": 2023,
            "journal": "Journal of Information Technology",
            "assessment": "Very high - peer-reviewed, recent, directly relevant to agile transformation"
        },
        {
            "title": "Agile Transformation: How Employees Experience and Cope with Transformative Change",
            "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC7510805/",
            "institution": "University of Gothenburg, Aalborg University", 
            "year": 2020,
            "journal": "PMC",
            "assessment": "High - academic research on agile transformation experience"
        },
        {
            "title": "Large-Scale Agile Transformation: A Case Study",
            "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC7251607/",
            "institution": "Various Nordic universities",
            "year": 2020,
            "journal": "PMC",
            "assessment": "High - large-scale transformation case study"
        },
        {
            "title": "Agile transformation in large organisations - framework for project management",
            "url": "https://pure.southwales.ac.uk/files/10622375/CS_DBA_Final_thesis.pdf",
            "institution": "University of South Wales",
            "year": 2023,
            "type": "Doctoral thesis",
            "assessment": "High - recent doctoral research, comprehensive framework"
        },
        {
            "title": "Changes to team autonomy in large-scale software development (SAFe)",
            "url": "https://www.sciencesphere.org/ijispm/archive/ijispm-100102.pdf",
            "institution": "Scandinavian universities",
            "year": 2022,
            "journal": "International Journal of Information Systems and Project Management",
            "assessment": "Medium-High - SAFe specific research"
        },
        {
            "title": "Critical Success Factors in Large-Scale Agile Software Development",
            "url": "https://pearl.plymouth.ac.uk/context/ada-research/article/1368/viewcontent/Critical_Success_Factors_in_Large_Scale_Agile_Software_Development___JAET.pdf",
            "institution": "University of Plymouth",
            "year": 2023,
            "assessment": "Medium-High - success factors analysis"
        }
    ]
    
    # High-quality consulting firm papers
    consulting_sources = [
        {
            "title": "Overcoming the agile operating model challenges",
            "url": "https://assets.kpmg.com/content/dam/kpmg/be/pdf/TA-AgileTransformation-2024-Brochure-A4.pdf",
            "firm": "KPMG",
            "year": 2024,
            "assessment": "High - structured agile transformation framework, recent"
        },
        {
            "title": "From Agile experiments to operating model transformation",
            "url": "https://assets.kpmg.com/content/dam/kpmg/pe/pdf/Publicaciones/TL/agile-transformation.pdf",
            "firm": "KPMG",
            "year": 2024,
            "assessment": "High - operating model transformation focus"
        },
        {
            "title": "Agile Transformation Survey",
            "url": "https://assets.kpmg.com/content/dam/kpmg/nl/pdf/2019/advisory/2019-kpmg-agile-survey.pdf",
            "firm": "KPMG",
            "year": 2019,
            "assessment": "Medium-High - survey data on agile transformation"
        },
        {
            "title": "Transforming for Growth: An Evidence-Based Guide",
            "url": "https://bcghendersoninstitute.com/wp-content/uploads/2020/05/BCG-Transforming-for-Growth-An-Evidence-Based-Guide-Jun-2020_tcm9-251757.pdf",
            "firm": "BCG Henderson Institute",
            "year": 2020,
            "assessment": "Very high - evidence-based, comprehensive guide"
        }
    ]
    
    # Assess and categorize sources
    for source in academic_sources:
        if source.get("year", 0) >= 2020 and "agile" in source["title"].lower():
            sources["academic_papers"].append(source)
            print(f" ACADEMIC: {source['title']} - {source['assessment']}")
        elif source.get("year", 0) < 2020:
            sources["skip_reasons"][source["title"]] = "Too old (pre-2020)"
    
    for source in consulting_sources:
        if source.get("year", 0) >= 2019:
            sources["high_priority"].append(source)
            print(f" CONSULTING: {source['title']} - {source['assessment']}")
        else:
            sources["skip_reasons"][source["title"]] = "Too old or low relevance"
    
    # Web-based sources (need assessment for PDF availability)
    web_sources = [
        {
            "title": "Enterprise agility: Buzz or business impact?",
            "url": "https://www.mckinsey.com/capabilities/people-and-organizational-performance/our-insights/enterprise-agility-buzz-or-business-impact",
            "firm": "McKinsey",
            "year": 2020,
            "assessment": "Medium - web content, may not have PDF"
        },
        {
            "title": "The impact of agility: How to shape your organization to compete",
            "url": "https://www.mckinsey.com/capabilities/people-and-organizational-performance/our-insights/the-impact-of-agility-how-to-shape-your-organization-to-compete",
            "firm": "McKinsey", 
            "year": 2021,
            "assessment": "Medium - web content, need to check PDF availability"
        }
    ]
    
    for source in web_sources:
        sources["medium_priority"].append(source)
        print(f" WEB: {source['title']} - {source['assessment']}")
    
    print(f"\nASSESSMENT SUMMARY:")
    print(f"    Academic papers (highest priority): {len(sources['academic_papers'])}")
    print(f"    Consulting documents: {len(sources['high_priority'])}")
    print(f"    Web sources: {len(sources['medium_priority'])}")
    print(f"   ⏭ Skipped sources: {len(sources['skip_reasons'])}")
    
    return sources

def download_research_documents(sources: Dict[str, List[Any]]):
    """Download high-quality research documents."""
    
    print(f"\n DOWNLOADING RESEARCH DOCUMENTS")
    print("-" * 50)
    
    # Create directories
    os.makedirs("real_documents/dissertation_research_papers/academic_papers_2024", exist_ok=True)
    os.makedirs("real_documents/dissertation_research_papers/consulting_frameworks_2024", exist_ok=True)
    
    downloaded = {"academic": 0, "consulting": 0, "failed": []}
    
    # Download academic papers
    print(" Downloading academic papers...")
    for source in sources["academic_papers"]:
        success = download_document(
            source["url"], 
            source["title"], 
            "real_documents/dissertation_research_papers/academic_papers_2024",
            source.get("institution", "Unknown")
        )
        if success:
            downloaded["academic"] += 1
        else:
            downloaded["failed"].append(f"Academic: {source['title']}")
    
    # Download consulting documents
    print("\n Downloading consulting documents...")
    for source in sources["high_priority"]:
        success = download_document(
            source["url"],
            source["title"],
            "real_documents/dissertation_research_papers/consulting_frameworks_2024", 
            source.get("firm", "Unknown")
        )
        if success:
            downloaded["consulting"] += 1
        else:
            downloaded["failed"].append(f"Consulting: {source['title']}")
    
    print(f"\nDOWNLOAD SUMMARY:")
    print(f"   Academic papers downloaded: {downloaded['academic']}")
    print(f"   Consulting documents downloaded: {downloaded['consulting']}")
    print(f"   Failed downloads: {len(downloaded['failed'])}")
    
    if downloaded["failed"]:
        print(f"   Failed sources:")
        for failed in downloaded["failed"]:
            print(f"     • {failed}")
    
    return downloaded

def download_document(url: str, title: str, directory: str, source: str) -> bool:
    """Download a single document with retry logic."""
    
    try:
        # Clean filename
        filename = title.lower().replace(" ", "_").replace("-", "_")
        filename = "".join(c for c in filename if c.isalnum() or c in ["_", "."])
        filename = f"{filename}.pdf"
        filepath = os.path.join(directory, filename)
        
        print(f"   Downloading: {title}")
        print(f"       Source: {source}")
        print(f"      URL: {url[:50]}...")
        
        # Set headers to mimic browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/pdf,application/octet-stream,*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # Download with timeout
        response = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
        response.raise_for_status()
        
        # Check if response is actually a PDF
        content_type = response.headers.get('content-type', '').lower()
        if 'pdf' not in content_type and not url.endswith('.pdf'):
            print(f"      ⚠ Not a PDF: {content_type}")
            return False
        
        # Save file
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        file_size = len(response.content)
        print(f"      Downloaded: {file_size:,} bytes")
        
        # Verify it's a valid PDF
        with open(filepath, 'rb') as f:
            header = f.read(4)
            if header != b'%PDF':
                print(f"      Invalid PDF format")
                os.remove(filepath)
                return False
        
        print(f"      Saved: {filepath}")
        time.sleep(1)  # Be respectful to servers
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"      Download failed: {str(e)}")
        return False
    except Exception as e:
        print(f"      Error: {str(e)}")
        return False

def create_download_report(sources: Dict[str, List[Any]], downloaded: Dict[str, Any]):
    """Create report of download activities."""
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "purpose": "Enhanced RAG system with additional research sources",
        "assessment_summary": {
            "academic_papers_identified": len(sources["academic_papers"]),
            "consulting_documents_identified": len(sources["high_priority"]),
            "web_sources_identified": len(sources["medium_priority"]),
            "sources_skipped": len(sources["skip_reasons"])
        },
        "download_results": {
            "academic_papers_downloaded": downloaded["academic"],
            "consulting_documents_downloaded": downloaded["consulting"],
            "total_successful_downloads": downloaded["academic"] + downloaded["consulting"],
            "failed_downloads": len(downloaded["failed"]),
            "failed_sources": downloaded["failed"]
        },
        "quality_criteria": {
            "minimum_year": 2019,
            "preferred_year": 2020,
            "required_topics": ["agile", "transformation", "operating model", "lean"],
            "source_preferences": ["academic journals", "top-tier consulting firms", "peer-reviewed papers"]
        },
        "next_steps": [
            "Process downloaded PDFs with pdf_processor.py",
            "Update RAG system with new patterns",
            "Validate integration with test_real_document_rag.py"
        ]
    }
    
    with open("research_enhancement_report.json", "w") as f:
        import json
        json.dump(report, f, indent=2)
    
    print(f"Download report saved: research_enhancement_report.json")
    return report

def main():
    """Main function to assess and collect research sources."""
    
    print("ENHANCING RAG SYSTEM WITH ADDITIONAL RESEARCH")
    print("=" * 80)
    print("Objective: Add high-quality academic and consulting research")
    print("Focus: Agile transformation, operating models, lean methodologies")
    print("Quality criteria: Recent (2019+), credible sources, relevant content")
    print()
    
    # Assess sources
    sources = assess_research_sources()
    
    # Download high-quality documents
    downloaded = download_research_documents(sources)
    
    # Create report
    report = create_download_report(sources, downloaded)
    
    print(f"\nRESEARCH ENHANCEMENT COMPLETE!")
    print("=" * 50)
    
    total_new = downloaded["academic"] + downloaded["consulting"]
    if total_new > 0:
        print(f"Successfully added {total_new} new research documents")
        print(f" Academic papers: {downloaded['academic']}")
        print(f" Consulting frameworks: {downloaded['consulting']}")
        print(f"Saved to: dissertation_research_papers/")
        
        print(f"\nNEXT STEPS:")
        print("1. Process new PDFs: python3 pdf_processor.py")
        print("2. Update RAG system: python3 integrate_real_rag_documents.py") 
        print("3. Test enhanced system: python3 test_real_document_rag.py")
    else:
        print(f"⚠ No new documents successfully downloaded")
        print(f"Check network connectivity and source availability")
    
    return report

if __name__ == "__main__":
    main()
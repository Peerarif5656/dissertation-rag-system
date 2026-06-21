#!/usr/bin/env python3
"""
Enhance RAG System with Additional Operating Model Frameworks
Add high-quality sources from the 33 provided while keeping existing sources
"""

import requests
import json
import os
from datetime import datetime
from typing import Dict, Any, List

def get_high_priority_sources():
    """Get high-priority sources from the 33 list for RAG enhancement."""
    
    high_priority_sources = [
        # McKinsey Operating Models
        {
            "title": "A new operating model for a new world",
            "url": "https://www.mckinsey.com/capabilities/people-and-organizational-performance/our-insights/a-new-operating-model-for-a-new-world", 
            "firm": "McKinsey",
            "year": 2025,
            "focus": "12-element Organize to Value framework",
            "priority": "very_high"
        },
        {
            "title": "How to get your operating model transformation back on track",
            "url": "https://www.mckinsey.com/capabilities/people-and-organizational-performance/our-insights/how-to-get-your-operating-model-transformation-back-on-track",
            "firm": "McKinsey", 
            "year": 2025,
            "focus": "Operating model transformation recovery",
            "priority": "high"
        },
        
        # Bain Operating Models
        {
            "title": "From Silos to Speed: How Product Operating Model Is Transforming Consumer Products Companies",
            "url": "https://www.bain.com/insights/from-silos-to-speed-how-product-operating-model-is-transforming-consumer-products-companies/",
            "firm": "Bain",
            "year": 2025, 
            "focus": "Product operating model transformation",
            "priority": "high"
        },
        {
            "title": "Design Principles for a Robust Operating Model",
            "url": "https://www.bain.com/insights/design-principles-for-a-robust-operating-model/",
            "firm": "Bain",
            "year": 2015,
            "focus": "Operating model design principles",
            "priority": "high"
        },
        
        # PwC Strategy& Operating Models
        {
            "title": "The strategic operating model",
            "url": "https://www.strategyand.pwc.com/uk/en/insights/strategic-operating-model.html",
            "firm": "PwC Strategy&",
            "year": 2023,
            "focus": "Strategic operating model framework",
            "priority": "high"
        },
        {
            "title": "Six dimensions of the agile enterprise", 
            "url": "https://www.strategyand.pwc.com/us/en/reports/2020/six-dimensions-of-the-agile-enterprise.html",
            "firm": "PwC Strategy&",
            "year": 2020,
            "focus": "Agile enterprise dimensions",
            "priority": "high"
        },
        
        # Additional BCG Sources
        {
            "title": "Why Companies Get Agile Right—and Wrong",
            "url": "https://www.bcg.com/publications/2024/why-companies-get-agile-right-wrong",
            "firm": "BCG",
            "year": 2024,
            "focus": "Agile transformation success factors",
            "priority": "high"
        },
        {
            "title": "How to Create a Transformation That Lasts",
            "url": "https://www.bcg.com/publications/2024/how-to-create-a-transformation-that-lasts",
            "firm": "BCG", 
            "year": 2025,
            "focus": "Sustainable transformation",
            "priority": "high"
        },
        
        # Deloitte Operating Models
        {
            "title": "Designing an Operating Model for Changing Market Needs",
            "url": "https://www.deloitte.com/us/en/services/consulting/articles/changing-operating-model.html",
            "firm": "Deloitte",
            "year": 2025,
            "focus": "Adaptive operating model design",
            "priority": "high"
        },
        
        # Academic Sources (highest priority)
        {
            "title": "An exploratory study of a large-scale agile transformation",
            "url": "https://journals.sagepub.com/doi/full/10.1177/02683962231164428",
            "firm": "Academic",
            "institution": "University of Galway",
            "year": 2023,
            "journal": "Journal of Information Technology", 
            "focus": "Large-scale agile transformation research",
            "priority": "very_high"
        }
    ]
    
    return high_priority_sources

def extract_content_from_web_source(url: str, title: str) -> Dict[str, Any]:
    """Extract content from web sources for RAG integration."""
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Extract text content (basic HTML parsing)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Get text content
        text_content = soup.get_text()
        
        # Clean up text
        lines = (line.strip() for line in text_content.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Limit content size
        if len(text) > 10000:
            text = text[:10000] + "..."
        
        return {
            "title": title,
            "url": url,
            "content": text,
            "word_count": len(text.split()),
            "extraction_success": True
        }
        
    except Exception as e:
        print(f"Failed to extract content from {url}: {str(e)}")
        return {
            "title": title,
            "url": url,
            "content": f"Content extraction failed. Source: {url}",
            "word_count": 0,
            "extraction_success": False,
            "error": str(e)
        }

def create_enhanced_rag_patterns():
    """Create enhanced RAG patterns with new sources."""
    
    print("Creating Enhanced RAG Patterns")
    print("=" * 50)
    
    # Load existing RAG data
    try:
        with open('bpi_rag_data_enhanced_with_additional_research.json', 'r') as f:
            existing_rag = json.load(f)
        print(f"Loaded existing RAG data: {len(existing_rag['patterns'])} patterns")
    except FileNotFoundError:
        print("No existing RAG data found, starting fresh")
        existing_rag = {"patterns": [], "metadata": {}}
    
    # Get new sources
    new_sources = get_high_priority_sources()
    print(f"Processing {len(new_sources)} new sources")
    
    # Extract content from web sources
    new_patterns = []
    pattern_id = 7000  # Start high to avoid conflicts
    
    for source in new_sources:
        print(f"Processing: {source['title']}")
        
        # Try to extract web content
        content_data = extract_content_from_web_source(source['url'], source['title'])
        
        if content_data['extraction_success'] and content_data['word_count'] > 100:
            # Create main document pattern
            pattern = {
                "id": f"OP{pattern_id:04d}",
                "source": "operating_model_framework",
                "document_type": source['firm'].lower().replace(' ', '_'),
                "title": source['title'],
                "url": source['url'],
                "firm": source['firm'],
                "year": source.get('year', 2024),
                "focus_area": source.get('focus', ''),
                "content": content_data['content'],
                "word_count": content_data['word_count'],
                "search_text": content_data['content'][:3000],  # First 3000 chars for search
                "keywords": extract_framework_keywords(content_data['content']),
                "metadata": {
                    "type": "operating_model_framework",
                    "priority": source.get('priority', 'medium'),
                    "extraction_method": "web_scraping",
                    "academic_source": source['firm'] == 'Academic'
                },
                "processed_timestamp": datetime.now().isoformat()
            }
            
            new_patterns.append(pattern)
            pattern_id += 1
            print(f"  Added pattern: {content_data['word_count']} words")
        else:
            print(f"  Skipped: {content_data.get('error', 'insufficient content')}")
    
    # Combine with existing patterns
    all_patterns = existing_rag.get('patterns', []) + new_patterns
    
    # Create enhanced RAG dataset
    enhanced_rag = {
        "metadata": {
            "created": datetime.now().isoformat(),
            "source": "enhanced_with_operating_model_frameworks",
            "total_patterns": len(all_patterns),
            "existing_patterns": len(existing_rag.get('patterns', [])),
            "new_operating_model_patterns": len(new_patterns),
            "framework_sources": list(set([p.get('firm', 'Unknown') for p in new_patterns])),
            "enhancement_focus": "Operating model frameworks and transformation methodologies"
        },
        "patterns": all_patterns,
        "benchmarks": existing_rag.get('benchmarks', {})
    }
    
    # Save enhanced dataset
    output_file = "bpi_rag_data_with_operating_models.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(enhanced_rag, f, indent=2, ensure_ascii=False)
    
    print(f"\nEnhancement Complete:")
    print(f"Total patterns: {enhanced_rag['metadata']['total_patterns']}")
    print(f"New patterns added: {len(new_patterns)}")
    print(f"Framework sources: {', '.join(enhanced_rag['metadata']['framework_sources'])}")
    print(f"Enhanced dataset saved: {output_file}")
    
    return enhanced_rag

def extract_framework_keywords(content: str) -> List[str]:
    """Extract relevant keywords for operating model frameworks."""
    
    framework_terms = [
        "operating model", "transformation", "agile", "lean", "process optimization",
        "organizational design", "capability building", "digital transformation",
        "performance improvement", "change management", "governance", "accountability",
        "value creation", "efficiency", "effectiveness", "innovation", "collaboration",
        "automation", "digitization", "customer experience", "employee experience"
    ]
    
    content_lower = content.lower()
    found_keywords = []
    
    for term in framework_terms:
        if term in content_lower:
            found_keywords.append(term)
    
    # Add specific business terms that appear frequently
    words = content_lower.split()
    business_words = ["strategy", "execution", "governance", "capabilities", "processes", 
                     "performance", "technology", "people", "culture", "leadership"]
    
    for word in business_words:
        if words.count(word) >= 3 and word not in found_keywords:
            found_keywords.append(word)
    
    return found_keywords[:15]  # Limit to top 15 keywords

def update_rag_system_config():
    """Update RAG system to use enhanced dataset."""
    
    print("\nUpdating RAG system configuration...")
    
    # Update rag_system.py
    try:
        with open('rag_system.py', 'r') as f:
            content = f.read()
        
        # Update the dataset path
        old_path = 'bpi_rag_data_enhanced_with_additional_research.json'
        new_path = 'bpi_rag_data_with_operating_models.json'
        
        updated_content = content.replace(old_path, new_path)
        
        with open('rag_system.py', 'w') as f:
            f.write(updated_content)
        
        print("RAG system updated to use enhanced dataset")
        
    except Exception as e:
        print(f"Warning: Could not update RAG system config: {e}")

def main():
    """Main enhancement function."""
    
    print("RAG System Enhancement with Operating Model Frameworks")
    print("=" * 70)
    
    # Install required dependency
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print("Installing required dependency...")
        os.system("pip3 install beautifulsoup4")
    
    # Create enhanced patterns
    enhanced_rag = create_enhanced_rag_patterns()
    
    # Update system configuration
    update_rag_system_config()
    
    print("\nRAG Enhancement Summary:")
    print(f"- Total patterns: {enhanced_rag['metadata']['total_patterns']}")
    print(f"- Operating model sources: {', '.join(enhanced_rag['metadata']['framework_sources'])}")
    print(f"- Focus: {enhanced_rag['metadata']['enhancement_focus']}")
    print("- RAG system updated to use enhanced dataset")
    print("\nReady for comprehensive workflow analysis with expanded knowledge base!")
    
    return enhanced_rag

if __name__ == "__main__":
    main()
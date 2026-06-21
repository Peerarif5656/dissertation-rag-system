#!/usr/bin/env python3
"""
PDF Processor for RAG System
Extracts text and structure from collected research documents
"""

import os
import json
import pdfplumber
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib

class PDFProcessor:
    """Process PDF documents into structured text for RAG system."""
    
    def __init__(self, documents_dir: str = "real_documents"):
        self.documents_dir = documents_dir
        self.processed_dir = os.path.join(documents_dir, "processed")
        os.makedirs(self.processed_dir, exist_ok=True)
        
        self.processing_log = {
            "started": datetime.now().isoformat(),
            "documents_processed": [],
            "processing_errors": [],
            "extraction_stats": {
                "total_documents": 0,
                "successful_extractions": 0,
                "total_pages_processed": 0,
                "total_words_extracted": 0
            }
        }
    
    def extract_text_from_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Extract text and metadata from a PDF file."""
        
        try:
            print(f"Processing: {os.path.basename(pdf_path)}")
            
            with pdfplumber.open(pdf_path) as pdf:
                # Extract metadata
                metadata = {}
                if hasattr(pdf, 'metadata') and pdf.metadata:
                    metadata = {
                        "title": pdf.metadata.get('Title', ''),
                        "author": pdf.metadata.get('Author', ''),
                        "subject": pdf.metadata.get('Subject', ''),
                        "creator": pdf.metadata.get('Creator', ''),
                        "producer": pdf.metadata.get('Producer', ''),
                        "creation_date": str(pdf.metadata.get('CreationDate', '')),
                        "modification_date": str(pdf.metadata.get('ModDate', ''))
                    }
                
                # Extract text from all pages
                full_text = ""
                page_texts = []
                
                for page_num, page in enumerate(pdf.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            page_texts.append({
                                "page_number": page_num + 1,
                                "text": page_text,
                                "word_count": len(page_text.split())
                            })
                            full_text += page_text + "\n\n"
                    except Exception as e:
                        print(f"   ⚠ Error extracting page {page_num + 1}: {str(e)}")
                
                # Clean and structure the text
                cleaned_text = self.clean_extracted_text(full_text)
                
                # Extract key sections
                sections = self.extract_document_sections(cleaned_text)
                
                # Generate text hash for deduplication
                text_hash = hashlib.md5(cleaned_text.encode()).hexdigest()
                
                extraction_result = {
                    "file_path": pdf_path,
                    "file_name": os.path.basename(pdf_path),
                    "num_pages": len(pdf.pages),
                    "metadata": metadata,
                    "full_text": cleaned_text,
                    "page_texts": page_texts,
                    "sections": sections,
                    "word_count": len(cleaned_text.split()),
                    "text_hash": text_hash,
                    "processed_timestamp": datetime.now().isoformat()
                }
                
                print(f"   Extracted {len(cleaned_text.split())} words from {len(pdf.pages)} pages")
                return extraction_result
                
        except Exception as e:
            error_msg = f"Failed to process {pdf_path}: {str(e)}"
            print(f"   {error_msg}")
            self.processing_log["processing_errors"].append({
                "file_path": pdf_path,
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            })
            return None
    
    def clean_extracted_text(self, text: str) -> str:
        """Clean and normalize extracted PDF text."""
        
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        
        # Remove page headers/footers (common patterns)
        text = re.sub(r'Page \d+.*?\n', '', text)
        text = re.sub(r'\n\d+\n', '\n', text)
        
        # Remove URLs and email addresses for cleaner text
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        text = re.sub(r'\S+@\S+\.\S+', '', text)
        
        # Normalize line breaks
        text = text.strip()
        
        return text
    
    def extract_document_sections(self, text: str) -> Dict[str, str]:
        """Extract common document sections (abstract, introduction, etc.)."""
        
        sections = {}
        text_lower = text.lower()
        
        # Common section patterns
        section_patterns = {
            "abstract": r"(?:abstract|summary)[\s\n]+(.*?)(?=\n\s*(?:introduction|keywords|1\.|contents)|$)",
            "introduction": r"(?:introduction|1\.?\s*introduction)[\s\n]+(.*?)(?=\n\s*(?:2\.|background|methodology|literature)|$)",
            "methodology": r"(?:methodology|methods|approach)[\s\n]+(.*?)(?=\n\s*(?:3\.|results|findings|analysis)|$)",
            "conclusions": r"(?:conclusion|conclusions|summary)[\s\n]+(.*?)(?=\n\s*(?:references|bibliography|appendix)|$)",
            "key_findings": r"(?:key findings|findings|results)[\s\n]+(.*?)(?=\n\s*(?:discussion|conclusion|references)|$)"
        }
        
        for section_name, pattern in section_patterns.items():
            match = re.search(pattern, text_lower, re.DOTALL | re.IGNORECASE)
            if match:
                sections[section_name] = match.group(1).strip()[:2000]  # Limit length
        
        return sections
    
    def process_all_pdfs(self) -> List[Dict[str, Any]]:
        """Process all PDF files in the documents directory."""
        
        print("PDF PROCESSING STARTED")
        print("=" * 50)
        
        processed_documents = []
        
        # Find all PDF files in all subdirectories
        for root, dirs, files in os.walk(self.documents_dir):
            for file in files:
                if file.endswith('.pdf') and not file.startswith('.'):
                    pdf_path = os.path.join(root, file)
                    
                    # Skip if already in processed directory
                    if 'processed' in pdf_path:
                        continue
                    
                    extraction_result = self.extract_text_from_pdf(pdf_path)
                    
                    if extraction_result:
                        # Save processed document
                        processed_file = os.path.join(
                            self.processed_dir, 
                            f"{os.path.splitext(file)[0]}_processed.json"
                        )
                        
                        with open(processed_file, 'w', encoding='utf-8') as f:
                            json.dump(extraction_result, f, indent=2, ensure_ascii=False)
                        
                        # Update log
                        self.processing_log["documents_processed"].append({
                            "original_file": pdf_path,
                            "processed_file": processed_file,
                            "word_count": extraction_result["word_count"],
                            "pages": extraction_result["num_pages"]
                        })
                        
                        # Update stats
                        self.processing_log["extraction_stats"]["successful_extractions"] += 1
                        self.processing_log["extraction_stats"]["total_pages_processed"] += extraction_result["num_pages"]
                        self.processing_log["extraction_stats"]["total_words_extracted"] += extraction_result["word_count"]
                        
                        processed_documents.append(extraction_result)
                    
                    self.processing_log["extraction_stats"]["total_documents"] += 1
        
        # Save processing log
        log_file = os.path.join(self.processed_dir, "pdf_processing_log.json")
        self.processing_log["completed"] = datetime.now().isoformat()
        
        with open(log_file, 'w') as f:
            json.dump(self.processing_log, f, indent=2)
        
        print(f"\nPDF PROCESSING SUMMARY")
        print("=" * 40)
        print(f"Documents processed: {self.processing_log['extraction_stats']['successful_extractions']}")
        print(f"Total pages processed: {self.processing_log['extraction_stats']['total_pages_processed']}")
        print(f"Total words extracted: {self.processing_log['extraction_stats']['total_words_extracted']:,}")
        print(f"Processing errors: {len(self.processing_log['processing_errors'])}")
        print(f"Processed files saved to: {self.processed_dir}")
        print(f"Processing log: {log_file}")
        
        return processed_documents
    
    def create_rag_dataset(self, processed_documents: List[Dict[str, Any]]) -> str:
        """Convert processed documents into RAG-compatible dataset."""
        
        print("\nCREATING RAG DATASET FROM PROCESSED DOCUMENTS")
        print("-" * 50)
        
        rag_patterns = []
        pattern_id = 5000  # Start high to avoid conflicts with BPI data
        
        for doc in processed_documents:
            # Determine source type from file path
            source_type = "unknown"
            if "mckinsey" in doc["file_path"].lower():
                source_type = "mckinsey"
            elif "bcg" in doc["file_path"].lower():
                source_type = "bcg"
            elif "bain" in doc["file_path"].lower():
                source_type = "bain"
            elif "deloitte" in doc["file_path"].lower():
                source_type = "deloitte"
            elif "kpmg" in doc["file_path"].lower():
                source_type = "kpmg"
            elif "pwc" in doc["file_path"].lower():
                source_type = "pwc"
            elif "academic" in doc["file_path"].lower():
                source_type = "academic"
            
            # Create main document pattern
            main_pattern = {
                "id": f"DOC{pattern_id:04d}",
                "source": "research_document",
                "document_type": source_type,
                "title": doc.get("metadata", {}).get("title", doc["file_name"]),
                "author": doc.get("metadata", {}).get("author", ""),
                "file_name": doc["file_name"],
                "full_text": doc["full_text"],
                "word_count": doc["word_count"],
                "page_count": doc["num_pages"],
                "sections": doc["sections"],
                "processed_timestamp": doc["processed_timestamp"],
                "text_hash": doc["text_hash"],
                
                # RAG-compatible search fields
                "search_text": doc["full_text"][:5000],  # First 5000 chars for search
                "keywords": self.extract_keywords(doc["full_text"]),
                
                # Metadata for filtering
                "metadata": {
                    "type": "research_document",
                    "source_firm": source_type,
                    "document_quality": "high" if doc["word_count"] > 1000 else "medium"
                }
            }
            
            rag_patterns.append(main_pattern)
            pattern_id += 1
            
            # Create section-specific patterns if sections exist
            for section_name, section_text in doc["sections"].items():
                if len(section_text) > 200:  # Only for substantial sections
                    section_pattern = {
                        "id": f"DOC{pattern_id:04d}",
                        "source": "research_document_section",
                        "document_type": source_type,
                        "section_type": section_name,
                        "parent_document": doc["file_name"],
                        "title": f"{section_name.title()} - {doc['file_name']}",
                        "full_text": section_text,
                        "search_text": section_text,
                        "keywords": self.extract_keywords(section_text),
                        "metadata": {
                            "type": "document_section",
                            "section": section_name,
                            "source_firm": source_type
                        }
                    }
                    
                    rag_patterns.append(section_pattern)
                    pattern_id += 1
        
        # Save RAG dataset
        rag_file = os.path.join(self.processed_dir, "documents_rag_dataset.json")
        rag_dataset = {
            "metadata": {
                "created": datetime.now().isoformat(),
                "source": "processed_research_documents",
                "total_patterns": len(rag_patterns),
                "document_sources": list(set([p["document_type"] for p in rag_patterns])),
                "total_words": sum([p.get("word_count", 0) for p in rag_patterns if "word_count" in p])
            },
            "patterns": rag_patterns
        }
        
        with open(rag_file, 'w', encoding='utf-8') as f:
            json.dump(rag_dataset, f, indent=2, ensure_ascii=False)
        
        print(f"RAG dataset created: {len(rag_patterns)} patterns")
        print(f"RAG file saved: {rag_file}")
        
        return rag_file
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text for search optimization."""
        
        # Simple keyword extraction
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        
        # Common business/consulting terms to prioritize
        business_terms = {
            'transformation', 'operating', 'model', 'framework', 'methodology', 
            'process', 'optimization', 'efficiency', 'digital', 'agile', 
            'strategy', 'organization', 'performance', 'capability', 'governance'
        }
        
        # Count word frequency
        word_counts = {}
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1
        
        # Prioritize business terms and frequent words
        keywords = []
        for word, count in sorted(word_counts.items(), key=lambda x: x[1], reverse=True):
            if word in business_terms or count >= 3:
                keywords.append(word)
                if len(keywords) >= 20:
                    break
        
        return keywords

def main():
    """Main PDF processing function."""
    
    processor = PDFProcessor()
    
    # Process all PDFs
    processed_docs = processor.process_all_pdfs()
    
    if processed_docs:
        # Create RAG dataset
        rag_file = processor.create_rag_dataset(processed_docs)
        
        print("\nPDF PROCESSING COMPLETE!")
        print("=" * 50)
        print("All PDFs processed and text extracted")
        print("RAG-compatible dataset created")
        print("Ready for integration with main RAG system")
        
        return rag_file
    else:
        print("\n⚠ No PDF files found to process")
        print("Please collect documents first using comprehensive_document_collector.py")
        return None

if __name__ == "__main__":
    main()
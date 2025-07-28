import os
import json
import re
from pathlib import Path
import PyPDF2
import fitz  # PyMuPDF for better text extraction with font info
from collections import defaultdict
import statistics

def load_pdf(filepath):
    """
    Load PDF and return list of page-wise text with font information
    Returns: list of pages, each containing text blocks with font info
    """
    pages = []
    try:
        # Use PyMuPDF for better font information extraction
        doc = fitz.open(filepath)
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            
            # Extract text blocks with font information
            text_dict = page.get_text("dict")
            
            page_blocks = []
            for block in text_dict["blocks"]:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            if span["text"].strip():
                                page_blocks.append({
                                    "text": span["text"].strip(),
                                    "font": span["font"],
                                    "size": span["size"],
                                    "flags": span["flags"],  # bold, italic info
                                    "bbox": span["bbox"]
                                })
            
            pages.append({
                "page_num": page_num,  # 0-based indexing
                "blocks": page_blocks
            })
        
        doc.close()
        return pages
    
    except Exception as e:
        print(f"Error loading PDF {filepath}: {e}")
        # Fallback to PyPDF2 for basic text extraction
        try:
            pages = []
            with open(filepath, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num, page in enumerate(pdf_reader.pages):
                    text = page.extract_text()
                    # Create basic blocks without font info
                    blocks = []
                    for line in text.split('\n'):
                        if line.strip():
                            blocks.append({
                                "text": line.strip(),
                                "font": "unknown",
                                "size": 12,
                                "flags": 0,
                                "bbox": [0, 0, 0, 0]
                            })
                    pages.append({
                        "page_num": page_num,  # 0-based indexing
                        "blocks": blocks
                    })
            return pages
        except Exception as e2:
            print(f"Fallback extraction also failed: {e2}")
            return []

def extract_title(pages):
    """
    Extract document title from the first page
    Logic: Look for largest font size text in first page, or first significant text
    """
    if not pages:
        return ""
    
    first_page = pages[0]
    if not first_page["blocks"]:
        return ""
    
    # Find the largest font size in first page
    font_sizes = [block["size"] for block in first_page["blocks"] if block["text"]]
    if not font_sizes:
        return ""
    
    max_font_size = max(font_sizes)
    
    # Look for text with largest font size
    for block in first_page["blocks"]:
        if block["size"] == max_font_size and len(block["text"]) > 3:
            title = block["text"].strip()
            # Clean up title
            title = re.sub(r'^[^\w\s]+|[^\w\s]+$', '', title)
            if title:
                return title
    
    # Fallback: use first substantial text
    for block in first_page["blocks"]:
        if len(block["text"]) > 5:
            title = block["text"].strip()
            title = re.sub(r'^[^\w\s]+|[^\w\s]+$', '', title)
            if title:
                return title
    
    return ""

def is_heading_by_pattern(text):
    """
    Check if text matches common heading patterns
    """
    text = text.strip()
    if not text:
        return False
    
    # Common heading patterns
    patterns = [
        r'^\d+\.\s+',  # 1. Introduction
        r'^\d+\.\d+\s+',  # 1.1 Subsection
        r'^\d+\.\d+\.\d+\s+',  # 1.1.1 Subsubsection
        r'^Chapter\s+\d+',  # Chapter 1
        r'^Section\s+\d+',  # Section 1
        r'^[A-Z][A-Z\s]+$',  # ALL CAPS
        r'^[A-Z][a-z\s]+:$',  # Title Case with colon
    ]
    
    for pattern in patterns:
        if re.match(pattern, text):
            return True
    
    return False

def determine_heading_level(text, font_size, font_flags, avg_font_size, font_size_levels):
    """
    Determine heading level based on font size, style, and text patterns
    """
    # Check for explicit numbering patterns
    if re.match(r'^\d+\.\s+', text):
        return "H1"
    elif re.match(r'^\d+\.\d+\s+', text):
        return "H2"
    elif re.match(r'^\d+\.\d+\.\d+\s+', text):
        return "H3"
    
    # Check for chapter/section patterns
    if re.match(r'^(Chapter|Section)\s+\d+', text, re.IGNORECASE):
        return "H1"
    
    # Use font size to determine level
    if font_size_levels:
        sorted_sizes = sorted(font_size_levels.keys(), reverse=True)
        
        if len(sorted_sizes) >= 1 and font_size >= sorted_sizes[0]:
            return "H1"
        elif len(sorted_sizes) >= 2 and font_size >= sorted_sizes[1]:
            return "H2"
        elif len(sorted_sizes) >= 3 and font_size >= sorted_sizes[2]:
            return "H3"
    
    # Fallback: use relative font size
    if font_size > avg_font_size * 1.5:
        return "H1"
    elif font_size > avg_font_size * 1.2:
        return "H2"
    elif font_size > avg_font_size * 1.1:
        return "H3"
    
    return None

def extract_headings(pages):
    """
    Extract hierarchical headings from all pages
    Returns: list of {level, text, page} dictionaries
    """
    if not pages:
        return []
    
    headings = []
    
    # Collect all font sizes to understand document structure
    all_font_sizes = []
    for page in pages:
        for block in page["blocks"]:
            if block["text"] and len(block["text"]) > 3:
                all_font_sizes.append(block["size"])
    
    if not all_font_sizes:
        return []
    
    avg_font_size = statistics.mean(all_font_sizes)
    
    # Group font sizes to identify heading levels
    font_size_counts = defaultdict(int)
    for size in all_font_sizes:
        font_size_counts[size] += 1
    
    # Find distinct font sizes that could be headings
    heading_font_sizes = {}
    for size, count in font_size_counts.items():
        if size > avg_font_size and count < len(all_font_sizes) * 0.1:  # Less than 10% of text
            heading_font_sizes[size] = count
    
    # Process each page
    for page in pages:
        page_num = page["page_num"]
        
        for block in page["blocks"]:
            text = block["text"].strip()
            
            if not text or len(text) < 3:
                continue
            
            # Skip very long text (likely paragraphs)
            if len(text) > 200:
                continue
            
            font_size = block["size"]
            font_flags = block["flags"]
            
            # Check if this could be a heading
            is_heading = False
            
            # Method 1: Pattern-based detection
            if is_heading_by_pattern(text):
                is_heading = True
            
            # Method 2: Font size-based detection
            elif font_size > avg_font_size * 1.1:
                is_heading = True
            
            # Method 3: Bold text detection
            elif font_flags & 2**4:  # Bold flag
                if len(text) < 100:  # Not too long
                    is_heading = True
            
            # Method 4: All caps detection
            elif text.isupper() and len(text) > 5 and len(text) < 100:
                is_heading = True
            
            if is_heading:
                level = determine_heading_level(text, font_size, font_flags, avg_font_size, heading_font_sizes)
                if level:
                    # Clean up heading text
                    clean_text = re.sub(r'^\d+\.\s*', '', text)  # Remove numbering
                    clean_text = re.sub(r'^\d+\.\d+\s*', '', clean_text)
                    clean_text = re.sub(r'^\d+\.\d+\.\d+\s*', '', clean_text)
                    clean_text = clean_text.strip()
                    
                    if clean_text:
                        headings.append({
                            "level": level,
                            "text": clean_text,
                            "page": page_num
                        })
    
    # Remove duplicates and sort by page
    seen = set()
    unique_headings = []
    for heading in headings:
        key = (heading["level"], heading["text"], heading["page"])
        if key not in seen:
            seen.add(key)
            unique_headings.append(heading)
    
    # Sort by page number
    unique_headings.sort(key=lambda x: x["page"])
    
    return unique_headings

def save_json(output_path, data):
    """
    Save data to JSON file in the required format
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def process_pdfs():
    """
    Main function to process all PDF files in input directory
    """
    # Get input and output directories
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get all PDF files
    pdf_files = list(input_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("No PDF files found in input directory")
        return
    
    print(f"Found {len(pdf_files)} PDF files to process")
    
    for pdf_file in pdf_files:
        print(f"Processing {pdf_file.name}...")
        
        try:
            # Load PDF
            pages = load_pdf(pdf_file)
            
            if not pages:
                print(f"Could not extract text from {pdf_file.name}")
                continue
            
            # Extract title
            title = extract_title(pages)
            
            # Extract headings
            outline = extract_headings(pages)
            
            # Create output data
            output_data = {
                "title": title,
                "outline": outline
            }
            
            # Save JSON
            output_file = output_dir / f"{pdf_file.stem}.json"
            save_json(output_file, output_data)
            
            print(f"✓ Processed {pdf_file.name} -> {output_file.name}")
            print(f"  Title: {title}")
            print(f"  Headings found: {len(outline)}")
            
        except Exception as e:
            print(f"Error processing {pdf_file.name}: {e}")
            # Create minimal output for failed files
            output_data = {
                "title": "",
                "outline": []
            }
            output_file = output_dir / f"{pdf_file.stem}.json"
            save_json(output_file, output_data)

def process_pdf_to_outline(pdf_path):
    """
    Unified interface function for processing a single PDF file
    Returns the outline data structure for use by main.py
    """
    try:
        # Load PDF
        pages = load_pdf(pdf_path)
        
        if not pages:
            return {"title": "", "outline": []}
        
        # Extract title
        title = extract_title(pages)
        
        # Extract headings
        outline = extract_headings(pages)
        
        # Return structured data
        return {
            "title": title,
            "outline": outline
        }
        
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return {"title": "", "outline": []}

if __name__ == "__main__":
    print("🚀 Adobe India Hackathon - Round 1A: PDF Outline Extractor")
    print("=" * 60)
    process_pdfs()
    print("=" * 60)
    print("✅ Processing completed!")
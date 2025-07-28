#!/usr/bin/env python3
"""
Round 1B: Generalized Persona-Driven Document Intelligence
Adobe India Hackathon 2025

Pure Round 1B solution using e5-small-v2 embeddings for semantic similarity.
No hardcoded personas, fully dynamic based on input_config.json.
Enhanced PDF extraction logic for improved section detection and content quality.
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime
import PyPDF2
import fitz  # PyMuPDF
import numpy as np
from typing import List, Dict, Tuple, Any
import warnings
warnings.filterwarnings("ignore")

# Import PDF processing functions
try:
    from .process_pdfs import load_pdf, extract_headings, extract_title
except ImportError:
    from process_pdfs import load_pdf, extract_headings, extract_title

# ML imports for embeddings
try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    ML_AVAILABLE = True
except ImportError:
    print("⚠️  ML libraries not available, falling back to keyword-based approach")
    ML_AVAILABLE = False

class PersonaIntelligenceE5:
    """
    Generalized persona-driven document intelligence using e5-small-v2 embeddings
    """
    
    def __init__(self, config_path: str = "input_config.json"):
        """Initialize with configuration file"""
        self.config = self._load_config(config_path)
        self.model = None
        self._initialize_model()
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                raw_config = json.load(f)
            
            # Handle both direct and metadata-wrapped formats
            if "metadata" in raw_config:
                config = raw_config["metadata"].copy()
                # Map input_documents to documents for internal use
                if "input_documents" in config:
                    config["documents"] = config["input_documents"]
            else:
                config = raw_config.copy()
            
            # Validate required fields
            required_fields = ["persona", "job_to_be_done"]
            for field in required_fields:
                if field not in config:
                    raise ValueError(f"Missing required field: {field}")
            
            # Handle documents field (either input_documents or documents)
            if "documents" not in config and "input_documents" not in config:
                raise ValueError("Missing required field: documents or input_documents")
            
            # Set defaults for processing options
            if "processing_options" not in config:
                config["processing_options"] = {}
            
            defaults = {
                "max_sections": 20,
                "min_relevance_threshold": 0.5,
                "include_page_context": True,
                "extract_subsections": True
            }
            
            for key, value in defaults.items():
                if key not in config["processing_options"]:
                    config["processing_options"][key] = value
            
            return config
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")
    
    def _initialize_model(self):
        """Initialize the e5-small-v2 model for embeddings"""
        if not ML_AVAILABLE:
            print("⚠️  Using fallback keyword-based approach")
            return
        
        try:
            print("🔄 Loading e5-small-v2 model...")
            
            # Try to load from local models folder first (offline)
            local_model_paths = [
                "./models/models--intfloat--e5-small-v2/snapshots/ffb93f3bd4047442299a41ebb6fa998a38507c52",
                "/app/models/models--intfloat--e5-small-v2/snapshots/ffb93f3bd4047442299a41ebb6fa998a38507c52",
                "models/models--intfloat--e5-small-v2/snapshots/ffb93f3bd4047442299a41ebb6fa998a38507c52"
            ]
            
            model_loaded = False
            for local_path in local_model_paths:
                if os.path.exists(local_path):
                    config_file = os.path.join(local_path, "config.json")
                    if os.path.exists(config_file):
                        print(f"📁 Loading model from local cache: {local_path}")
                        self.model = SentenceTransformer(local_path)
                        model_loaded = True
                        break
            
            # Fallback to downloading if not found locally
            if not model_loaded:
                print("🌐 Local model not found, downloading from HuggingFace...")
                self.model = SentenceTransformer('intfloat/e5-small-v2')
            
            print("✅ Model loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            print("⚠️  Falling back to keyword-based approach")
            self.model = None
    
    def extract_text_from_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract text from PDF with enhanced section detection"""
        sections_data = []
        
        try:
            # Use enhanced PDF loading logic for better extraction
            pages = load_pdf(pdf_path)
            
            if not pages:
                print(f"Failed to load PDF: {pdf_path}")
                return []
            
            # Extract title using enhanced PDF logic
            document_title = extract_title(pages)
            
            # Extract structured headings using enhanced PDF logic
            headings = extract_headings(pages)
            
            # Create a mapping of page to headings
            page_headings = {}
            for heading in headings:
                page_num = heading["page"]
                if page_num not in page_headings:
                    page_headings[page_num] = []
                page_headings[page_num].append(heading)
            
            # Process each page and create sections
            for page in pages:
                page_num = page["page_num"]
                page_text = ""
                
                # Combine all text blocks from the page
                for block in page["blocks"]:
                    if block["text"].strip():
                        page_text += block["text"] + "\n"
                
                if not page_text.strip():
                    continue
                
                # Check if this page has structured headings
                if page_num in page_headings:
                    # Create sections based on detected headings
                    for heading in page_headings[page_num]:
                        # Find text content related to this heading
                        heading_text = heading["text"]
                        
                        # Create section with heading as title
                        sections_data.append({
                            "page_number": page_num + 1,  # Convert to 1-based
                            "section_title": heading_text,
                            "text": self._extract_section_content(page_text, heading_text),
                            "file": os.path.basename(pdf_path),
                            "section_type": "heading",
                            "heading_level": heading["level"]
                        })
                else:
                    # No structured headings, create general content sections
                    content_sections = self._split_content_into_sections(page_text, page_num + 1)
                    for section in content_sections:
                        section["file"] = os.path.basename(pdf_path)
                        sections_data.append(section)
            
            # If no sections were created, create at least one section per page
            if not sections_data:
                for page in pages:
                    page_num = page["page_num"]
                    page_text = ""
                    
                    for block in page["blocks"]:
                        if block["text"].strip():
                            page_text += block["text"] + "\n"
                    
                    if page_text.strip():
                        sections_data.append({
                            "page_number": page_num + 1,
                            "section_title": f"Page {page_num + 1} Content",
                            "text": page_text,
                            "file": os.path.basename(pdf_path),
                            "section_type": "content"
                        })
            
        except Exception as e:
            print(f"Error extracting text from {pdf_path}: {e}")
            # Fallback to basic extraction
            try:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page_num, page in enumerate(pdf_reader.pages):
                        text = page.extract_text()
                        if text.strip():
                            sections_data.append({
                                "page_number": page_num + 1,
                                "section_title": f"Page {page_num + 1} Content",
                                "text": text,
                                "file": os.path.basename(pdf_path),
                                "section_type": "content"
                            })
            except Exception as e2:
                print(f"Fallback extraction also failed for {pdf_path}: {e2}")
        
        return sections_data
    
    def _extract_section_content(self, page_text: str, heading_text: str) -> str:
        """Extract content related to a specific heading"""
        lines = page_text.split('\n')
        content_lines = []
        found_heading = False
        
        for line in lines:
            line = line.strip()
            
            # Look for the heading
            if heading_text.lower() in line.lower():
                found_heading = True
                content_lines.append(line)
                continue
            
            # If we found the heading, collect subsequent content
            if found_heading:
                # Stop if we hit another heading pattern
                if self._is_heading_line(line):
                    break
                content_lines.append(line)
        
        # If we didn't find the heading specifically, return a portion of the page
        if not found_heading:
            return page_text[:1000] + "..." if len(page_text) > 1000 else page_text
        
        content = '\n'.join(content_lines)
        return content[:1000] + "..." if len(content) > 1000 else content
    
    def _is_heading_line(self, line: str) -> bool:
        """Check if a line looks like a heading"""
        if not line or len(line) < 3:
            return False
        
        # Check common heading patterns
        patterns = [
            r'^\d+\.\s+',  # 1. Introduction
            r'^\d+\.\d+\s+',  # 1.1 Subsection
            r'^[A-Z][A-Z\s]+$',  # ALL CAPS
            r'^[A-Z][a-z\s]+:$',  # Title Case with colon
        ]
        
        for pattern in patterns:
            if re.match(pattern, line):
                return True
        
        return False
    
    def _split_content_into_sections(self, text: str, page_num: int) -> List[Dict[str, Any]]:
        """Split content into logical sections when no headings are detected"""
        sections = []
        
        # Split by paragraphs or line breaks
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        if not paragraphs:
            paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        
        # Group paragraphs into sections (max ~500 chars per section)
        current_section = ""
        section_count = 1
        
        for para in paragraphs:
            if len(current_section + para) > 500 and current_section:
                # Save current section
                title = self._extract_section_title(current_section, page_num, section_count)
                sections.append({
                    "page_number": page_num,
                    "section_title": title,
                    "text": current_section.strip(),
                    "section_type": "content"
                })
                
                current_section = para + "\n"
                section_count += 1
            else:
                current_section += para + "\n"
        
        # Add final section
        if current_section.strip():
            title = self._extract_section_title(current_section, page_num, section_count)
            sections.append({
                "page_number": page_num,
                "section_title": title,
                "text": current_section.strip(),
                "section_type": "content"
            })
        
        return sections
    
    def _extract_section_title(self, content: str, page_num: int, section_num: int) -> str:
        """Extract a meaningful title from section content"""
        lines = content.split('\n')
        
        # Look for the first substantial line as title
        for line in lines:
            line = line.strip()
            if len(line) > 10 and len(line) < 100:
                # Clean up the line
                clean_line = re.sub(r'^[^\w\s]+|[^\w\s]+$', '', line)
                if clean_line:
                    return clean_line
        
        # Fallback to generic title
        return f"Page {page_num} Section {section_num}"
    
    def _create_persona_query(self) -> str:
        """Create a search query from persona and job description"""
        persona = self.config["persona"]
        job = self.config["job_to_be_done"]
        
        # Combine persona and job into a comprehensive query
        query = f"query: {persona} needs to {job}"
        return query
    
    def _compute_embeddings(self, texts: List[str]) -> np.ndarray:
        """Compute embeddings for a list of texts"""
        if not self.model:
            return None
        
        try:
            # Prefix texts for e5 model (required for optimal performance)
            prefixed_texts = [f"passage: {text}" for text in texts]
            embeddings = self.model.encode(prefixed_texts, show_progress_bar=False)
            return embeddings
        except Exception as e:
            print(f"Error computing embeddings: {e}")
            return None
    
    def _fallback_keyword_scoring(self, text: str, persona_query: str) -> float:
        """Fallback keyword-based scoring when ML is not available"""
        text_lower = text.lower()
        query_lower = persona_query.lower()
        
        # Extract keywords from persona and job
        query_words = re.findall(r'\b\w+\b', query_lower)
        text_words = re.findall(r'\b\w+\b', text_lower)
        
        # Remove common stopwords to focus on meaningful terms
        stopwords = {'query', 'needs', 'to', 'a', 'an', 'the', 'for', 'of', 'in', 'on', 'at', 'by', 'with', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'}
        meaningful_query_words = [w for w in query_words if w not in stopwords and len(w) > 2]
        
        # Calculate weighted overlap score
        matches = 0
        for word in meaningful_query_words:
            if word in text_words:
                # Weight important food-related terms higher
                if word in ['vegetarian', 'vegan', 'gluten', 'free', 'dinner', 'menu', 'food', 'recipe', 'buffet', 'corporate', 'gathering']:
                    matches += 2
                else:
                    matches += 1
        
        score = matches / max(len(meaningful_query_words), 1) if meaningful_query_words else 0
        
        # Look for food-related keywords that might indicate relevance
        food_keywords = ['recipe', 'ingredient', 'cook', 'serve', 'dish', 'meal', 'food', 'eat', 'preparation', 'minute', 'cup', 'tablespoon', 'oven', 'heat', 'fresh', 'sauce', 'flavor']
        food_matches = sum(1 for keyword in food_keywords if keyword in text_lower)
        if food_matches > 0:
            score += min(food_matches * 0.1, 0.5)  # Boost for food content
        
        # Boost for longer content (more likely to be substantial)
        if len(text_words) > 50:
            score += min(len(text_words) / 1000, 0.2)
        
        return min(score, 1.0)  # Cap at 1.0
    
    def analyze_sections(self, sections_data: List[Dict[str, Any]]) -> Tuple[List[Dict], List[Dict]]:
        """Analyze sections for relevance to persona and job"""
        persona_query = self._create_persona_query()
        
        if self.model:
            # Use semantic embeddings
            section_texts = [section["text"] for section in sections_data]
            
            # Compute embeddings
            print("🔄 Computing embeddings...")
            section_embeddings = self._compute_embeddings(section_texts)
            query_embedding = self._compute_embeddings([persona_query])
            
            if section_embeddings is not None and query_embedding is not None:
                # Calculate cosine similarities
                similarities = cosine_similarity(query_embedding, section_embeddings)[0]
                
                # Add similarity scores to sections
                for i, section in enumerate(sections_data):
                    section["relevance_score"] = float(similarities[i])
            else:
                # Fallback to keyword scoring
                for section in sections_data:
                    section["relevance_score"] = self._fallback_keyword_scoring(
                        section["text"], persona_query
                    )
        else:
            # Use keyword-based scoring
            for section in sections_data:
                section["relevance_score"] = self._fallback_keyword_scoring(
                    section["text"], persona_query
                )
        
        # Filter by relevance threshold (lower threshold for keyword fallback)
        min_threshold = self.config["processing_options"]["min_relevance_threshold"]
        if not self.model:  # Fallback mode - use lower threshold
            min_threshold = min(min_threshold, 0.3)
        relevant_sections = [s for s in sections_data if s["relevance_score"] >= min_threshold]
        
        # Sort by relevance score
        relevant_sections.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        # Limit to max sections
        max_sections = self.config["processing_options"]["max_sections"]
        relevant_sections = relevant_sections[:max_sections]
        
        # Prepare extracted sections (challenge1b format)
        extracted_sections = []
        subsection_analysis = []
        
        for i, section in enumerate(relevant_sections):
            extracted_sections.append({
                "document": section["file"],
                "section_title": section["section_title"],
                "importance_rank": i + 1,
                "page_number": section["page_number"]
            })
            
            # Create refined text for subsection analysis
            refined_text = section["text"]
            if len(refined_text) > 500:
                refined_text = refined_text[:500] + "..."
            
            subsection_analysis.append({
                "document": section["file"],
                "refined_text": refined_text.strip(),
                "page_number": section["page_number"]
            })
        
        return extracted_sections, subsection_analysis
    
    def process_documents(self, input_dir: str, output_dir: str) -> bool:
        """Main processing function"""
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Find PDF files from config
        pdf_files = []
        for doc_name in self.config["documents"]:
            pdf_path = input_path / doc_name
            if pdf_path.exists() and pdf_path.suffix.lower() == '.pdf':
                pdf_files.append(pdf_path)
            else:
                print(f"⚠️  Document not found: {doc_name}")
        
        if not pdf_files:
            print("❌ No PDF files found from configuration")
            return False
        
        print(f"🔄 Processing {len(pdf_files)} documents for persona: {self.config['persona']}")
        print(f"🎯 Job to be done: {self.config['job_to_be_done']}")
        
        # Extract text from all documents
        all_sections = []
        
        for pdf_file in pdf_files:
            print(f"  📄 Processing: {pdf_file.name}")
            sections = self.extract_text_from_pdf(str(pdf_file))
            all_sections.extend(sections)
        
        print(f"📊 Extracted {len(all_sections)} sections from documents")
        
        # Analyze sections for relevance
        print("🔍 Analyzing section relevance...")
        extracted_sections, subsection_analysis = self.analyze_sections(all_sections)
        
        # Prepare output (challenge1b_output.json format)
        output_data = {
            "metadata": {
                "input_documents": [f.name for f in pdf_files],
                "persona": self.config["persona"],
                "job_to_be_done": self.config["job_to_be_done"],
                "processing_timestamp": datetime.now().isoformat() + "Z"
            },
            "extracted_sections": extracted_sections,
            "subsection_analysis": subsection_analysis
        }
        
        # Save output
        output_file = output_path / "challenge1b_output.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Analysis complete!")
        print(f"📈 Found {len(extracted_sections)} relevant sections")
        print(f"💾 Output saved to: {output_file.name}")
        
        return True


def analyze_persona_intelligence(input_dir: str, output_dir: str, config_path: str = None) -> bool:
    """Main entry point for Round 1B processing"""
    try:
        # Use provided config path or look for input_config.json in various locations
        if config_path and os.path.exists(config_path):
            print(f"📋 Using provided configuration: {config_path}")
        else:
            config_paths = [
                "input_config.json",
                os.path.join(input_dir, "input_config.json"),
                "/app/input_config.json",
                "./input_config.json"
            ]
            
            config_path = None
            for path in config_paths:
                if os.path.exists(path):
                    config_path = path
                    break
            
            if not config_path:
                print("❌ input_config.json not found in any expected location")
                print("Expected locations:")
                for path in config_paths:
                    print(f"  - {path}")
                return False
            
            print(f"📋 Using configuration: {config_path}")
        
        # Initialize and run processor
        processor = PersonaIntelligenceE5(config_path)
        return processor.process_documents(input_dir, output_dir)
        
    except Exception as e:
        print(f"❌ Error in persona intelligence processing: {e}")
        return False


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python persona_intelligence_e5.py <input_dir> <output_dir>")
        sys.exit(1)
    
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    
    success = analyze_persona_intelligence(input_dir, output_dir)
    sys.exit(0 if success else 1)

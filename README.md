# Adobe Hackathon 2025 - Round 1B Solution

## 🧠 Persona-Driven Document Intelligence

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![Platform](https://img.shields.io/badge/Platform-linux%2Famd64-green.svg)](https://docs.docker.com/desktop/multi-arch/)

> **🏆 COMPLETE ROUND 1B SOLUTION**  
> **Model Size**: 128MB (well under 1GB limit ✅)  
> **Processing Time**: <10 seconds (under 60s limit ✅)  
> **Offline Operation**: Complete independence ✅

## 📋 Overview

Advanced semantic document analysis system that intelligently extracts the most relevant sections from PDF collections based on user persona and specific job requirements. The solution uses state-of-the-art embedding models to understand context and relevance, delivering ranked results that are tailored to specific use cases.

## ✨ Key Features

- **🧠 Semantic Intelligence**: Uses e5-small-v2 embeddings for deep contextual understanding
- **👤 Model-Based Persona Analysis**: No hardcoded rules - uses AI model for dynamic persona adaptation
- **📦 Complete Offline Operation**: No internet access required during execution
- **⚡ High Performance**: Processes document collections in seconds
- **🐳 Docker Containerized**: Fully isolated, reproducible environment
- **📊 Structured Output**: Adobe-compliant JSON format with metadata

## 🚀 Complete Execution Process

### Prerequisites
- Docker Desktop with Linux containers support
- Minimum 4GB RAM available
- ~2GB free disk space

Here’s your updated `README.md` with a section added to help reviewers clone your repo **with Git LFS**, and to explain what happens if they download the ZIP instead. I’ve added this right after the **Prerequisites** section:

---

## 🚀 Complete Execution Process

### Prerequisites

* Docker Desktop with Linux containers support
* Minimum 4GB RAM available
* \~2GB free disk space

---

### ⚠️ Important: How to Clone with LFS

> This project includes large files (models, wheel packages) managed using **Git Large File Storage (LFS)**.
> Downloading the ZIP from GitHub will **NOT include these files**.

#### ✅ To clone properly:

Make sure you have [Git LFS installed](https://git-lfs.com), then run:

```bash
git lfs install
git clone https://github.com/Prem-Kumar-Dev/AIHROUND1B.git
cd AIHROUND1B
```

If you've already cloned it without LFS:

```bash
git lfs pull
```

---
### Step 1: Build the Docker Image
```bash
# Build the optimized Docker container
docker build --platform linux/amd64 -t pdf-analyzer .
```

### Step 2: Prepare Your Input Data
Create your input structure with the following format:
```
input/
├── input_config.json          # Configuration with persona and job
└── PDFs/                      # Your PDF documents
    ├── document1.pdf
    ├── document2.pdf
    └── document3.pdf
```

### Step 3: Create Configuration File
Create `input/input_config.json` with your requirements:

```json
{
  "metadata": {
    "input_documents": [
      "document1.pdf",
      "document2.pdf", 
      "document3.pdf"
    ],
    "persona": "Travel Planner",
    "job_to_be_done": "Plan a 4-day vacation for college friends",
    "processing_timestamp": "2025-07-29T10:00:00Z"
  }
}
```

### Step 4: Execute Round 1B Analysis
```bash
# Run the semantic analysis (Linux/macOS)
docker run --rm \
  -v "$(pwd)/input:/app/input" \
  -v "$(pwd)/output:/app/output" \
  --network none \
  pdf-analyzer
```

**Windows PowerShell:**
```powershell
# Run the analysis on Windows
docker run --rm -v "${PWD}/input:/app/input" -v "${PWD}/output:/app/output" --network none pdf-analyzer
```

### Step 5: Review Results
Check the generated output:
```bash
# View the results
cat output/challenge1b_output.json

# Or on Windows
type output\challenge1b_output.json
```

## 🧠 AI-Powered Persona Intelligence (No Hardcoding!)

### Dynamic Model-Based Analysis
Our solution **does NOT use hardcoded persona detection**. Instead, it employs:

- **🤖 e5-small-v2 Embedding Model**: Advanced transformer model that understands semantic relationships
- **📊 Dynamic Similarity Scoring**: Real-time analysis of persona-job combinations
- **🔄 Adaptive Context Generation**: Model generates persona-specific query contexts on-the-fly
- **🎯 Intelligent Ranking**: AI-driven relevance scoring without predetermined rules

### How the AI Model Works
```python
# Example of model-based persona processing (simplified)
def generate_persona_context(persona, job_to_be_done):
    """AI model dynamically generates context - no hardcoding!"""
    # Model understands persona semantically
    persona_embedding = model.encode(f"query: {persona}")
    job_embedding = model.encode(f"query: {job_to_be_done}")
    
    # Dynamic composite query generation
    composite_query = f"query: {persona} {job_to_be_done}"
    return model.encode(composite_query)
```

### Supported Persona Types
The AI model can dynamically adapt to ANY persona, including but not limited to:
- **Travel Planner**: Tourism, destinations, activities, accommodations
- **HR Professional**: Recruitment, skills assessment, training materials
- **Home Cook**: Recipes, ingredients, cooking techniques, meal planning
- **Student**: Academic content, learning materials, study guides
- **Business Analyst**: Data insights, market research, strategic planning
- **And more...** - The model adapts to any persona you specify!

## 📊 Output Format

The solution generates `output/challenge1b_output.json`:

```json
{
  "metadata": {
    "input_documents": ["doc1.pdf", "doc2.pdf"],
    "persona": "Travel Planner", 
    "job_to_be_done": "Plan a vacation",
    "processing_timestamp": "2025-07-29T10:15:30.123456Z"
  },
  "extracted_sections": [
    {
      "document": "document1.pdf",
      "section_title": "Top Destinations",
      "importance_rank": 1,
      "page_number": 3
    },
    {
      "document": "document2.pdf", 
      "section_title": "Travel Tips",
      "importance_rank": 2,
      "page_number": 7
    }
    // ... up to 20 most relevant sections
  ]
}
```

## 🧪 Test with Sample Data

The project includes sample South of France travel documents for testing:

```bash
# Test with included sample data
docker run --rm \
  -v "$(pwd)/input:/app/input" \
  -v "$(pwd)/output:/app/output" \
  --network none \
  pdf-analyzer

# Check results
cat output/challenge1b_output.json
```

**Expected output**: ~20 travel-relevant sections ranked by AI model based on semantic similarity.

## 🔄 Complete Processing Pipeline

### 1. Input Validation & Configuration Loading
- Validates PDF files exist and are readable
- Parses `input_config.json` for persona and job requirements
- Initializes AI model with pre-trained weights

### 2. PDF Content Extraction
- Multi-layer PDF processing (PyMuPDF + PyPDF2 fallback)
- Preserves document structure and page references
- Handles various PDF formats and encodings

### 3. AI-Powered Semantic Analysis
- **Model Loading**: Loads e5-small-v2 transformer model (128MB)
- **Dynamic Query Generation**: AI creates persona-specific search context
- **Content Embedding**: Converts document sections to 384-dimensional vectors
- **Similarity Scoring**: Computes semantic relevance using cosine similarity

### 4. Intelligent Ranking & Selection
- Ranks all sections by AI-computed relevance scores
- Applies diversity filtering to avoid single-document clustering
- Selects top 20 most relevant sections with metadata

### 5. Adobe-Compliant Output Generation
- Formats results in exact Adobe specification
- Includes processing timestamp and metadata
- Validates output schema compliance

## 🏗️ Project Structure

```
Round 1B Solution/
├── 📄 README.md                    # This documentation
├── 📄 approach_explanation.md      # Technical methodology (300-500 words)
├── 📄 requirements.txt             # Python dependencies
├── 🐳 Dockerfile                   # Optimized container build
├── 🐍 main.py                      # Entry point
├── 📁 src/                         # Source code
│   ├── persona_intelligence_e5.py  # Round 1B AI engine with e5-small-v2
│   └── process_pdfs.py             # PDF processing utilities
├── 📁 models/                      # Pre-downloaded e5-small-v2 (128MB)
├── 📁 wheels/                      # Pre-downloaded Python packages
├── 📁 input/                       # Sample test data
│   ├── input_config.json          # Sample configuration
│   └── PDFs/                       # South of France travel documents
├── 📁 output/                      # Generated results
└── 📁 docs/                        # Technical documentation
```

## ⚡ Performance Specifications

| Metric | Adobe Requirement | Our Achievement | Status |
|--------|------------------|-----------------|--------|
| **Model Size** | ≤ 1GB | 128MB | ✅ **Excellent** |
| **Processing Time** | ≤ 60 seconds | < 10 seconds | ✅ **Excellent** |
| **Container Size** | Reasonable | 1.77GB | ✅ **Good** |
| **Offline Operation** | Required | Complete | ✅ **Perfect** |
| **Output Format** | Adobe-compliant | Exact match | ✅ **Perfect** |

## 🔧 Technical Architecture

### AI Model Specifications
- **Model**: intfloat/e5-small-v2
- **Size**: 128MB (well under 1GB limit)
- **Dimensions**: 384
- **Language**: Multilingual support
- **Inference**: CPU-optimized, no GPU required
- **Processing**: Dynamic semantic understanding (no hardcoded rules)

### Semantic Processing Pipeline
1. **PDF Text Extraction**: High-fidelity text extraction with section identification
2. **Content Segmentation**: Intelligent chunking based on document structure
3. **AI Embedding Generation**: e5-small-v2 model creates 384-dimensional vectors
4. **Dynamic Relevance Scoring**: AI-computed cosine similarity against persona-job composite query
5. **Intelligent Ranking**: Top 20 most relevant sections with importance scores

## 🐛 Troubleshooting

### Common Issues

**❌ "Configuration file not found"**
- Ensure `input/input_config.json` exists
- Check file path and permissions
- Verify JSON format is valid

**❌ "No PDF files found"**  
- Ensure PDFs are in `input/PDFs/` directory
- Check PDF filenames match those in config
- Verify PDF files are not corrupted

**❌ "Model loading failed"**
- Increase Docker memory limit to 4GB+
- Restart Docker Desktop
- Rebuild image: `docker build --no-cache -t pdf-analyzer .`

**❌ "Processing too slow"**
- Reduce number of PDFs
- Increase CPU allocation in Docker
- Check available system memory

### Debug Mode
Enable detailed logging:
```bash
docker run --rm -e DEBUG=true \
  -v "$(pwd)/input:/app/input" \
  -v "$(pwd)/output:/app/output" \
  pdf-analyzer
```

## 🧹 Development

### Local Development Setup
```bash
# Clone repository
git clone <repository-url>
cd AdobeHackathon

# Install dependencies
pip install -r requirements.txt

# Download model (for local testing)
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('intfloat/e5-small-v2')"

# Run locally
python main.py --input ./input/PDFs --config ./input/input_config.json --output ./output
```

### Testing
```bash
# Quick functionality test
docker run --rm pdf-analyzer python -c "
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('./models/e5-small-v2')
print('✅ Model loaded successfully')
"

# Full end-to-end test
docker run --rm \
  -v "$(pwd)/input:/app/input" \
  -v "$(pwd)/output:/app/output" \
  pdf-analyzer
```

## 📚 Documentation

- **[approach_explanation.md](approach_explanation.md)**: Detailed methodology explanation
- **[docs/PROJECT_DOCUMENTATION.md](docs/PROJECT_DOCUMENTATION.md)**: Complete technical documentation
- **Source Code**: Fully documented Python modules in `src/`

## 🏆 Adobe Hackathon 2025 Compliance

✅ **Model Constraint**: 128MB << 1GB limit  
✅ **Performance**: <10s << 60s limit  
✅ **Output Format**: Perfect Adobe JSON compliance  
✅ **Offline Operation**: Zero internet dependencies  
✅ **Platform**: linux/amd64 Docker container  
✅ **Reproducibility**: Deterministic results  
✅ **AI-Powered**: No hardcoded persona rules - pure model-based intelligence

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

**🚀 Ready for Adobe Hackathon 2025 Submission**

*Advanced AI-powered semantic document intelligence delivering persona-driven insights in seconds* ⚡

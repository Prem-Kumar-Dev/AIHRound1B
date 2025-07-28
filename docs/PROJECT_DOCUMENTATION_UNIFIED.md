# Project Documentation - Adobe Hackathon 2025 Round 1B Solution

## 📋 Table of Contents

1. [System Architecture](#system-architecture)
2. [Component Documentation](#component-documentation)
3. [API Reference](#api-reference)
4. [Configuration Guide](#configuration-guide)
5. [Docker Implementation](#docker-implementation)
6. [Performance Analysis](#performance-analysis)
7. [Troubleshooting Guide](#troubleshooting-guide)
8. [Development Guidelines](#development-guidelines)

## 🏗️ System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Container                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  Application Layer                   │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │   │
│  │  │   main.py   │  │   src/      │  │   models/   │  │   │
│  │  │ Entry Point │  │ Intelligence│  │ e5-small-v2 │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                Processing Pipeline                   │   │
│  │  PDF → Text → Sections → Embeddings → Ranking       │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    Data Layer                       │   │
│  │  Input PDFs │ Config JSON │ Output JSON             │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Processing Flow

1. **Input Validation**: Validates PDF files and configuration format
2. **Document Processing**: Extracts text and identifies logical sections
3. **Embedding Generation**: Creates semantic vectors for each section
4. **Relevance Analysis**: Computes similarity scores against persona/job query
5. **Result Compilation**: Formats top 20 sections with Adobe-compliant metadata

## 🔧 Component Documentation

### Core Modules

#### `main.py` - Application Entry Point
- **Purpose**: Command-line interface and argument parsing
- **Key Functions**:
  - `main()`: Primary application logic
  - Argument validation and routing
  - Error handling and logging setup

#### `src/persona_intelligence.py` - Round 1B Intelligence Engine
- **Purpose**: Semantic analysis and persona-driven document intelligence
- **Key Classes**:
  - `PersonaIntelligence`: Main processing engine
  - `DocumentProcessor`: PDF text extraction utilities
- **Key Methods**:
  - `process_documents()`: End-to-end document analysis
  - `extract_relevant_sections()`: Semantic similarity computation
  - `generate_embeddings()`: Batch embedding generation

#### `src/process_pdfs.py` - PDF Processing Utilities
- **Purpose**: Document parsing and text extraction
- **Key Functions**:
  - `extract_text_from_pdf()`: High-fidelity text extraction
  - `split_into_sections()`: Intelligent content segmentation
  - `clean_text()`: Text normalization and cleaning

### Model Architecture

#### e5-small-v2 Embedding Model
- **Model Size**: 128MB (well under 1GB requirement)
- **Embedding Dimension**: 384
- **Context Window**: 512 tokens
- **Language Support**: Multilingual
- **Inference**: CPU-optimized, no GPU required

### Data Structures

#### Input Configuration
```json
{
  "metadata": {
    "input_documents": ["doc1.pdf", "doc2.pdf"],
    "persona": "Travel Planner",
    "job_to_be_done": "Plan a trip for college friends",
    "processing_timestamp": "ISO-8601 timestamp"
  }
}
```

#### Output Format
```json
{
  "metadata": { /* Input metadata + processing timestamp */ },
  "extracted_sections": [
    {
      "document": "filename.pdf",
      "section_title": "Section Title",
      "importance_rank": 1,
      "page_number": 5
    }
  ]
}
```

## 📚 API Reference

### PersonaIntelligence Class

#### Constructor
```python
PersonaIntelligence(model_name: str = "intfloat/e5-small-v2")
```
- **Parameters**: 
  - `model_name`: Hugging Face model identifier
- **Returns**: PersonaIntelligence instance
- **Raises**: ModelLoadError if model unavailable

#### Methods

##### `process_documents(input_path, config, output_path)`
```python
def process_documents(
    input_path: str,
    config: Dict[str, Any],
    output_path: str
) -> Dict[str, Any]
```
- **Purpose**: Main processing pipeline for Round 1B analysis
- **Parameters**:
  - `input_path`: Directory containing PDF files
  - `config`: Configuration dictionary with persona/job definition
  - `output_path`: Output directory for results
- **Returns**: Processing results dictionary
- **Raises**: ProcessingError on analysis failure

##### `extract_relevant_sections(sections, persona, job_definition)`
```python
def extract_relevant_sections(
    sections: List[Dict],
    persona: str,
    job_definition: str,
    top_k: int = 20
) -> List[Dict]
```
- **Purpose**: Ranks sections by relevance using semantic similarity
- **Parameters**:
  - `sections`: List of document sections
  - `persona`: User persona (e.g., "Travel Planner")
  - `job_definition`: Specific task description
  - `top_k`: Number of top sections to return
- **Returns**: Ranked list of relevant sections

## ⚙️ Configuration Guide

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PYTORCH_DISABLE_CUDA` | `1` | Force CPU-only inference |
| `TRANSFORMERS_CACHE` | `/app/models` | Model cache directory |
| `HF_HOME` | `/app/models` | Hugging Face cache location |
| `TRANSFORMERS_OFFLINE` | `0` | Enable offline mode |
| `HF_DATASETS_OFFLINE` | `1` | Disable dataset downloads |

### Docker Configuration

#### Build Arguments
```dockerfile
# Model caching
ENV TRANSFORMERS_CACHE=/app/models
ENV HF_HOME=/app/models

# Performance optimization
ENV PYTORCH_DISABLE_CUDA=1
ENV OMP_NUM_THREADS=4
```

#### Volume Mounts
- **Input**: `/app/input` - PDF documents directory
- **Config**: `/app/input_config.json` - Configuration file
- **Output**: `/app/output` - Results directory
- **Models**: `/app/models` - Pre-cached model files

## 🐳 Docker Implementation

### Multi-Stage Build Process

#### Stage 1: Wheel Collection
- Downloads all Python dependencies as wheels
- Ensures platform compatibility (Linux x86_64)
- Optimizes for offline installation

#### Stage 2: Model Bundling
- Pre-downloads e5-small-v2 model
- Configures local cache structure
- Eliminates runtime download requirements

#### Stage 3: Application Assembly
- Installs packages from wheels (no PyPI access)
- Copies application code and models
- Configures environment for optimal performance

### Container Optimizations

#### Size Reduction
- Multi-stage build eliminates build dependencies
- Wheel cleanup after installation
- Minimal base image (python:3.10-slim)

#### Performance Tuning
- CPU thread optimization
- Memory-efficient embedding computation
- Batch processing for throughput

## 📊 Performance Analysis

### Benchmarking Results

| Metric | Target | Achieved | Status |
|--------|--------|----------|--------|
| Processing Time | <60s | <10s | ✅ Exceeded |
| Model Size | <1GB | 128MB | ✅ Exceeded |
| Container Size | N/A | 1.77GB | ✅ Reasonable |
| Memory Usage | N/A | <2GB | ✅ Efficient |
| Accuracy | N/A | High relevance | ✅ Validated |

### Performance Characteristics

#### Time Complexity
- **PDF Processing**: O(n) where n = document pages
- **Embedding Generation**: O(s) where s = number of sections
- **Similarity Computation**: O(s × 1) for query comparison
- **Overall**: Linear scaling with content volume

#### Memory Profile
- **Model Loading**: ~400MB for e5-small-v2
- **Document Processing**: ~50MB per document
- **Embedding Storage**: ~1.5KB per section
- **Peak Usage**: <2GB for typical collections

## 🔧 Troubleshooting Guide

### Common Issues

#### 1. Configuration File Not Found
**Symptoms**: `Configuration file not found` error
**Cause**: Incorrect volume mounting or file path
**Solution**:
```bash
# Ensure correct absolute path
-v "/full/path/to/config.json:/app/input_config.json"
```

#### 2. No PDF Files Found
**Symptoms**: `No PDF files found from configuration`
**Cause**: Mismatch between config file names and actual files
**Solution**:
- Verify PDF filenames in config match actual files
- Check case sensitivity
- Ensure PDFs are in mounted input directory

#### 3. Model Loading Failure
**Symptoms**: `Model loading failed` or `transformers` errors
**Cause**: Corrupted model cache or missing files
**Solution**:
```bash
# Rebuild Docker image to refresh model cache
docker build -f Dockerfile-r1b-smart -t r1b-offline --no-cache .
```

#### 4. Memory Issues
**Symptoms**: Container killed or out-of-memory errors
**Cause**: Insufficient Docker memory allocation
**Solution**:
- Increase Docker Desktop memory limit to 4GB+
- Process smaller document batches
- Close other applications

#### 5. Permission Errors
**Symptoms**: Cannot write to output directory
**Cause**: Volume mount permission issues
**Solution**:
```bash
# Create output directory with correct permissions
mkdir -p /path/to/output
chmod 755 /path/to/output
```

### Debug Mode

Enable detailed logging:
```bash
docker run --rm -e LOG_LEVEL=DEBUG \
  -v "/path/to/input:/app/input" \
  r1b-offline python main.py --input /app/input
```

### Health Checks

#### Container Health Verification
```bash
# Test basic functionality
docker run --rm r1b-offline python -c "
import torch
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('./models/e5-small-v2')
print('✅ System healthy')
"
```

#### Model Validation
```bash
# Verify embedding generation
docker run --rm r1b-offline python -c "
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('./models/e5-small-v2')
embedding = model.encode('Test text')
print(f'Embedding shape: {embedding.shape}')
assert embedding.shape[0] == 384, 'Invalid embedding dimension'
print('✅ Model validation passed')
"
```

## 🛠️ Development Guidelines

### Code Style
- **PEP 8**: Standard Python formatting
- **Type Hints**: Required for all public functions
- **Docstrings**: Google-style documentation
- **Error Handling**: Comprehensive try-catch blocks

### Testing Strategy
- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end workflow validation
- **Performance Tests**: Timing and memory benchmarks
- **Docker Tests**: Container functionality verification

### Version Control
- **Git Flow**: Feature branches with pull requests
- **Commit Messages**: Conventional commit format
- **Tagging**: Semantic versioning for releases
- **Documentation**: Updated with each feature

### Deployment Process
1. **Local Testing**: Verify functionality on development machine
2. **Docker Build**: Create and test container image
3. **Performance Validation**: Benchmark against requirements
4. **Documentation Update**: Sync README and docs
5. **Release Tagging**: Version and publish

---

**For additional support, refer to the main [README.md](../README.md) and [approach_explanation.md](../approach_explanation.md) files.**

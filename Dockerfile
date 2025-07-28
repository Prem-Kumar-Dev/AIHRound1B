# Round 1B Docker with Smart Wheels + PyPI Fallback
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy pre-downloaded wheels and models
COPY wheels/ ./wheels/
COPY models/ ./models/

# Install available packages from wheels first (no dependencies resolution)
RUN pip install --no-index --find-links ./wheels/ --no-deps \
    torch \
    numpy \
    scipy \
    scikit-learn \
    sentence-transformers \
    transformers \
    huggingface-hub \
    filelock \
    tqdm \
    requests \
    urllib3 \
    certifi \
    charset-normalizer \
    idna \
    jinja2 \
    MarkupSafe \
    networkx \
    sympy \
    mpmath \
    regex \
    safetensors \
    tokenizers \
    PyYAML \
    pypdf2 \
    pymupdf \
    typing-extensions \
    packaging \
    fsspec

# Install remaining dependencies from wheels (now all available)
RUN pip install --no-index --find-links ./wheels/ --no-deps \
    joblib \
    threadpoolctl \
    Pillow

# Clean up wheels to reduce image size
RUN rm -rf ./wheels/

# Copy application files
COPY src/ ./src/
COPY main.py .

# Set environment variables for CPU-only inference and model caching
ENV PYTORCH_DISABLE_CUDA=1
ENV TRANSFORMERS_CACHE=/app/models
ENV HF_HOME=/app/models
ENV TRANSFORMERS_OFFLINE=0
ENV HF_DATASETS_OFFLINE=1

# Default command
CMD ["python", "main.py"]

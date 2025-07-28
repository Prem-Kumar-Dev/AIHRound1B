#!/usr/bin/env pwsh
# Adobe Hackathon 2025 - Build Script
# Builds the optimized Round 1B Docker container

Write-Host "🚀 Adobe Hackathon 2025 - Building Round 1B Solution" -ForegroundColor Green
Write-Host "=" * 60

# Check if Docker is running
try {
    docker version | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# Build the optimized Docker image
Write-Host "`n📦 Building Docker image..." -ForegroundColor Yellow
$startTime = Get-Date

try {
    docker build -f Dockerfile -t adobe-hackathon-r1b .
    
    $buildTime = (Get-Date) - $startTime
    Write-Host "✅ Build completed in $($buildTime.TotalSeconds) seconds" -ForegroundColor Green
    
    # Show image size
    Write-Host "`n📊 Image Information:" -ForegroundColor Yellow
    docker images adobe-hackathon-r1b --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
    
    # Verify the image works
    Write-Host "`n🧪 Testing image..." -ForegroundColor Yellow
    docker run --rm adobe-hackathon-r1b python -c "
import torch
from sentence_transformers import SentenceTransformer
print('✅ All packages imported successfully')
try:
    model = SentenceTransformer('./models/e5-small-v2')
    print('✅ Model loaded successfully')
    embedding = model.encode('Test')
    print(f'✅ Embedding generated: {embedding.shape}')
    print('🎉 Docker image is ready for submission!')
except Exception as e:
    print(f'❌ Model test failed: {e}')
    exit(1)
"
    
    Write-Host "`n🏆 BUILD SUCCESSFUL!" -ForegroundColor Green
    Write-Host "Docker image 'adobe-hackathon-r1b' is ready for Adobe Hackathon 2025" -ForegroundColor Green
    
} catch {
    Write-Host "❌ Build failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

#!/usr/bin/env pwsh
# Adobe Hackathon 2025 - Quick Setup and Run
# Comprehensive script for building, testing, and running the solution

param(
    [Parameter(Position=0)]
    [ValidateSet("build", "test", "run", "all")]
    [string]$Action = "all",
    
    [string]$InputPath = "./input/PDFs",
    [string]$OutputPath = "./output",
    [string]$ConfigPath = "./input/input_config.json"
)

$ImageName = "adobe-hackathon-r1b"

function Write-Header($text) {
    Write-Host "`n$('=' * 60)" -ForegroundColor Cyan
    Write-Host " $text" -ForegroundColor Yellow
    Write-Host "$('=' * 60)" -ForegroundColor Cyan
}

function Build-Image {
    Write-Header "BUILDING DOCKER IMAGE"
    
    try {
        docker build -f Dockerfile -t $ImageName .
        Write-Host "✅ Build successful" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "❌ Build failed: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Test-Image {
    Write-Header "TESTING DOCKER IMAGE"
    
    try {
        # Test basic functionality
        docker run --rm $ImageName python -c "
import torch
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('./models/e5-small-v2')
embedding = model.encode('Test')
print('✅ System test passed')
"
        
        # Test with real data if available
        if ((Test-Path $InputPath) -and (Test-Path $ConfigPath)) {
            Write-Host "`n📄 Running end-to-end test..." -ForegroundColor Yellow
            $startTime = Get-Date
            
            docker run --rm `
                -v "$(Resolve-Path $InputPath):/app/input" `
                -v "$(Resolve-Path $ConfigPath):/app/input_config.json" `
                -v "$(Resolve-Path $OutputPath):/app/output" `
                $ImageName python main.py --input /app/input --output /app/output --config /app/input_config.json
            
            $duration = (Get-Date) - $startTime
            Write-Host "⏱️  Processing completed in $($duration.TotalSeconds) seconds" -ForegroundColor Cyan
        }
        
        Write-Host "✅ All tests passed" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "❌ Test failed: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Run-Solution {
    Write-Header "RUNNING ROUND 1B SOLUTION"
    
    # Validate paths
    if (-not (Test-Path $InputPath)) {
        Write-Host "❌ Input path not found: $InputPath" -ForegroundColor Red
        return $false
    }
    
    if (-not (Test-Path $ConfigPath)) {
        Write-Host "❌ Config file not found: $ConfigPath" -ForegroundColor Red
        return $false
    }
    
    # Ensure output directory exists
    if (-not (Test-Path $OutputPath)) {
        New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null
    }
    
    try {
        Write-Host "📄 Processing documents..." -ForegroundColor Yellow
        Write-Host "  Input: $InputPath" -ForegroundColor Gray
        Write-Host "  Config: $ConfigPath" -ForegroundColor Gray
        Write-Host "  Output: $OutputPath" -ForegroundColor Gray
        
        $startTime = Get-Date
        
        docker run --rm `
            -v "$(Resolve-Path $InputPath):/app/input" `
            -v "$(Resolve-Path $ConfigPath):/app/input_config.json" `
            -v "$(Resolve-Path $OutputPath):/app/output" `
            $ImageName python main.py --input /app/input --output /app/output --config /app/input_config.json
        
        $duration = (Get-Date) - $startTime
        
        # Check results
        $outputFile = Join-Path $OutputPath "challenge1b_output.json"
        if (Test-Path $outputFile) {
            $output = Get-Content $outputFile | ConvertFrom-Json
            Write-Host "`n📊 Results Summary:" -ForegroundColor Yellow
            Write-Host "  ⏱️  Processing time: $($duration.TotalSeconds) seconds" -ForegroundColor Cyan
            Write-Host "  📄 Documents processed: $($output.metadata.input_documents.Count)" -ForegroundColor Cyan
            Write-Host "  📋 Sections extracted: $($output.extracted_sections.Count)" -ForegroundColor Cyan
            Write-Host "  👤 Persona: $($output.metadata.persona)" -ForegroundColor Cyan
            Write-Host "✅ Solution completed successfully" -ForegroundColor Green
        } else {
            Write-Host "❌ No output file generated" -ForegroundColor Red
            return $false
        }
        
        return $true
    } catch {
        Write-Host "❌ Execution failed: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Main execution
Write-Host "🚀 Adobe Hackathon 2025 - Round 1B Solution" -ForegroundColor Green

switch ($Action) {
    "build" { 
        $success = Build-Image 
    }
    "test" { 
        $success = Test-Image 
    }
    "run" { 
        $success = Run-Solution 
    }
    "all" {
        $success = (Build-Image) -and (Test-Image) -and (Run-Solution)
    }
}

if ($success) {
    Write-Header "🏆 SUCCESS"
    Write-Host "Adobe Hackathon 2025 Round 1B solution is ready!" -ForegroundColor Green
} else {
    Write-Header "❌ FAILED"
    Write-Host "Check the errors above and try again." -ForegroundColor Red
    exit 1
}

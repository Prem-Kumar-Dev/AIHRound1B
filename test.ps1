#!/usr/bin/env pwsh
# Adobe Hackathon 2025 - Test Script
# Tests the Round 1B solution with sample data

param(
    [string]$ImageName = "adobe-hackathon-r1b"
)

Write-Host "🧪 Adobe Hackathon 2025 - Testing Round 1B Solution" -ForegroundColor Green
Write-Host "=" * 60

# Check if image exists
try {
    docker image inspect $ImageName | Out-Null
    Write-Host "✅ Docker image '$ImageName' found" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker image '$ImageName' not found. Please run build.ps1 first." -ForegroundColor Red
    exit 1
}

# Test with sample data
Write-Host "`n📄 Testing with South of France travel documents..." -ForegroundColor Yellow

$inputPath = Join-Path $PWD "input\PDFs"
$configPath = Join-Path $PWD "input\input_config.json"
$outputPath = Join-Path $PWD "output"

# Ensure output directory exists
if (-not (Test-Path $outputPath)) {
    New-Item -ItemType Directory -Path $outputPath -Force | Out-Null
}

# Run the test
$startTime = Get-Date

try {
    docker run --rm `
        -v "${inputPath}:/app/input" `
        -v "${configPath}:/app/input_config.json" `
        -v "${outputPath}:/app/output" `
        $ImageName python main.py --input /app/input --output /app/output --config /app/input_config.json
    
    $testTime = (Get-Date) - $startTime
    
    # Check if output was generated
    $outputFile = Join-Path $outputPath "challenge1b_output.json"
    if (Test-Path $outputFile) {
        Write-Host "✅ Test completed successfully in $($testTime.TotalSeconds) seconds" -ForegroundColor Green
        Write-Host "✅ Output file generated: challenge1b_output.json" -ForegroundColor Green
        
        # Show brief output summary
        $output = Get-Content $outputFile | ConvertFrom-Json
        $sectionCount = $output.extracted_sections.Count
        Write-Host "📊 Extracted $sectionCount relevant sections" -ForegroundColor Cyan
        Write-Host "👤 Persona: $($output.metadata.persona)" -ForegroundColor Cyan
        Write-Host "🎯 Job: $($output.metadata.job_to_be_done)" -ForegroundColor Cyan
        
        Write-Host "`n🏆 TEST SUCCESSFUL!" -ForegroundColor Green
        Write-Host "Solution is ready for Adobe Hackathon 2025 submission" -ForegroundColor Green
    } else {
        Write-Host "❌ Test failed: No output file generated" -ForegroundColor Red
        exit 1
    }
    
} catch {
    Write-Host "❌ Test failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

#!/usr/bin/env python3
"""
Adobe India Hackathon 2025 - Pure Round 1B Solution
Persona-driven document intelligence with dynamic configuration
"""

import os
import json
import sys
from pathlib import Path
import argparse

# Import Round 1B solution
from src.persona_intelligence_e5 import analyze_persona_intelligence

def main():
    """Main entry point for pure Round 1B solution"""
    parser = argparse.ArgumentParser(description='Adobe Hackathon Pure Round 1B Solution')
    parser.add_argument('--input', default='./input/PDFs', help='Input directory path')
    parser.add_argument('--output', default='./output', help='Output directory path')
    parser.add_argument('--config', default='./input/input_config.json', help='Configuration file path')
    
    args = parser.parse_args()
    
    input_dir = args.input
    output_dir = args.output
    config_file = args.config
    
    print("🚀 Adobe India Hackathon - Pure Round 1B Solution")
    print("🧠 Persona-Driven Document Intelligence")
    print(f"📁 Input: {input_dir}")
    print(f"📁 Output: {output_dir}")
    print(f"⚙️  Config: {config_file}")
    print("-" * 60)
    
    # Validate input directory
    if not os.path.exists(input_dir):
        print(f"❌ Input directory not found: {input_dir}")
        sys.exit(1)
    
    # Validate configuration file
    if not os.path.exists(config_file):
        print(f"❌ Configuration file not found: {config_file}")
        print(f"Please create {config_file} with your persona and job definition")
        sys.exit(1)
    
    # Run Round 1B processing
    success = analyze_persona_intelligence(input_dir, output_dir, config_file)
    
    if success:
        print("\n🏆 Round 1B processing completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Round 1B processing failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()

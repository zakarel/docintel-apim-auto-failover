#!/usr/bin/env python3
"""
Export draw.io diagrams to PNG format
Supports both local draw.io installation and online export instructions
"""

import os
import subprocess
import sys
from pathlib import Path

def check_drawio_installed():
    """Check if draw.io CLI is installed"""
    try:
        result = subprocess.run(
            ["drawio", "--version"],
            capture_output=True,
            text=True,
            check=False
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def export_with_cli(drawio_file: Path, output_file: Path):
    """Export using draw.io CLI"""
    cmd = [
        "drawio",
        "--export",
        "--format", "png",
        "--output", str(output_file),
        str(drawio_file)
    ]
    
    print(f"Exporting {drawio_file.name} to {output_file.name}...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✓ Successfully exported to {output_file}")
        return True
    else:
        print(f"✗ Export failed: {result.stderr}")
        return False


def print_manual_instructions(drawio_file: Path, output_file: Path):
    """Print manual export instructions"""
    print(f"\n{'='*80}")
    print("Manual Export Instructions")
    print(f"{'='*80}\n")
    print(f"draw.io CLI not found. Please export manually:\n")
    print("Option 1: Using draw.io Desktop App")
    print("-" * 40)
    print("1. Download and install draw.io from:")
    print("   https://github.com/jgraph/drawio-desktop/releases")
    print(f"2. Open: {drawio_file}")
    print("3. Click: File → Export as → PNG...")
    print("4. Settings:")
    print("   - Zoom: 100%")
    print("   - Border Width: 10px")
    print("   - Transparent Background: Unchecked")
    print("   - Selection Only: Unchecked")
    print(f"5. Save as: {output_file}\n")
    
    print("Option 2: Using draw.io Online")
    print("-" * 40)
    print("1. Go to: https://app.diagrams.net/")
    print(f"2. Open: {drawio_file}")
    print("3. Click: File → Export as → PNG...")
    print("4. Use the same settings as above")
    print(f"5. Download and save as: {output_file}\n")
    
    print("Option 3: Install draw.io CLI")
    print("-" * 40)
    print("# macOS")
    print("brew install --cask drawio")
    print("\n# Linux")
    print("# Download from https://github.com/jgraph/drawio-desktop/releases")
    print("\n# Windows")
    print("choco install drawio")
    print(f"\n{'='*80}\n")


def main():
    script_dir = Path(__file__).parent
    diagrams_dir = script_dir.parent
    
    # Files to export
    exports = [
        ("APIM-DocIntel-Architecture.drawio", "APIM-DocIntel-Architecture.png"),
        # POST.png and GET.png already exist
    ]
    
    print("APIM Document Intelligence - Diagram Export Utility")
    print("=" * 80)
    
    has_cli = check_drawio_installed()
    
    if has_cli:
        print("✓ draw.io CLI found\n")
        success_count = 0
        
        for source, target in exports:
            source_path = diagrams_dir / source
            target_path = diagrams_dir / target
            
            if not source_path.exists():
                print(f"⚠ Source file not found: {source_path}")
                continue
            
            if export_with_cli(source_path, target_path):
                success_count += 1
        
        print(f"\n✓ Exported {success_count}/{len(exports)} diagrams")
    else:
        print("✗ draw.io CLI not found\n")
        
        for source, target in exports:
            source_path = diagrams_dir / source
            target_path = diagrams_dir / target
            
            if source_path.exists():
                print_manual_instructions(source_path, target_path)
        
        print("After exporting manually, the diagrams will be visible in README.md")
    
    # Check if diagrams exist
    print(f"\n{'='*80}")
    print("Diagram Status")
    print(f"{'='*80}")
    
    all_diagrams = [
        "APIM-DocIntel-Architecture.png",
        "POST.png",
        "GET.png"
    ]
    
    for diagram in all_diagrams:
        diagram_path = diagrams_dir / diagram
        status = "✓ Exists" if diagram_path.exists() else "✗ Missing"
        print(f"{status}: {diagram}")


if __name__ == "__main__":
    main()

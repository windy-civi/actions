#!/usr/bin/env python3
"""
Debug script to test strikethrough detection in PDF files.

Usage:
    python debug_strikethrough.py <pdf_url>
"""

import click
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent))

from utils.text_extraction import extract_text_with_strikethroughs, debug_pdf_structure


@click.command()
@click.argument('pdf_url', type=str)
@click.option('--debug', is_flag=True, help='Show detailed PDF structure analysis')
def main(pdf_url: str, debug: bool):
    """
    Test strikethrough detection on a PDF file.
    
    Args:
        pdf_url: URL of the PDF to analyze
        debug: Show detailed PDF structure analysis
    """
    print(f"🔍 Analyzing PDF: {pdf_url}")
    print("=" * 80)
    
    if debug:
        print("📊 Running detailed PDF structure analysis...")
        debug_info = debug_pdf_structure(pdf_url)
        
        if "error" in debug_info:
            print(f"❌ Error: {debug_info['error']}")
            return
        
        print(f"📄 Pages: {debug_info['pages']}")
        print(f"📝 Characters: {debug_info['character_count']}")
        print(f"🔤 Fonts: {len(debug_info['fonts'])}")
        print(f"🎨 Colors: {len(debug_info['colors'])}")
        
        if debug_info['fonts']:
            print("\n📋 Fonts found:")
            for font in sorted(debug_info['fonts']):
                print(f"   - {font}")
        
        if debug_info['colors']:
            print("\n🎨 Colors found:")
            for color in sorted(debug_info['colors']):
                print(f"   - {color}")
        
        if debug_info['potential_strikethroughs']:
            print(f"\n🔍 Potential strikethroughs found: {len(debug_info['potential_strikethroughs'])}")
            for item in debug_info['potential_strikethroughs']:
                print(f"   - Page {item['page']}: '{item['text']}' (font: {item['font']}, color: {item['color']})")
        else:
            print("\n🔍 No obvious strikethrough indicators found")
    
    print("\n📄 Testing strikethrough text extraction...")
    result = extract_text_with_strikethroughs(pdf_url)
    
    if result:
        print(f"✅ Extraction successful")
        print(f"📊 Has strikethroughs: {result.get('has_strikethroughs', False)}")
        print(f"📊 Strikethrough count: {result.get('strikethrough_count', 0)}")
        
        # Show a preview of the extracted text
        raw_text = result.get('raw_text', '')
        if raw_text:
            print(f"\n📝 Text preview (first 500 characters):")
            print("-" * 40)
            print(raw_text[:500] + "..." if len(raw_text) > 500 else raw_text)
            print("-" * 40)
    else:
        print("❌ Extraction failed")


if __name__ == "__main__":
    main()

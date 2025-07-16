#!/usr/bin/env python3
"""
Script to identify all missing or null "Buyer Ticker" values in each commodity file.
"""

import json
import os
from pathlib import Path
from collections import defaultdict

def find_missing_buyer_tickers():
    """Find all projects with missing or null Buyer Ticker values."""
    
    script_dir = Path(__file__).resolve().parent
    structured_output_dir = script_dir.parent / "data" / "structured_output_sample"
    
    # Get all JSON files except backups and ALL.json
    json_files = []
    for file_path in structured_output_dir.glob("*.json"):
        filename = file_path.name
        
        # Skip backup files and ALL.json itself
        if ('backup' in filename.lower() or 
            filename == 'ALL.json'):
            continue
            
        json_files.append(file_path)
    
    print(f"Checking {len(json_files)} commodity files for missing Buyer Ticker values...")
    print("=" * 80)
    
    # Process each file
    for file_path in sorted(json_files):
        print(f"\n📁 FILE: {file_path.name}")
        print("-" * 50)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            missing_tickers = []
            
            # Check each project
            for entry in data:
                project_name = entry.get('Project Name', '')
                
                # Check if Buyer Ticker field is missing OR null
                if 'Buyer Ticker' not in entry:
                    # Field is completely missing
                    missing_tickers.append({
                        'project_name': project_name,
                        'status': 'MISSING_FIELD',
                        'article_link': entry.get('Article Link', 'N/A')
                    })
                elif entry['Buyer Ticker'] is None or entry['Buyer Ticker'] == "" or entry['Buyer Ticker'] == "null":
                    # Field exists but is null/empty
                    missing_tickers.append({
                        'project_name': project_name,
                        'status': 'NULL_VALUE',
                        'value': entry['Buyer Ticker'],
                        'article_link': entry.get('Article Link', 'N/A')
                    })
            
            # Report results
            if missing_tickers:
                print(f"❌ Found {len(missing_tickers)} projects with missing/null Buyer Ticker:")
                for i, item in enumerate(missing_tickers, 1):
                    if item['status'] == 'MISSING_FIELD':
                        print(f"   {i:2d}. {item['project_name']:<30} | Status: FIELD MISSING")
                    else:
                        print(f"   {i:2d}. {item['project_name']:<30} | Status: NULL ({item['value']})")
            else:
                print(f"✅ All projects have Buyer Ticker values")
                
        except Exception as e:
            print(f"❌ Error processing {file_path.name}: {e}")
    
    print("\n" + "=" * 80)
    print("Analysis complete!")

if __name__ == "__main__":
    find_missing_buyer_tickers()
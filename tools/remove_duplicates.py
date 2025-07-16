#!/usr/bin/env python3
"""
Script to remove duplicate entries from ALL.json based on Project Name.
Keeps the first occurrence of each project name.
"""

import json
import sys
from collections import OrderedDict

def remove_duplicates(input_file, output_file):
    """Remove duplicate entries based on Project Name, keeping the first occurrence."""
    
    print(f"Reading data from {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Original entries: {len(data)}")
    
    # Use OrderedDict to maintain insertion order and remove duplicates
    seen_projects = OrderedDict()
    duplicates_removed = 0
    
    for entry in data:
        project_name = entry.get('Project Name', '')
        
        if project_name not in seen_projects:
            seen_projects[project_name] = entry
        else:
            duplicates_removed += 1
    
    # Convert back to list
    unique_data = list(seen_projects.values())
    
    print(f"Unique entries: {len(unique_data)}")
    print(f"Duplicates removed: {duplicates_removed}")
    
    # Write the deduplicated data
    print(f"Writing deduplicated data to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(unique_data, f, indent=2, ensure_ascii=False)
    
    print("Deduplication completed successfully!")
    return len(data), len(unique_data), duplicates_removed

if __name__ == "__main__":
    input_file = "/home/mois/mining-articles-extract/excel-converter/canada_sheets/ALL.json"
    output_file = "/home/mois/mining-articles-extract/excel-converter/canada_sheets/ALL_deduplicated.json"
    
    try:
        original_count, unique_count, removed_count = remove_duplicates(input_file, output_file)
        print(f"\nSummary:")
        print(f"  Original entries: {original_count}")
        print(f"  Unique entries: {unique_count}")
        print(f"  Duplicates removed: {removed_count}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
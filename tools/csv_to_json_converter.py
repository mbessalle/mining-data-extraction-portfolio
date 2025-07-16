#!/usr/bin/env python3
"""
Script to convert Cu_manual_cross_reference.csv to JSON format
"""

import csv
import json
import sys
from pathlib import Path

def convert_csv_to_json(csv_file_path, json_file_path):
    """
    Convert CSV file to JSON format
    
    Args:
        csv_file_path (str): Path to the input CSV file
        json_file_path (str): Path to the output JSON file
    """
    data = []
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            # Use csv.reader to properly handle multiline cells
            reader = csv.reader(csvfile)
            
            # Read header row
            headers = next(reader)
            # Clean up headers by removing line numbers and arrows
            clean_headers = []
            for header in headers:
                # Remove line number prefixes like "1→"
                clean_header = header.split('→', 1)[-1] if '→' in header else header
                clean_headers.append(clean_header.strip())
            
            # Read data rows
            for row in reader:
                # Skip empty rows
                if not any(row):
                    continue
                    
                # Create dictionary for this row
                row_dict = {}
                for i, value in enumerate(row):
                    if i < len(clean_headers):
                        # Clean up values by removing line number prefixes
                        clean_value = value.split('→', 1)[-1] if '→' in value else value
                        row_dict[clean_headers[i]] = clean_value.strip()
                
                data.append(row_dict)
        
        # Write to JSON file
        with open(json_file_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(data, jsonfile, indent=2, ensure_ascii=False)
        
        print(f"Successfully converted {csv_file_path} to {json_file_path}")
        print(f"Converted {len(data)} records")
        
    except FileNotFoundError:
        print(f"Error: File {csv_file_path} not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error converting file: {e}")
        sys.exit(1)

def main():
    # Define file paths
    csv_file = "excel-converter/canada_sheets/Cu_manual_cross_reference.csv"
    json_file = "excel-converter/canada_sheets/Cu_manual_cross_reference.json"
    
    # Check if CSV file exists
    if not Path(csv_file).exists():
        print(f"Error: CSV file {csv_file} not found")
        sys.exit(1)
    
    # Convert CSV to JSON
    convert_csv_to_json(csv_file, json_file)

if __name__ == "__main__":
    main()
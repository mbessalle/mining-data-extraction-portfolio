#!/usr/bin/env python3
"""
Script to convert JSON files to CSV format
Converts all stage-split JSON files to CSV
"""

import json
import csv
import os
import glob

def json_to_csv(json_file_path, csv_file_path):
    """Convert a single JSON file to CSV format"""
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not data:
            print(f"Warning: {json_file_path} is empty")
            return
        
        # Define the desired field order
        desired_order = [
            "Operator Company", "Buyer Ticker", "Project Name", "Commodities", 
            "Resource Value", "Stage", "Project State Or Province", "Project Ownership", 
            "Project Country", "Longitude", "Latitude", "Mineral District", 
            " $/ha ", "Project Area Ha", "Owner Marketcap", "Operator Marketcap", 
            "Owner Website", "Operator Website", "Title", "News Tags", "Article Link", 
            "Contact/CEO", "Interest Acquired %", "Currency", " Aggregate Deal ", 
            " Currency ", " Cash Payments ", " Currency _1", " Exp Comit ", 
            " share value ", " Shares ", " Currency _2", " Share Price", "NSR%", 
            "Date", "Month", "Day", "Year"
        ]
        
        # Get all unique field names across all records
        all_fields = set()
        for record in data:
            all_fields.update(record.keys())
        
        # Create final fieldnames list: desired order first, then any remaining fields
        fieldnames = []
        for field in desired_order:
            if field in all_fields:
                fieldnames.append(field)
                all_fields.remove(field)
        
        # Add any remaining fields that weren't in the desired order
        fieldnames.extend(sorted(list(all_fields)))
        
        # Write CSV file
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        
        print(f"Converted {json_file_path} -> {csv_file_path} ({len(data)} records)")
        
    except Exception as e:
        print(f"Error converting {json_file_path}: {e}")

def convert_all_stage_files():
    """Convert all stage-split JSON files to CSV"""
    
    input_dir = "/home/mois/mining-articles-extract/excel-converter/canada_sheets"
    
    # Find all stage-split JSON files
    json_files = glob.glob(os.path.join(input_dir, "*_earlystage.json"))
    json_files.extend(glob.glob(os.path.join(input_dir, "*_advancedexploration.json")))
    
    print(f"Found {len(json_files)} stage-split JSON files to convert")
    
    for json_file in json_files:
        # Create CSV filename by replacing .json with .csv
        csv_file = json_file.replace('.json', '.csv')
        json_to_csv(json_file, csv_file)
    
    print("CSV conversion complete!")

if __name__ == "__main__":
    print("Converting JSON files to CSV format...")
    convert_all_stage_files()
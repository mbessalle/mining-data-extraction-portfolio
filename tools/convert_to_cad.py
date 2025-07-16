#!/usr/bin/env python3
"""
Script to convert all financial values to CAD
Converts USD and AUD values to CAD using exchange rates
"""

import json
import os
import glob

# Exchange rates (as of recent data - you may want to update these)
EXCHANGE_RATES = {
    'CAD': 1.0,        # Base currency
    'USD': 1.43,       # 1 USD = 1.43 CAD (approximate)
    'AUD': 0.92,       # 1 AUD = 0.92 CAD (approximate)
}

# Financial fields that need currency conversion
FINANCIAL_FIELDS = [
    " $/ha ",
    " Aggregate Deal ",
    " Cash Payments ",
    " Share Price ",
    " share value ",
    " Exp Comit ",
    "Owner Marketcap",
    "Operator Marketcap"
]

def convert_to_cad(amount, currency):
    """Convert an amount from given currency to CAD"""
    if amount is None or amount == "":
        return amount
    
    try:
        # Convert to float if it's a string
        if isinstance(amount, str):
            amount = float(amount)
        
        # Get exchange rate
        rate = EXCHANGE_RATES.get(currency, 1.0)
        
        # Convert to CAD
        cad_amount = amount * rate
        
        # Return as float for JSON compatibility
        return round(cad_amount, 2)
        
    except (ValueError, TypeError):
        # If conversion fails, return original value
        return amount

def convert_record_to_cad(record):
    """Convert all financial fields in a record to CAD"""
    # Get the main currency for this record
    main_currency = record.get("Currency", "CAD")
    
    # Convert each financial field
    for field in FINANCIAL_FIELDS:
        if field in record and record[field] is not None:
            # Determine which currency field to use for this financial field
            if field == " Aggregate Deal ":
                currency = record.get(" Currency ", main_currency)
            elif field == " Cash Payments ":
                currency = record.get(" Currency _1", main_currency)
            elif field in [" Share Price ", " share value "]:
                currency = record.get(" Currency _2", main_currency)
            else:
                currency = main_currency
            
            # Convert the value
            original_value = record[field]
            converted_value = convert_to_cad(original_value, currency)
            record[field] = converted_value
            
            # Log significant conversions
            if currency != "CAD" and original_value != converted_value:
                print(f"  {field}: {original_value} {currency} -> {converted_value} CAD")
    
    # Update all currency fields to CAD
    currency_fields = ["Currency", " Currency ", " Currency _1", " Currency _2"]
    for curr_field in currency_fields:
        if curr_field in record:
            record[curr_field] = "CAD"
    
    return record

def convert_json_file_to_cad(json_file_path):
    """Convert all financial values in a JSON file to CAD"""
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not data:
            print(f"Warning: {json_file_path} is empty")
            return
        
        print(f"Converting {os.path.basename(json_file_path)} ({len(data)} records)")
        
        converted_count = 0
        for record in data:
            original_currency = record.get("Currency", "CAD")
            if original_currency != "CAD":
                print(f"  Converting record: {record.get('Project Name', 'Unknown')} ({original_currency} -> CAD)")
                convert_record_to_cad(record)
                converted_count += 1
            else:
                # Still need to update currency fields for consistency
                convert_record_to_cad(record)
        
        # Write back the converted data
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"  Converted {converted_count} records with non-CAD currencies")
        
    except Exception as e:
        print(f"Error converting {json_file_path}: {e}")

def convert_all_files_to_cad():
    """Convert all stage-split JSON files to CAD"""
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(script_dir, "..", "data", "structured_output_sample")
    
    # Find all stage-split JSON files
    json_files = glob.glob(os.path.join(input_dir, "*_earlystage.json"))
    json_files.extend(glob.glob(os.path.join(input_dir, "*_advancedexploration.json")))
    
    print(f"Found {len(json_files)} JSON files to convert to CAD")
    print(f"Using exchange rates: USD={EXCHANGE_RATES['USD']}, AUD={EXCHANGE_RATES['AUD']}")
    print()
    
    for json_file in sorted(json_files):
        convert_json_file_to_cad(json_file)
        print()
    
    print("CAD conversion complete!")

if __name__ == "__main__":
    print("Converting all financial values to CAD...")
    convert_all_files_to_cad()
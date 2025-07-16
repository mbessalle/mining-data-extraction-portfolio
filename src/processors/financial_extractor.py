"""
Advanced Financial Data Extraction System for Mining Industry

This module demonstrates AI-powered extraction of structured financial data
from unstructured mining industry news articles and reports using comprehensive
extraction rules and validation logic.
"""

import json
import time
import re
import os
from typing import Dict, List, Optional, Any
from pathlib import Path
from openai import OpenAI

class FinancialExtractor:
    """
    AI-powered financial data extractor for mining industry articles.
    
    Uses Google Gemini API with comprehensive extraction rules to extract 
    structured financial information from unstructured text sources with 
    high accuracy and validation.
    """
    
    def __init__(self, api_key: str = None, rate_limit: float = 1.0):
        """
        Initialize the financial extractor.
        
        Args:
            api_key: Google Gemini API key
            rate_limit: Delay between API calls (seconds)
        """
        self.client = OpenAI(
            api_key=api_key or os.getenv('GEMINI_API_KEY'),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        self.rate_limit = rate_limit
        self.model = "gemini-2.5-pro"
        
        # Load comprehensive extraction rules
        self.system_prompt = self._load_extraction_rules()
        
    def _load_extraction_rules(self) -> str:
        """Load and combine comprehensive extraction rules into system prompt."""
        
        # Get the path to the extraction rules
        current_dir = Path(__file__).parent
        rules_dir = current_dir.parent.parent / "docs" / "extraction-rules"
        
        rule_files = [
            rules_dir / "extraction-rules-core-logic.md",
            rules_dir / "extraction-rules-edge-cases.md",
        ]
        
        # Load and combine rules
        combined_rules = ""
        for rule_file in rule_files:
            if rule_file.exists():
                with open(rule_file, 'r', encoding='utf-8') as f:
                    combined_rules += f.read() + "\n---\n"
            else:
                print(f"Warning: Rule file not found: {rule_file}")
        
        if not combined_rules:
            # Fallback to basic rules if files not found
            return self._get_basic_extraction_prompt()
        
        # Build comprehensive system prompt
        system_prompt = f"""
You are a meticulous data synthesis engine specializing in mining and M&A announcements.
Your task is to analyze a collection of documents related to a single project and synthesize the information into ONE SINGLE, CONSOLIDATED JSON object.

You MUST adhere to the following rules, which are composed of core logic and edge cases.
Failure to follow these rules, especially the justification requirements, will result in an incorrect output.

--- START OF COMPREHENSIVE EXTRACTION RULES ---
{combined_rules}
--- END OF COMPREHENSIVE EXTRACTION RULES ---

Your output MUST be a single, valid JSON object that strictly conforms to the schema defined in the rules.
Do not include any explanatory text, markdown formatting, or anything else outside of the JSON object itself.
For every field, you must provide both a `value` and a `justification` as specified in the rules.

CRITICAL REQUIREMENTS:
1. Follow the value/justification structure for ALL fields
2. Apply DATA RELEVANCE rules - only extract data for the specified project
3. Handle SHARED COMMITMENTS by dividing values appropriately
4. Use the entity resolution protocol to identify BUYER vs SELLER
5. Follow the financial data extraction hierarchy strictly
6. Provide detailed justifications with direct quotes from the text
"""
        return system_prompt
    
    def _get_basic_extraction_prompt(self) -> str:
        """Fallback basic extraction prompt if rule files are not available."""
        return """
You are a financial data extraction expert for the mining industry.
Extract structured financial data from mining M&A announcements.

Return data in this format with value/justification pairs:
{
  "project_name": {"value": "string|null", "justification": "string|null"},
  "company_name": {"value": "string|null", "justification": "string|null"},
  "currency": {"value": "string|null", "justification": "string|null"},
  "cash_payments_raw": {"value": "number|null", "justification": "string|null"},
  "amount_of_shares_issued": {"value": "number|null", "justification": "string|null"},
  "issued_share_price": {"value": "number|null", "justification": "string|null"},
  "exploration_commitment_value_raw": {"value": "number|null", "justification": "string|null"},
  "buyer_ticker_and_exchange": {"value": "string|null", "justification": "string|null"},
  "interest_acquired_percent": {"value": "number|null", "justification": "string|null"},
  "nsr_acquired_percent": {"value": "number|null", "justification": "string|null"}
}

Rules:
- Extract only data for the specified project
- Use direct quotes in justifications
- Return null for missing values
- Remove formatting from numbers
- Use three-letter currency codes (USD, CAD, AUD)
"""
    
    def extract_financial_data(self, text_content: str, project_name: str, 
                             authoritative_metadata: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Extract structured financial data from unstructured text using comprehensive rules.
        
        Args:
            text_content: Raw article or document text
            project_name: Name of the mining project
            authoritative_metadata: Additional metadata to guide extraction
            
        Returns:
            Dictionary containing structured financial data with value/justification pairs
        """
        
        # Pre-validation: Check if content contains financial indicators
        if not self._has_financial_content(text_content):
            return {"error": "No financial data detected in content"}
        
        # Build authoritative metadata block
        auth_lines = []
        if authoritative_metadata:
            for key, value in authoritative_metadata.items():
                if value and value != 'N/A':
                    display_key = "ticker and exchange" if key in ['exchange', 'root_ticker'] else key.replace('_', ' ')
                    auth_lines.append(f"The authoritative {display_key} for this project is **{value}**.")
        
        auth_block = "\n".join(auth_lines) if auth_lines else "No additional authoritative metadata provided."
        
        # Build user prompt with comprehensive context
        user_prompt = f"""
The primary project of interest for this analysis is: **{project_name.upper()}**

You have been provided with the following authoritative metadata:
{auth_block}

You will now be given text content for analysis. Your task is to analyze ALL of this text to produce ONE SINGLE, CONSOLIDATED JSON output that best represents the financial details for the **{project_name.upper()}** project ONLY.

REMEMBER: Follow all extraction rules, especially:
1. DATA RELEVANCE - Only extract data for {project_name.upper()}
2. SHARED COMMITMENTS - Divide shared values appropriately
3. ENTITY RESOLUTION - Identify buyer vs seller correctly
4. VALUE/JUSTIFICATION - Provide both for every field

--- TEXT CONTENT START ---
{text_content}
--- TEXT CONTENT END ---
"""
        
        try:
            # Apply rate limiting
            time.sleep(self.rate_limit)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            result = self._parse_response(response.choices[0].message.content)
            return self._validate_financial_data(result)
            
        except Exception as e:
            return {"error": f"API extraction failed: {str(e)}"}
    
    def _has_financial_content(self, text: str) -> bool:
        """Check if text contains financial indicators worth processing."""
        financial_indicators = [
            r'\$[\d,]+', r'CAD', r'USD', r'AUD', r'million', r'billion',
            r'shares?', r'cash', r'payment', r'acquisition', r'deal',
            r'exploration', r'commitment', r'NSR', r'royalty', r'interest',
            r'ticker', r'exchange', r'ASX', r'TSX', r'NYSE'
        ]
        
        for indicator in financial_indicators:
            if re.search(indicator, text, re.IGNORECASE):
                return True
        return False
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse AI response and extract JSON data."""
        try:
            # Extract JSON from response (handle potential markdown formatting)
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {"error": "No valid JSON found in response"}
        except json.JSONDecodeError as e:
            return {"error": f"JSON parsing failed: {str(e)}"}
    
    def _validate_financial_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate extracted financial data for consistency and accuracy.
        
        Implements business rules and mathematical validation based on
        the comprehensive extraction rules.
        """
        if "error" in data:
            return data
            
        validated = data.copy()
        validation_errors = []
        
        # Check for value/justification structure
        for field_name, field_data in data.items():
            if isinstance(field_data, dict):
                if 'value' not in field_data or 'justification' not in field_data:
                    validation_errors.append(f"Field {field_name} missing value/justification structure")
        
        # Validate financial calculations if values are present
        try:
            # Extract values from the value/justification structure
            def get_value(field_name):
                field_data = data.get(field_name, {})
                if isinstance(field_data, dict):
                    return field_data.get('value')
                return field_data
            
            cash_payments = get_value('cash_payments_raw')
            shares_issued = get_value('amount_of_shares_issued')
            share_price = get_value('issued_share_price')
            exploration_commitment = get_value('exploration_commitment_value_raw')
            
            # Validate share calculations
            if (self._is_numeric(shares_issued) and 
                self._is_numeric(share_price)):
                
                expected_share_value = shares_issued * share_price
                # Check if share_value field exists and validate
                share_value = get_value('share_value')
                if self._is_numeric(share_value):
                    if abs(expected_share_value - share_value) > 1000:
                        validation_errors.append(f"Share value calculation inconsistent: {share_value} vs expected {expected_share_value}")
            
            # Check for required justifications
            for field_name, field_data in data.items():
                if isinstance(field_data, dict):
                    value = field_data.get('value')
                    justification = field_data.get('justification')
                    
                    # If value is not null, justification should exist
                    if value is not None and not justification:
                        validation_errors.append(f"Field {field_name} has value but no justification")
        
        except Exception as e:
            validation_errors.append(f"Validation error: {str(e)}")
        
        # Add validation summary
        validated['validation'] = {
            'is_valid': len(validation_errors) == 0,
            'errors': validation_errors,
            'completeness_score': self._calculate_completeness(data),
            'extraction_method': 'comprehensive_rules'
        }
        
        return validated
    
    def _is_numeric(self, value: Any) -> bool:
        """Check if value is numeric (int or float)."""
        return isinstance(value, (int, float)) and value is not None
    
    def _calculate_completeness(self, data: Dict[str, Any]) -> float:
        """Calculate data completeness percentage."""
        
        # Key fields for completeness calculation
        key_fields = [
            'project_name', 'company_name', 'currency', 'cash_payments_raw',
            'amount_of_shares_issued', 'issued_share_price', 'exploration_commitment_value_raw',
            'buyer_ticker_and_exchange', 'interest_acquired_percent'
        ]
        
        completed_fields = 0
        total_fields = len(key_fields)
        
        for field in key_fields:
            field_data = data.get(field, {})
            if isinstance(field_data, dict):
                value = field_data.get('value')
                if value is not None:
                    completed_fields += 1
            elif field_data is not None:
                completed_fields += 1
        
        return (completed_fields / total_fields) * 100


class DataValidator:
    """
    Comprehensive data validation for mining industry datasets.
    
    Implements business rules, mathematical consistency checks,
    and data quality scoring based on extraction rules.
    """
    
    @staticmethod
    def validate_project_data(project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate complete project dataset against extraction rules.
        
        Args:
            project_data: Complete project financial data
            
        Returns:
            Validation results with scores and recommendations
        """
        results = {
            'is_valid': True,
            'score': 0,
            'errors': [],
            'warnings': [],
            'recommendations': []
        }
        
        # Check for value/justification structure
        for field_name, field_data in project_data.items():
            if isinstance(field_data, dict) and 'value' in field_data:
                value = field_data.get('value')
                justification = field_data.get('justification')
                
                # Check if non-null values have justifications
                if value is not None and not justification:
                    results['warnings'].append(f"Field {field_name} has value but no justification")
        
        # Check required fields based on extraction rules
        required_fields = ['project_name', 'company_name', 'currency']
        for field in required_fields:
            field_data = project_data.get(field, {})
            if isinstance(field_data, dict):
                value = field_data.get('value')
            else:
                value = field_data
                
            if not value:
                results['errors'].append(f"Missing required field: {field}")
                results['is_valid'] = False
        
        # Validate ticker format if present
        ticker_field = project_data.get('buyer_ticker_and_exchange', {})
        if isinstance(ticker_field, dict):
            ticker = ticker_field.get('value')
        else:
            ticker = ticker_field
            
        if ticker and not re.match(r'^[A-Z-]+:[A-Z]+$', ticker):
            results['warnings'].append(f"Invalid ticker format: {ticker}")
        
        # Calculate quality score
        results['score'] = DataValidator._calculate_quality_score(project_data)
        
        # Add recommendations
        if results['score'] < 50:
            results['recommendations'].append("Consider manual review due to low completeness score")
        
        if not results['errors'] and not results['warnings']:
            results['recommendations'].append("Data quality is good")
        
        return results
    
    @staticmethod
    def _calculate_quality_score(data: Dict[str, Any]) -> float:
        """Calculate overall data quality score (0-100) based on extraction rules."""
        
        weights = {
            'project_identification': 0.25,  # project_name, company_name
            'financial_data': 0.40,          # cash, shares, commitments
            'market_data': 0.20,             # ticker, currency, interest
            'data_quality': 0.15             # justifications, validation
        }
        
        scores = {}
        
        # Project identification score
        project_fields = ['project_name', 'company_name']
        project_score = 0
        for field in project_fields:
            field_data = data.get(field, {})
            if isinstance(field_data, dict):
                value = field_data.get('value')
            else:
                value = field_data
            if value:
                project_score += 50
        scores['project_identification'] = project_score
        
        # Financial data score
        financial_fields = ['cash_payments_raw', 'amount_of_shares_issued', 'issued_share_price', 'exploration_commitment_value_raw']
        financial_score = 0
        for field in financial_fields:
            field_data = data.get(field, {})
            if isinstance(field_data, dict):
                value = field_data.get('value')
            else:
                value = field_data
            if value is not None:
                financial_score += 25
        scores['financial_data'] = financial_score
        
        # Market data score
        market_fields = ['buyer_ticker_and_exchange', 'currency', 'interest_acquired_percent']
        market_score = 0
        for field in market_fields:
            field_data = data.get(field, {})
            if isinstance(field_data, dict):
                value = field_data.get('value')
            else:
                value = field_data
            if value is not None:
                market_score += 33.33
        scores['market_data'] = market_score
        
        # Data quality score (based on justifications)
        total_fields = len(data)
        justified_fields = 0
        for field_name, field_data in data.items():
            if isinstance(field_data, dict):
                value = field_data.get('value')
                justification = field_data.get('justification')
                if value is not None and justification:
                    justified_fields += 1
        
        scores['data_quality'] = (justified_fields / total_fields * 100) if total_fields > 0 else 0
        
        # Calculate weighted average
        total_score = sum(scores[category] * weights[category] 
                         for category in weights.keys())
        
        return round(total_score, 2)


# Usage Example and Testing
if __name__ == "__main__":
    # Example usage demonstration
    sample_article = """
    XYZ Mining Corp. (TSX: XYZ) announced today the acquisition of the Golden Eagle 
    project for a total consideration of $25 million. The deal comprises $10 million 
    in cash payments and 15 million shares valued at $1.00 per share. The company 
    will also commit to $5 million in exploration expenditures over the next two years.
    
    The Golden Eagle project covers 1,200 hectares in the Yukon Territory and contains
    an estimated 2.5 million ounces of gold equivalent resources.
    """
    
    # Initialize extractor with comprehensive rules
    extractor = FinancialExtractor()
    
    # Extract financial data
    result = extractor.extract_financial_data(
        sample_article, 
        "Golden Eagle",
        authoritative_metadata={
            'project_name': 'Golden Eagle',
            'company_name': 'XYZ Mining Corp',
            'exchange': 'TSX',
            'ticker': 'XYZ'
        }
    )
    
    print("Extraction Result:")
    print(json.dumps(result, indent=2))
    
    # Validate the results
    validator = DataValidator()
    validation_result = validator.validate_project_data(result)
    
    print("\nValidation Result:")
    print(json.dumps(validation_result, indent=2))
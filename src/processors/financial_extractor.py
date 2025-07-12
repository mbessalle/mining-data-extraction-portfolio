"""
Advanced Financial Data Extraction System for Mining Industry

This module demonstrates AI-powered extraction of structured financial data
from unstructured mining industry news articles and reports.
"""

import json
import time
import re
from typing import Dict, List, Optional, Any
from openai import OpenAI

class FinancialExtractor:
    """
    AI-powered financial data extractor for mining industry articles.
    
    Uses Google Gemini API to extract structured financial information
    from unstructured text sources with high accuracy and validation.
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
        
    def extract_financial_data(self, text_content: str, project_name: str) -> Dict[str, Any]:
        """
        Extract structured financial data from unstructured text.
        
        Args:
            text_content: Raw article or document text
            project_name: Name of the mining project
            
        Returns:
            Dictionary containing structured financial data
        """
        
        # Pre-validation: Check if content contains financial indicators
        if not self._has_financial_content(text_content):
            return {"error": "No financial data detected in content"}
            
        prompt = self._build_extraction_prompt(text_content, project_name)
        
        try:
            # Apply rate limiting
            time.sleep(self.rate_limit)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a financial data extraction expert for the mining industry."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            result = self._parse_response(response.choices[0].message.content)
            return self._validate_financial_data(result)
            
        except Exception as e:
            return {"error": f"API extraction failed: {str(e)}"}
    
    def _has_financial_content(self, text: str) -> bool:
        """Check if text contains financial indicators worth processing."""
        financial_indicators = [
            r'\$[\d,]+', r'CAD', r'USD', r'million', r'billion',
            r'shares?', r'cash', r'payment', r'acquisition', r'deal'
        ]
        
        for indicator in financial_indicators:
            if re.search(indicator, text, re.IGNORECASE):
                return True
        return False
    
    def _build_extraction_prompt(self, text: str, project_name: str) -> str:
        """Build optimized prompt for financial data extraction."""
        return f"""
Extract financial data from this mining industry article about {project_name}.

TEXT:
{text}

INSTRUCTIONS:
1. Extract ALL financial information with precise amounts
2. Convert currencies to consistent format (CAD/USD)
3. Calculate aggregate deal values
4. Identify buyer ticker symbols
5. Return ONLY valid JSON, no explanations

REQUIRED JSON FORMAT:
{{
  "buyer_ticker": "exchange:symbol or null",
  "aggregate_deal": numeric_value_or_null,
  "cash_payments": numeric_value_or_null,
  "shares": numeric_count_or_null,
  "share_price": numeric_value_or_null,
  "share_value": numeric_value_or_null,
  "exploration_commitment": numeric_value_or_null,
  "currency": "CAD/USD",
  "interest_acquired_percent": numeric_value_or_null,
  "nsr_percent": numeric_value_or_null
}}

VALIDATION RULES:
- aggregate_deal should equal sum of cash_payments + share_value + exploration_commitment
- share_value should equal shares * share_price
- All amounts in base currency units (not millions)
- Return null for missing/unclear values
"""

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
        
        Implements business rules and mathematical validation.
        """
        if "error" in data:
            return data
            
        validated = data.copy()
        validation_errors = []
        
        # Validate aggregate deal calculation
        if self._is_numeric(data.get('aggregate_deal')):
            components = [
                data.get('cash_payments', 0) or 0,
                data.get('share_value', 0) or 0,
                data.get('exploration_commitment', 0) or 0
            ]
            expected_total = sum(components)
            actual_total = data['aggregate_deal']
            
            if abs(expected_total - actual_total) > 1000:  # Allow small rounding differences
                validation_errors.append(f"Aggregate deal mismatch: {actual_total} vs {expected_total}")
        
        # Validate share calculations
        if (self._is_numeric(data.get('shares')) and 
            self._is_numeric(data.get('share_price')) and 
            self._is_numeric(data.get('share_value'))):
            
            expected_value = data['shares'] * data['share_price']
            actual_value = data['share_value']
            
            if abs(expected_value - actual_value) > 1000:
                validation_errors.append(f"Share value mismatch: {actual_value} vs {expected_value}")
        
        # Add validation summary
        validated['validation'] = {
            'is_valid': len(validation_errors) == 0,
            'errors': validation_errors,
            'completeness_score': self._calculate_completeness(data)
        }
        
        return validated
    
    def _is_numeric(self, value: Any) -> bool:
        """Check if value is numeric (int or float)."""
        return isinstance(value, (int, float)) and value is not None
    
    def _calculate_completeness(self, data: Dict[str, Any]) -> float:
        """Calculate data completeness percentage."""
        required_fields = [
            'buyer_ticker', 'aggregate_deal', 'cash_payments', 
            'shares', 'share_price', 'currency'
        ]
        
        completed_fields = sum(1 for field in required_fields 
                             if data.get(field) is not None)
        
        return (completed_fields / len(required_fields)) * 100


class DataValidator:
    """
    Comprehensive data validation for mining industry datasets.
    
    Implements business rules, mathematical consistency checks,
    and data quality scoring.
    """
    
    @staticmethod
    def validate_project_data(project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate complete project dataset.
        
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
        
        # Check required fields
        required_fields = ['Project Name', 'Buyer Ticker', 'Currency']
        missing_fields = [field for field in required_fields 
                         if not project_data.get(field)]
        
        if missing_fields:
            results['errors'].extend([f"Missing required field: {field}" 
                                    for field in missing_fields])
            results['is_valid'] = False
        
        # Validate ticker format
        ticker = project_data.get('Buyer Ticker')
        if ticker and not re.match(r'^[A-Z-]+:[A-Z]+$', ticker):
            results['warnings'].append(f"Invalid ticker format: {ticker}")
        
        # Calculate quality score
        results['score'] = DataValidator._calculate_quality_score(project_data)
        
        return results
    
    @staticmethod
    def _calculate_quality_score(data: Dict[str, Any]) -> float:
        """Calculate overall data quality score (0-100)."""
        weights = {
            'buyer_ticker': 0.2,
            'aggregate_deal': 0.2,
            'financial_breakdown': 0.3,
            'market_data': 0.2,
            'metadata': 0.1
        }
        
        scores = {}
        
        # Buyer ticker score
        scores['buyer_ticker'] = 100 if data.get('Buyer Ticker') else 0
        
        # Aggregate deal score
        scores['aggregate_deal'] = 100 if data.get(' Aggregate Deal ') else 0
        
        # Financial breakdown score
        financial_fields = [' Cash Payments ', ' Shares ', ' Share Price ']
        completed_financial = sum(1 for field in financial_fields 
                                if data.get(field) is not None)
        scores['financial_breakdown'] = (completed_financial / len(financial_fields)) * 100
        
        # Market data score
        market_fields = ['Owner Marketcap', 'Project Area Ha']
        completed_market = sum(1 for field in market_fields 
                             if data.get(field) is not None)
        scores['market_data'] = (completed_market / len(market_fields)) * 100
        
        # Metadata score
        metadata_fields = ['Date', 'Article Link', 'Contact/CEO']
        completed_metadata = sum(1 for field in metadata_fields 
                               if data.get(field) is not None)
        scores['metadata'] = (completed_metadata / len(metadata_fields)) * 100
        
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
    """
    
    extractor = FinancialExtractor()
    result = extractor.extract_financial_data(sample_article, "Golden Eagle")
    
    print("Extraction Result:")
    print(json.dumps(result, indent=2))
    
    # Validation example
    validator = DataValidator()
    validation_result = validator.validate_project_data(result)
    
    print("\nValidation Result:")
    print(json.dumps(validation_result, indent=2))
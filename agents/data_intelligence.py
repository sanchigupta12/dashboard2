import pandas as pd
import numpy as np
import json
from google import genai
from google.genai import types

class DataIntelligenceAgent:
    """Agent 1: Analyzes CSV data structure and identifies business domain"""
    
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        
    def analyze_data(self, df):
        """Comprehensive data analysis including domain detection"""
        
        # Basic statistics
        basic_stats = {
            'rows': len(df),
            'columns': len(df.columns),
            'memory_usage': df.memory_usage(deep=True).sum(),
            'missing_values': df.isnull().sum().sum()
        }
        
        # Column analysis
        column_analysis = self._analyze_columns(df)
        
        # Domain detection
        domain_info = self._detect_business_domain(df, column_analysis)
        
        # Data quality assessment
        quality_assessment = self._assess_data_quality(df)
        
        return {
            'basic_stats': basic_stats,
            'column_analysis': column_analysis,
            'domain': domain_info,
            'quality': quality_assessment,
            'sample_data': df.head(3).to_dict('records')
        }
    
    def _analyze_columns(self, df):
        """Analyze column types and characteristics"""
        analysis = {
            'numeric': [],
            'categorical': [],
            'datetime': [],
            'boolean': [],
            'text': []
        }
        
        for col in df.columns:
            dtype = df[col].dtype
            unique_count = df[col].nunique()
            total_count = len(df[col])
            
            if pd.api.types.is_numeric_dtype(dtype):
                analysis['numeric'].append(col)
            elif pd.api.types.is_datetime64_any_dtype(dtype):
                analysis['datetime'].append(col)
            elif pd.api.types.is_bool_dtype(dtype):
                analysis['boolean'].append(col)
            elif unique_count / total_count < 0.5 and unique_count < 50:
                analysis['categorical'].append(col)
            else:
                analysis['text'].append(col)
        
        return analysis
    
    def _detect_business_domain(self, df, column_analysis):
        """Use AI to detect business domain based on column names and data patterns"""
        
        # Prepare column information for AI analysis
        column_info = {
            'column_names': list(df.columns),
            'numeric_columns': column_analysis['numeric'],
            'categorical_columns': column_analysis['categorical'],
            'sample_values': {}
        }
        
        # Get sample values for key columns
        for col in df.columns[:10]:  # Limit to first 10 columns
            sample_values = df[col].dropna().head(3).tolist()
            column_info['sample_values'][col] = [str(val) for val in sample_values]
        
        prompt = f"""
        Analyze the following dataset structure and identify the most likely business domain:
        
        Column Names: {column_info['column_names']}
        Numeric Columns: {column_info['numeric_columns']}
        Categorical Columns: {column_info['categorical_columns']}
        Sample Values: {column_info['sample_values']}
        
        Based on this information, determine:
        1. The most likely business domain (e-commerce, SaaS, restaurant, retail, finance, healthcare, etc.)
        2. Confidence level (0.0 to 1.0)
        3. Key indicators that led to this classification
        4. Suggested business insights that could be valuable
        
        Respond in JSON format:
        {{
            "type": "domain_name",
            "confidence": 0.85,
            "indicators": ["indicator1", "indicator2", "indicator3"],
            "suggested_insights": ["insight1", "insight2", "insight3"]
        }}
        """
        
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-pro",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            
            if response.text:
                domain_data = json.loads(response.text)
                return domain_data
            else:
                return self._fallback_domain_detection(df)
                
        except Exception as e:
            print(f"AI domain detection failed: {e}")
            return self._fallback_domain_detection(df)
    
    def _fallback_domain_detection(self, df):
        """Fallback domain detection using rule-based approach"""
        columns_lower = [col.lower() for col in df.columns]
        
        # E-commerce indicators
        ecommerce_keywords = ['price', 'product', 'order', 'customer', 'sales', 'revenue', 'quantity', 'sku']
        ecommerce_score = sum(1 for keyword in ecommerce_keywords if any(keyword in col for col in columns_lower))
        
        # SaaS indicators
        saas_keywords = ['user', 'subscription', 'plan', 'trial', 'churn', 'mrr', 'arr', 'feature']
        saas_score = sum(1 for keyword in saas_keywords if any(keyword in col for col in columns_lower))
        
        # Restaurant indicators
        restaurant_keywords = ['menu', 'table', 'order', 'food', 'dish', 'rating', 'reservation']
        restaurant_score = sum(1 for keyword in restaurant_keywords if any(keyword in col for col in columns_lower))
        
        scores = {
            'e-commerce': ecommerce_score,
            'saas': saas_score,
            'restaurant': restaurant_score
        }
        
        best_domain = max(scores.keys(), key=lambda k: scores[k])
        confidence = min(scores[best_domain] / len(columns_lower), 1.0)
        
        return {
            'type': best_domain if confidence > 0.2 else 'general',
            'confidence': confidence,
            'indicators': [f"Found {scores[best_domain]} relevant column indicators"],
            'suggested_insights': ["Revenue analysis", "Customer behavior patterns", "Performance metrics"]
        }
    
    def _assess_data_quality(self, df):
        """Assess data quality metrics"""
        total_cells = df.size
        missing_cells = df.isnull().sum().sum()
        
        return {
            'completeness': 1 - (missing_cells / total_cells),
            'missing_values_by_column': df.isnull().sum().to_dict(),
            'duplicate_rows': df.duplicated().sum(),
            'data_types_consistent': True  # Simplified for now
        }

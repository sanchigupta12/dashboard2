import json
from google import genai
from google.genai import types

class VisualizationAgent:
    """Agent 2: Suggests domain-specific visualizations using AI"""
    
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
    
    def suggest_visualizations(self, df, analysis_results):
        """Generate 6-7 domain-specific visualization suggestions"""
        
        domain_info = analysis_results.get('domain', {})
        column_analysis = analysis_results.get('column_analysis', {})
        
        # Prepare data context for AI
        data_context = {
            'domain': domain_info.get('type', 'general'),
            'confidence': domain_info.get('confidence', 0.5),
            'columns': {
                'numeric': column_analysis.get('numeric', []),
                'categorical': column_analysis.get('categorical', []),
                'datetime': column_analysis.get('datetime', []),
                'all_columns': list(df.columns)
            },
            'data_shape': {
                'rows': len(df),
                'columns': len(df.columns)
            },
            'sample_data': df.head(2).to_dict('records')
        }
        
        prompt = f"""
        As a data visualization expert, suggest 6-7 specific chart recommendations for this {data_context['domain']} dataset.
        
        Dataset Context:
        - Business Domain: {data_context['domain']} (confidence: {data_context['confidence']:.2f})
        - Numeric Columns: {data_context['columns']['numeric']}
        - Categorical Columns: {data_context['columns']['categorical']}
        - DateTime Columns: {data_context['columns']['datetime']}
        - Data Shape: {data_context['data_shape']['rows']} rows × {data_context['data_shape']['columns']} columns
        - Sample Data: {data_context['sample_data']}
        
        For each visualization suggestion, provide:
        1. Chart title (specific to the data)
        2. Chart type (bar, line, scatter, pie, heatmap, histogram, box, etc.)
        3. X-axis column (actual column name from the data)
        4. Y-axis column (actual column name from the data) 
        5. Color/group by column (if applicable)
        6. Description of business insight this chart would reveal
        7. Why this chart is particularly valuable for the {data_context['domain']} domain
        
        Ensure suggestions use ONLY the actual column names from the dataset: {data_context['columns']['all_columns']}
        
        Respond in JSON format as an array of chart objects:
        [
          {{
            "title": "Specific Chart Title",
            "chart_type": "bar",
            "x_axis": "actual_column_name",
            "y_axis": "actual_column_name",
            "color_by": "actual_column_name or null",
            "description": "What business insight this reveals",
            "domain_value": "Why this is valuable for {data_context['domain']} businesses"
          }}
        ]
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
                suggestions = json.loads(response.text)
                # Validate suggestions against actual columns
                validated_suggestions = self._validate_suggestions(suggestions, df.columns)
                return validated_suggestions
            else:
                return self._fallback_suggestions(df, analysis_results)
                
        except Exception as e:
            print(f"AI visualization suggestions failed: {e}")
            return self._fallback_suggestions(df, analysis_results)
    
    def _validate_suggestions(self, suggestions, available_columns):
        """Validate that suggested columns exist in the dataset"""
        validated = []
        available_cols_lower = [col.lower() for col in available_columns]
        col_mapping = {col.lower(): col for col in available_columns}
        
        for suggestion in suggestions:
            # Check if suggested columns exist (case-insensitive)
            x_axis = suggestion.get('x_axis')
            y_axis = suggestion.get('y_axis')
            color_by = suggestion.get('color_by')
            
            # Fix column names if they exist but with different case
            if x_axis and x_axis.lower() in available_cols_lower:
                suggestion['x_axis'] = col_mapping[x_axis.lower()]
            
            if y_axis and y_axis.lower() in available_cols_lower:
                suggestion['y_axis'] = col_mapping[y_axis.lower()]
                
            if color_by and color_by.lower() in available_cols_lower:
                suggestion['color_by'] = col_mapping[color_by.lower()]
            elif color_by and color_by.lower() not in available_cols_lower:
                suggestion['color_by'] = None
            
            # Only include suggestions with valid columns
            if (suggestion.get('x_axis') in available_columns or 
                suggestion.get('y_axis') in available_columns):
                validated.append(suggestion)
        
        return validated
    
    def _fallback_suggestions(self, df, analysis_results):
        """Generate basic suggestions when AI fails"""
        suggestions = []
        numeric_cols = analysis_results.get('column_analysis', {}).get('numeric', [])
        categorical_cols = analysis_results.get('column_analysis', {}).get('categorical', [])
        
        # Basic numeric distribution
        if numeric_cols:
            suggestions.append({
                'title': f'Distribution of {numeric_cols[0]}',
                'chart_type': 'histogram',
                'x_axis': numeric_cols[0],
                'y_axis': None,
                'color_by': None,
                'description': f'Shows the distribution pattern of {numeric_cols[0]} values',
                'domain_value': 'Understanding data distribution is crucial for business analysis'
            })
        
        # Categorical breakdown
        if categorical_cols:
            suggestions.append({
                'title': f'{categorical_cols[0]} Breakdown',
                'chart_type': 'pie',
                'x_axis': categorical_cols[0],
                'y_axis': None,
                'color_by': None,
                'description': f'Shows the composition of different {categorical_cols[0]} categories',
                'domain_value': 'Category analysis helps identify key segments'
            })
        
        # Correlation if multiple numeric columns
        if len(numeric_cols) >= 2:
            suggestions.append({
                'title': f'{numeric_cols[0]} vs {numeric_cols[1]}',
                'chart_type': 'scatter',
                'x_axis': numeric_cols[0],
                'y_axis': numeric_cols[1],
                'color_by': categorical_cols[0] if categorical_cols else None,
                'description': f'Explores relationship between {numeric_cols[0]} and {numeric_cols[1]}',
                'domain_value': 'Correlation analysis reveals important business relationships'
            })
        
        return suggestions

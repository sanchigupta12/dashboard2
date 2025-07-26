import json
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from google import genai
from google.genai import types
from utils.chart_generator import ChartGenerator

class ExecutorAgent:
    """Executor Agent: Handles chat functionality and dashboard generation"""
    
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        self.chart_generator = ChartGenerator()
    
    def chat_with_data(self, question, df, analysis_results):
        """Handle data-related questions using Gemini"""
        
        # Prepare context about the data
        domain_info = analysis_results.get('domain', {})
        column_analysis = analysis_results.get('column_analysis', {})
        
        data_context = f"""
        Dataset Context:
        - Business Domain: {domain_info.get('type', 'general')} (confidence: {domain_info.get('confidence', 0.5):.2f})
        - Shape: {len(df)} rows × {len(df.columns)} columns
        - Columns: {list(df.columns)}
        - Numeric Columns: {column_analysis.get('numeric', [])}
        - Categorical Columns: {column_analysis.get('categorical', [])}
        - Sample Data (first 3 rows): {df.head(3).to_dict('records')}
        - Basic Statistics: {df.describe().to_dict() if len(column_analysis.get('numeric', [])) > 0 else 'No numeric columns for statistics'}
        """
        
        prompt = f"""
        You are a business data analyst expert. Answer the user's question about their {domain_info.get('type', 'business')} data.
        
        {data_context}
        
        User Question: {question}
        
        Provide a comprehensive, business-focused answer that:
        1. Directly addresses the user's question
        2. Provides specific insights based on the actual data
        3. Includes relevant numbers, trends, or patterns when applicable
        4. Offers actionable business recommendations when appropriate
        5. Uses domain-specific terminology for {domain_info.get('type', 'business')} businesses
        
        Be conversational but professional, and focus on practical business value.
        """
        
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-pro",
                contents=prompt
            )
            
            if response.text:
                return response.text
            else:
                return "I apologize, but I couldn't generate a response to your question. Please try rephrasing or asking a different question about your data."
                
        except Exception as e:
            return f"I encountered an error while analyzing your data: {str(e)}. Please try asking your question in a different way."
    
    def generate_dashboard(self, df, selected_charts):
        """Generate interactive dashboard with selected charts"""
        charts = []
        
        for chart_config in selected_charts:
            try:
                figure = self.chart_generator.create_chart(df, chart_config)
                if figure:
                    charts.append({
                        'title': chart_config['title'],
                        'figure': figure,
                        'config': chart_config
                    })
            except Exception as e:
                print(f"Error creating chart {chart_config['title']}: {e}")
                continue
        
        return charts
    
    def create_custom_visualization(self, df, request, analysis_results):
        """Create a custom visualization based on user request"""
        
        domain_info = analysis_results.get('domain', {})
        column_analysis = analysis_results.get('column_analysis', {})
        
        data_context = f"""
        Available Columns: {list(df.columns)}
        Numeric Columns: {column_analysis.get('numeric', [])}
        Categorical Columns: {column_analysis.get('categorical', [])}
        DateTime Columns: {column_analysis.get('datetime', [])}
        Data Shape: {len(df)} rows × {len(df.columns)} columns
        Business Domain: {domain_info.get('type', 'general')}
        """
        
        prompt = f"""
        Create a visualization specification for this user request: "{request}"
        
        Dataset Information:
        {data_context}
        
        Sample Data: {df.head(2).to_dict('records')}
        
        Respond with a JSON object specifying the chart:
        {{
            "title": "Chart Title",
            "chart_type": "bar/line/scatter/pie/histogram/box/heatmap",
            "x_axis": "column_name or null",
            "y_axis": "column_name or null", 
            "color_by": "column_name or null",
            "description": "What this chart shows"
        }}
        
        Use ONLY column names that exist in the dataset: {list(df.columns)}
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
                chart_config = json.loads(response.text)
                figure = self.chart_generator.create_chart(df, chart_config)
                return figure
            else:
                return None
                
        except Exception as e:
            print(f"Custom visualization creation failed: {e}")
            return None

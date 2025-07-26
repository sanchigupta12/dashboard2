from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import json
import os
from agents.data_intelligence import DataIntelligenceAgent
from agents.planner import PlannerAgent
from agents.visualization import VisualizationAgent
from agents.executor import ExecutorAgent
from agents.memory import MemoryAgent
from utils.csv_processor import CSVProcessor
from utils.chart_generator import ChartGenerator

app = Flask(__name__)
CORS(app)

# Initialize agents with API key
api_key = os.getenv('GEMINI_API_KEY', 'AIzaSyD7NhpHFsCS9hCGOV5ZZ7jhxzFlqDzp9uM')
data_agent = DataIntelligenceAgent(api_key)
planner_agent = PlannerAgent()  # Planner doesn't need API key
viz_agent = VisualizationAgent(api_key)
executor_agent = ExecutorAgent(api_key)
memory_agent = MemoryAgent()
csv_processor = CSVProcessor()
chart_generator = ChartGenerator()

# Global variables to store session data
session_data = {}

@app.route('/api/upload', methods=['POST'])
def upload_csv():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({'error': 'File must be a CSV'}), 400
        
        # Process CSV
        csv_data = csv_processor.process_file(file)
        
        # Store in session
        session_data['csv_data'] = csv_data
        
        return jsonify({
            'success': True,
            'rows': len(csv_data),
            'columns': len(csv_data.columns) if hasattr(csv_data, 'columns') else 0,
            'filename': file.filename
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_data():
    try:
        if 'csv_data' not in session_data:
            return jsonify({'error': 'No data uploaded'}), 400
        
        csv_data = session_data['csv_data']
        
        # Analyze data using intelligence agent
        analysis = data_agent.analyze_data(csv_data)
        
        # Store analysis results
        session_data['analysis_results'] = analysis
        memory_agent.store_analysis(analysis)
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks', methods=['GET'])
def get_available_tasks():
    try:
        if 'analysis_results' not in session_data:
            return jsonify({'error': 'No analysis available'}), 400
        
        analysis_results = session_data['analysis_results']
        tasks = planner_agent.get_available_tasks(analysis_results)
        
        return jsonify({
            'success': True,
            'tasks': tasks
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat_with_data():
    try:
        data = request.get_json()
        question = data.get('question', '')
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        
        if 'csv_data' not in session_data or 'analysis_results' not in session_data:
            return jsonify({'error': 'No data or analysis available'}), 400
        
        csv_data = session_data['csv_data']
        analysis_results = session_data['analysis_results']
        
        # Get answer from executor agent
        answer = executor_agent.process_chat_question(question, csv_data, analysis_results)
        
        # Store interaction
        memory_agent.store_interaction('chat', {
            'question': question,
            'answer': answer
        })
        
        return jsonify({
            'success': True,
            'answer': answer
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/visualizations/suggestions', methods=['GET'])
def get_visualization_suggestions():
    try:
        if 'csv_data' not in session_data or 'analysis_results' not in session_data:
            return jsonify({'error': 'No data or analysis available'}), 400
        
        csv_data = session_data['csv_data']
        analysis_results = session_data['analysis_results']
        
        # Get suggestions from visualization agent
        suggestions = viz_agent.suggest_visualizations(csv_data, analysis_results)
        
        # Store suggestions
        session_data['viz_suggestions'] = suggestions
        
        return jsonify({
            'success': True,
            'suggestions': suggestions
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/generate', methods=['POST'])
def generate_dashboard():
    try:
        data = request.get_json()
        selected_charts = data.get('selected_charts', [])
        
        if not selected_charts:
            return jsonify({'error': 'No charts selected'}), 400
        
        if 'csv_data' not in session_data:
            return jsonify({'error': 'No data available'}), 400
        
        csv_data = session_data['csv_data']
        
        # Generate dashboard using executor agent
        charts = executor_agent.generate_dashboard(csv_data, selected_charts)
        
        # Store interaction
        memory_agent.store_interaction('visualization', {
            'selected_charts': selected_charts,
            'generated_charts': len(charts)
        })
        
        return jsonify({
            'success': True,
            'charts': charts
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/visualizations/custom', methods=['POST'])
def create_custom_visualization():
    try:
        data = request.get_json()
        request_text = data.get('request', '')
        
        if not request_text:
            return jsonify({'error': 'No request provided'}), 400
        
        if 'csv_data' not in session_data or 'analysis_results' not in session_data:
            return jsonify({'error': 'No data or analysis available'}), 400
        
        csv_data = session_data['csv_data']
        analysis_results = session_data['analysis_results']
        
        # Generate custom visualization
        chart = executor_agent.create_custom_visualization(request_text, csv_data, analysis_results)
        
        return jsonify({
            'success': True,
            'chart': chart
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/session/reset', methods=['POST'])
def reset_session():
    try:
        global session_data
        session_data = {}
        
        return jsonify({
            'success': True,
            'message': 'Session reset successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/session/status', methods=['GET'])
def get_session_status():
    try:
        return jsonify({
            'success': True,
            'has_data': 'csv_data' in session_data,
            'has_analysis': 'analysis_results' in session_data,
            'has_suggestions': 'viz_suggestions' in session_data,
            'interactions': len(memory_agent.get_session_history()) if memory_agent else 0
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
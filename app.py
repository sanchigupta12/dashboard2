import streamlit as st
import pandas as pd
import os
from agents.data_intelligence import DataIntelligenceAgent
from agents.planner import PlannerAgent
from agents.visualization import VisualizationAgent
from agents.executor import ExecutorAgent
from agents.memory import MemoryAgent
from utils.csv_processor import CSVProcessor

# Set page config
st.set_page_config(
    page_title="CSV to Dashboard AI",
    page_icon="📊",
    layout="wide"
)

# Initialize session state
if 'memory' not in st.session_state:
    st.session_state.memory = MemoryAgent()
if 'current_step' not in st.session_state:
    st.session_state.current_step = 'upload'
if 'csv_data' not in st.session_state:
    st.session_state.csv_data = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'selected_task' not in st.session_state:
    st.session_state.selected_task = None
if 'visualization_suggestions' not in st.session_state:
    st.session_state.visualization_suggestions = None
if 'selected_charts' not in st.session_state:
    st.session_state.selected_charts = []
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

def main():
    st.title("🤖 CSV to Dashboard AI")
    st.markdown("Transform your CSV files into intelligent dashboards through AI-powered analysis")
    
    # Check for API key
    api_key = os.getenv("GEMINI_API_KEY", "AIzaSyD7NhpHFsCS9hCGOV5ZZ7jhxzFlqDzp9uM")
    if not api_key:
        st.error("❌ Gemini API key not found. Please set the GEMINI_API_KEY environment variable.")
        return
    
    # Initialize agents
    data_agent = DataIntelligenceAgent(api_key)
    planner_agent = PlannerAgent()
    viz_agent = VisualizationAgent(api_key)
    executor_agent = ExecutorAgent(api_key)
    
    # Step 1: CSV Upload
    if st.session_state.current_step == 'upload':
        show_upload_interface()
    
    # Step 2: Data Analysis
    elif st.session_state.current_step == 'analysis':
        show_analysis_interface(data_agent)
    
    # Step 3: Task Planning
    elif st.session_state.current_step == 'planning':
        show_planning_interface(planner_agent)
    
    # Step 4: Task Execution
    elif st.session_state.current_step == 'execution':
        if st.session_state.selected_task == 'chat':
            show_chat_interface(executor_agent)
        elif st.session_state.selected_task == 'visualize':
            show_visualization_interface(viz_agent, executor_agent)
    
    # Sidebar - Memory and Context
    show_memory_sidebar()

def show_upload_interface():
    st.header("📁 Step 1: Upload Your CSV File")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="Upload your CSV file to begin the analysis"
    )
    
    if uploaded_file is not None:
        try:
            # Process CSV
            processor = CSVProcessor()
            df = processor.load_csv(uploaded_file)
            
            st.success(f"✅ Successfully loaded CSV with {len(df)} rows and {len(df.columns)} columns")
            
            # Show preview
            st.subheader("📋 Data Preview")
            st.dataframe(df.head(), use_container_width=True)
            
            # Store data and proceed
            st.session_state.csv_data = df
            
            if st.button("🔍 Analyze Data", type="primary"):
                st.session_state.current_step = 'analysis'
                st.rerun()
                
        except Exception as e:
            st.error(f"❌ Error loading CSV: {str(e)}")

def show_analysis_interface(data_agent):
    st.header("🧠 Step 2: AI Data Analysis")
    
    if st.session_state.csv_data is not None:
        with st.spinner("🤖 Agent 1 is analyzing your data..."):
            try:
                # Perform data intelligence analysis
                analysis = data_agent.analyze_data(st.session_state.csv_data)
                st.session_state.analysis_results = analysis
                
                # Store in memory
                st.session_state.memory.store_analysis(analysis)
                
                # Display results
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📊 Data Structure")
                    st.write(f"**Rows:** {analysis['basic_stats']['rows']}")
                    st.write(f"**Columns:** {analysis['basic_stats']['columns']}")
                    st.write(f"**Numeric Columns:** {len(analysis['column_analysis']['numeric'])}")
                    st.write(f"**Categorical Columns:** {len(analysis['column_analysis']['categorical'])}")
                
                with col2:
                    st.subheader("🏢 Business Domain")
                    st.write(f"**Detected Domain:** {analysis['domain']['type']}")
                    st.write(f"**Confidence:** {analysis['domain']['confidence']:.2f}")
                    if analysis['domain']['indicators']:
                        st.write("**Key Indicators:**")
                        for indicator in analysis['domain']['indicators'][:3]:
                            st.write(f"• {indicator}")
                
                st.subheader("🔍 Column Analysis")
                for col_type, columns in analysis['column_analysis'].items():
                    if columns:
                        st.write(f"**{col_type.title()} Columns:** {', '.join(columns)}")
                
                if st.button("➡️ Continue to Task Planning", type="primary"):
                    st.session_state.current_step = 'planning'
                    st.rerun()
                    
            except Exception as e:
                st.error(f"❌ Analysis failed: {str(e)}")
                if st.button("🔄 Retry Analysis"):
                    st.rerun()

def show_planning_interface(planner_agent):
    st.header("🎯 Step 3: Choose Your Task")
    
    if st.session_state.analysis_results:
        # Get available tasks from planner
        tasks = planner_agent.get_available_tasks(st.session_state.analysis_results)
        
        st.write("Based on your data analysis, here are the available tasks:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💬 Chat with Data", use_container_width=True):
                st.session_state.selected_task = 'chat'
                st.session_state.current_step = 'execution'
                st.rerun()
            st.write("Ask questions about your business data and get AI-powered insights")
        
        with col2:
            if st.button("📈 Create Visualizations", use_container_width=True):
                st.session_state.selected_task = 'visualize'
                st.session_state.current_step = 'execution'
                st.rerun()
            st.write("Generate domain-specific charts and interactive dashboards")
        
        # Show task recommendations
        st.subheader("🤖 AI Recommendations")
        for task_id, task_info in tasks.items():
            st.write(f"**{task_info['name']}:** {task_info['description']}")

def show_chat_interface(executor_agent):
    st.header("💬 Chat with Your Data")
    
    # Back button
    if st.button("⬅️ Back to Task Selection"):
        st.session_state.current_step = 'planning'
        st.rerun()
    
    # Display data context
    if st.session_state.analysis_results:
        with st.expander("📊 Data Context"):
            domain = st.session_state.analysis_results['domain']
            st.write(f"**Business Domain:** {domain['type']} (Confidence: {domain['confidence']:.2f})")
            st.write(f"**Data Shape:** {st.session_state.analysis_results['basic_stats']['rows']} rows × {st.session_state.analysis_results['basic_stats']['columns']} columns")
    
    # Chat interface
    st.subheader("Ask questions about your data:")
    
    # Display chat history
    for i, (question, answer) in enumerate(st.session_state.chat_history):
        with st.container():
            st.write(f"**You:** {question}")
            st.write(f"**AI:** {answer}")
            st.divider()
    
    # New question input
    question = st.text_input("Your question:", placeholder="e.g., What are the key trends in my data?")
    
    if st.button("🔍 Ask Question", type="primary") and question:
        with st.spinner("🤖 Analyzing your question..."):
            try:
                # Get answer from executor
                answer = executor_agent.chat_with_data(
                    question, 
                    st.session_state.csv_data, 
                    st.session_state.analysis_results
                )
                
                # Store in chat history
                st.session_state.chat_history.append((question, answer))
                
                # Store in memory
                st.session_state.memory.store_interaction('chat', {
                    'question': question,
                    'answer': answer
                })
                
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error processing question: {str(e)}")

def show_visualization_interface(viz_agent, executor_agent):
    st.header("📈 Create Visualizations")
    
    # Back button
    if st.button("⬅️ Back to Task Selection"):
        st.session_state.current_step = 'planning'
        st.rerun()
    
    # Get visualization suggestions if not already done
    if not st.session_state.visualization_suggestions:
        with st.spinner("🤖 Agent 2 is generating visualization suggestions..."):
            try:
                suggestions = viz_agent.suggest_visualizations(
                    st.session_state.csv_data,
                    st.session_state.analysis_results
                )
                st.session_state.visualization_suggestions = suggestions
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error generating suggestions: {str(e)}")
                return
    
    # Display suggestions
    if st.session_state.visualization_suggestions:
        st.subheader("🎨 Suggested Visualizations")
        st.write(f"Based on your {st.session_state.analysis_results['domain']['type']} domain:")
        
        # Chart selection
        suggestions = st.session_state.visualization_suggestions
        
        selected_charts = []
        for i, suggestion in enumerate(suggestions):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{suggestion['title']}**")
                st.write(f"*{suggestion['description']}*")
                st.write(f"📊 Type: {suggestion['chart_type']}")
            
            with col2:
                if st.checkbox(f"Select", key=f"chart_{i}"):
                    selected_charts.append(suggestion)
        
        # Generate dashboard
        if selected_charts and st.button("🚀 Generate Dashboard", type="primary"):
            st.session_state.selected_charts = selected_charts
            
            with st.spinner("🎨 Creating your dashboard..."):
                try:
                    # Generate charts
                    charts = executor_agent.generate_dashboard(
                        st.session_state.csv_data,
                        selected_charts
                    )
                    
                    # Display dashboard
                    st.subheader("📊 Your Interactive Dashboard")
                    
                    # Arrange charts in grid
                    for i in range(0, len(charts), 2):
                        cols = st.columns(2)
                        for j, col in enumerate(cols):
                            if i + j < len(charts):
                                with col:
                                    chart_data = charts[i + j]
                                    st.plotly_chart(
                                        chart_data['figure'], 
                                        use_container_width=True,
                                        key=f"chart_{i+j}"
                                    )
                    
                    # Store in memory
                    st.session_state.memory.store_interaction('visualization', {
                        'selected_charts': selected_charts,
                        'generated_charts': len(charts)
                    })
                    
                except Exception as e:
                    st.error(f"❌ Error generating dashboard: {str(e)}")
        
        # Additional visualization request
        st.subheader("💬 Request Additional Visualizations")
        custom_request = st.text_input(
            "Describe what you'd like to visualize:",
            placeholder="e.g., Show me sales trends by region over time"
        )
        
        if st.button("🎯 Create Custom Visualization") and custom_request:
            with st.spinner("🤖 Creating custom visualization..."):
                try:
                    custom_chart = executor_agent.create_custom_visualization(
                        st.session_state.csv_data,
                        custom_request,
                        st.session_state.analysis_results
                    )
                    
                    if custom_chart:
                        st.plotly_chart(custom_chart, use_container_width=True)
                        
                except Exception as e:
                    st.error(f"❌ Error creating custom visualization: {str(e)}")

def show_memory_sidebar():
    with st.sidebar:
        st.header("🧠 Session Memory")
        
        # Show current context
        if st.session_state.analysis_results:
            domain = st.session_state.analysis_results['domain']
            st.write(f"**Domain:** {domain['type']}")
            st.write(f"**Confidence:** {domain['confidence']:.2f}")
        
        # Show interaction count
        interactions = st.session_state.memory.get_interaction_summary()
        st.write(f"**Interactions:** {interactions['total']}")
        if interactions['chat'] > 0:
            st.write(f"• Chat: {interactions['chat']}")
        if interactions['visualization'] > 0:
            st.write(f"• Visualizations: {interactions['visualization']}")
        
        # Reset button
        if st.button("🔄 Start Over"):
            # Clear session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

if __name__ == "__main__":
    main()

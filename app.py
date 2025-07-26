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
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern design
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    
    .stApp > header {
        background-color: transparent;
    }
    
    .workflow-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
    }
    
    .workflow-step {
        background: rgba(255, 255, 255, 0.1);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #4CAF50;
    }
    
    .workflow-step.active {
        background: rgba(255, 255, 255, 0.2);
        border-left-color: #FFC107;
    }
    
    .workflow-step.completed {
        background: rgba(76, 175, 80, 0.2);
        border-left-color: #4CAF50;
    }
    
    .upload-area {
        background: #f8f9fa;
        border: 2px dashed #dee2e6;
        border-radius: 15px;
        padding: 3rem;
        text-align: center;
        margin: 2rem 0;
    }
    
    .upload-area:hover {
        border-color: #6c757d;
        background: #e9ecef;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    
    .task-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 1rem;
        transition: transform 0.2s;
        cursor: pointer;
        border: 2px solid transparent;
    }
    
    .task-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        border-color: #667eea;
    }
    
    .header-container {
        text-align: center;
        margin-bottom: 3rem;
    }
    
    .subtitle {
        color: #6c757d;
        font-size: 1.2rem;
        margin-top: 0.5rem;
    }
    
    .step-number {
        background: #667eea;
        color: white;
        border-radius: 50%;
        width: 30px;
        height: 30px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin-right: 10px;
    }
</style>
""", unsafe_allow_html=True)

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
    # Header
    st.markdown("""
    <div class="header-container">
        <h1>📊 CSV to Dashboard AI</h1>
        <p class="subtitle">Multi-Agent Data Analytics Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check for API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("❌ Gemini API key not found. Please set the GEMINI_API_KEY environment variable.")
        return
    
    # Initialize agents
    data_agent = DataIntelligenceAgent(api_key)
    planner_agent = PlannerAgent()
    viz_agent = VisualizationAgent(api_key)
    executor_agent = ExecutorAgent(api_key)
    
    # Show workflow progress
    show_workflow_progress()
    
    # Main content area
    if st.session_state.current_step == 'upload':
        show_modern_upload_interface()
    elif st.session_state.current_step == 'analysis':
        show_modern_analysis_interface(data_agent)
    elif st.session_state.current_step == 'planning':
        show_modern_planning_interface(planner_agent)
    elif st.session_state.current_step == 'execution':
        if st.session_state.selected_task == 'chat':
            show_modern_chat_interface(executor_agent)
        elif st.session_state.selected_task == 'visualize':
            show_modern_visualization_interface(viz_agent, executor_agent)
    
    # Sidebar
    show_modern_sidebar()

def show_workflow_progress():
    """Display modern workflow progress"""
    steps = [
        {"name": "Data Upload", "status": "completed" if st.session_state.csv_data is not None else ("active" if st.session_state.current_step == 'upload' else "pending")},
        {"name": "Data Intelligence Analysis", "status": "completed" if st.session_state.analysis_results is not None else ("active" if st.session_state.current_step == 'analysis' else "pending")},
        {"name": "Task Planning", "status": "completed" if st.session_state.selected_task is not None else ("active" if st.session_state.current_step == 'planning' else "pending")},
        {"name": "Task Execution", "status": "active" if st.session_state.current_step == 'execution' else "pending"}
    ]
    
    st.markdown("""
    <div class="workflow-container">
        <h3>🧠 AI Agent Workflow</h3>
    """, unsafe_allow_html=True)
    
    for i, step in enumerate(steps):
        status_class = step["status"]
        if status_class == "completed":
            icon = "✅"
        elif status_class == "active":
            icon = "🔄"
        else:
            icon = "⏳"
            
        st.markdown(f"""
        <div class="workflow-step {status_class}">
            <span class="step-number">{i+1}</span>
            {icon} {step["name"]}
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def show_modern_upload_interface():
    st.markdown("""
    <div style="text-align: center; margin: 2rem 0;">
        <h2>🎯 Transform Your Data with AI</h2>
        <p>Upload your CSV and let our AI agents create intelligent dashboards and insights in minutes</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create columns for centering
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="upload-area">
            <h3>📁 Upload Your CSV File</h3>
            <p>Drag and drop your CSV file here, or click to browse</p>
            <small>Supports CSV files up to 10MB</small>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Choose File",
            type=['csv'],
            help="Upload your CSV file to begin the analysis",
            label_visibility="collapsed"
        )
        
        if uploaded_file is not None:
            try:
                with st.spinner("Processing your CSV file..."):
                    processor = CSVProcessor()
                    df = processor.load_csv(uploaded_file)
                
                st.success(f"✅ Successfully loaded CSV with {len(df)} rows and {len(df.columns)} columns")
                
                # Show preview in an expander
                with st.expander("📋 Preview Data", expanded=True):
                    st.dataframe(df.head(), use_container_width=True)
                
                st.session_state.csv_data = df
                
                if st.button("🚀 Start AI Analysis", type="primary", use_container_width=True):
                    st.session_state.current_step = 'analysis'
                    st.rerun()
                    
            except Exception as e:
                st.error(f"❌ Error loading CSV: {str(e)}")

def show_modern_analysis_interface(data_agent):
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

def show_modern_planning_interface(planner_agent):
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

def show_modern_chat_interface(executor_agent):
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

def show_modern_visualization_interface(viz_agent, executor_agent):
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
                                        key=f"dashboard_chart_{i}_{j}"
                                    )
                    
                    # Store in memory
                    st.session_state.memory.store_interaction('visualization', {
                        'selected_charts': selected_charts,
                        'generated_charts': len(charts)
                    })
                    
                except Exception as e:
                    st.error(f"❌ Error generating dashboard: {str(e)}")
        
        # Additional visualization request
        st.markdown("---")
        st.markdown("### 💬 Request Additional Visualizations")
        st.markdown("Describe what you'd like to visualize:")
        
        custom_request = st.text_input(
            "Custom request",
            placeholder="e.g., Show me sales trends by region over time",
            label_visibility="collapsed"
        )
        
        if st.button("🎯 Create Custom Visualization", use_container_width=True) and custom_request:
            with st.spinner("🤖 Creating custom visualization..."):
                try:
                    custom_chart = executor_agent.create_custom_visualization(
                        st.session_state.csv_data,
                        custom_request,
                        st.session_state.analysis_results
                    )
                    
                    if custom_chart:
                        st.markdown("### Your Interactive Dashboard")
                        st.plotly_chart(custom_chart, use_container_width=True, key=f"custom_chart_{len(st.session_state.chat_history)}")
                    else:
                        st.error("Could not create the requested visualization. Please try a different description.")
                        
                except Exception as e:
                    st.error(f"❌ Error creating custom visualization: {str(e)}")

def show_modern_sidebar():
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

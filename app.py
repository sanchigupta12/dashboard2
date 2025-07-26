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

# Tailwind CSS and custom styles
st.markdown("""
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
<style>
    .stApp > header {
        background-color: transparent;
    }
    
    .gradient-bg {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .step-indicator {
        width: 32px;
        height: 32px;
        background: #667eea;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        margin-right: 12px;
    }
    
    .step-completed {
        background: #10b981;
    }
    
    .step-active {
        background: #f59e0b;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    .hover-lift:hover {
        transform: translateY(-2px);
        transition: all 0.2s ease;
    }
    
    .card-shadow {
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    .card-shadow:hover {
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
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
    # Header with Tailwind
    st.markdown("""
    <div class="text-center mb-12">
        <h1 class="text-4xl font-bold text-gray-800 mb-4">📊 CSV to Dashboard AI</h1>
        <p class="text-xl text-gray-600">Multi-Agent Data Analytics Platform</p>
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
    <div class="gradient-bg rounded-2xl p-8 mb-8 text-white">
        <h3 class="text-2xl font-bold mb-6">🧠 AI Agent Workflow</h3>
    """, unsafe_allow_html=True)
    
    for i, step in enumerate(steps):
        status_class = step["status"]
        if status_class == "completed":
            icon = "✅"
        elif status_class == "active":
            icon = "🔄"
        else:
            icon = "⏳"
            
        step_class = ""
        if status_class == "completed":
            step_class = "bg-white bg-opacity-20 border-l-4 border-green-400"
        elif status_class == "active":
            step_class = "bg-white bg-opacity-30 border-l-4 border-yellow-400"
        else:
            step_class = "bg-white bg-opacity-10 border-l-4 border-gray-400"
            
        indicator_class = "step-indicator"
        if status_class == "completed":
            indicator_class += " step-completed"
        elif status_class == "active":
            indicator_class += " step-active"
            
        st.markdown(f"""
        <div class="rounded-lg p-4 mb-3 {step_class}">
            <div class="flex items-center">
                <span class="{indicator_class}">{i+1}</span>
                <span class="text-lg font-medium">{icon} {step["name"]}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def show_modern_upload_interface():
    st.markdown("""
    <div class="text-center my-8">
        <h2 class="text-3xl font-bold text-gray-800 mb-4">🎯 Transform Your Data with AI</h2>
        <p class="text-lg text-gray-600">Upload your CSV and let our AI agents create intelligent dashboards and insights in minutes</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create columns for centering
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="bg-gray-50 border-2 border-dashed border-gray-300 rounded-2xl p-12 text-center my-8 hover:border-gray-400 hover:bg-gray-100 transition-all duration-200">
            <div class="mb-4">
                <svg class="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                    <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            </div>
            <h3 class="text-xl font-semibold text-gray-700 mb-2">📁 Upload Your CSV File</h3>
            <p class="text-gray-500 mb-2">Drag and drop your CSV file here, or click to browse</p>
            <p class="text-sm text-gray-400">Supports CSV files up to 10MB</p>
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
                
                # Display results with Tailwind styling
                col1, col2 = st.columns(2, gap="large")
                
                with col1:
                    st.markdown("""
                    <div class="bg-white rounded-xl p-6 card-shadow border-l-4 border-blue-500">
                        <h3 class="text-lg font-bold text-gray-800 mb-4 flex items-center">
                            <span class="mr-2">📊</span> Data Structure
                        </h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.metric("Rows", f"{analysis['basic_stats']['rows']:,}")
                    st.metric("Columns", analysis['basic_stats']['columns'])
                    st.metric("Numeric Columns", len(analysis['column_analysis']['numeric']))
                    st.metric("Categorical Columns", len(analysis['column_analysis']['categorical']))
                
                with col2:
                    st.markdown("""
                    <div class="bg-white rounded-xl p-6 card-shadow border-l-4 border-purple-500">
                        <h3 class="text-lg font-bold text-gray-800 mb-4 flex items-center">
                            <span class="mr-2">🏢</span> Business Domain
                        </h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    domain_type = analysis['domain']['type'].title()
                    confidence = analysis['domain']['confidence']
                    
                    st.metric("Detected Domain", domain_type)
                    st.metric("Confidence", f"{confidence:.2%}")
                    
                    if analysis['domain']['indicators']:
                        st.markdown("**Key Indicators:**")
                        for indicator in analysis['domain']['indicators'][:3]:
                            st.markdown(f"• {indicator}")
                
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
        
        st.markdown("""
        <div class="mb-8">
            <p class="text-lg text-gray-600 text-center">Based on your data analysis, here are the available tasks:</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2, gap="large")
        
        with col1:
            st.markdown("""
            <div class="bg-white rounded-2xl p-8 card-shadow hover-lift border-2 border-transparent hover:border-blue-200 transition-all duration-200 mb-4">
                <div class="text-center">
                    <div class="text-4xl mb-4">💬</div>
                    <h3 class="text-xl font-bold text-gray-800 mb-3">Chat with Data</h3>
                    <p class="text-gray-600 mb-6">Ask questions about your business data and get AI-powered insights</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("💬 Start Chat", use_container_width=True, type="primary"):
                st.session_state.selected_task = 'chat'
                st.session_state.current_step = 'execution'
                st.rerun()
        
        with col2:
            st.markdown("""
            <div class="bg-white rounded-2xl p-8 card-shadow hover-lift border-2 border-transparent hover:border-blue-200 transition-all duration-200 mb-4">
                <div class="text-center">
                    <div class="text-4xl mb-4">📈</div>
                    <h3 class="text-xl font-bold text-gray-800 mb-3">Create Visualizations</h3>
                    <p class="text-gray-600 mb-6">Generate domain-specific charts and interactive dashboards</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("📈 Create Dashboard", use_container_width=True, type="primary"):
                st.session_state.selected_task = 'visualize'
                st.session_state.current_step = 'execution'
                st.rerun()
        
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
    
    # Display suggestions with Tailwind
    if st.session_state.visualization_suggestions:
        domain_type = st.session_state.analysis_results['domain']['type'].title()
        
        st.markdown(f"""
        <div class="mb-8">
            <h2 class="text-2xl font-bold text-gray-800 mb-2">🎨 Suggested Visualizations</h2>
            <p class="text-gray-600">Based on your <span class="font-semibold text-blue-600">{domain_type}</span> domain analysis:</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Chart selection with Tailwind cards
        suggestions = st.session_state.visualization_suggestions
        selected_charts = []
        
        for i, suggestion in enumerate(suggestions):
            cols = st.columns([1, 10, 1])
            with cols[1]:
                chart_selected = st.checkbox(
                    f"Select {suggestion['title']}",
                    key=f"chart_{i}",
                    label_visibility="collapsed"
                )
                
                if chart_selected:
                    selected_charts.append(suggestion)
                
                # Card styling based on selection
                border_class = "border-blue-400 bg-blue-50" if chart_selected else "border-gray-200 hover:border-blue-300"
                
                st.markdown(f"""
                <div class="bg-white rounded-xl p-6 card-shadow border-2 {border_class} mb-4 transition-all duration-200">
                    <div class="flex items-start justify-between mb-3">
                        <h3 class="text-lg font-bold text-gray-800">{suggestion['title']}</h3>
                        <span class="bg-gradient-to-r from-blue-500 to-purple-600 text-white text-xs font-medium px-3 py-1 rounded-full">
                            {suggestion['chart_type'].title()}
                        </span>
                    </div>
                    <p class="text-gray-600 text-sm mb-3">{suggestion['description']}</p>
                    <div class="text-xs text-gray-500">
                        <strong>Business Value:</strong> {suggestion.get('domain_value', 'Provides valuable business insights')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Generate dashboard with enhanced button
        if selected_charts:
            st.markdown("""
            <div class="text-center my-8">
                <p class="text-sm text-gray-600 mb-4">
                    ✅ {count} visualization{plural} selected
                </p>
            </div>
            """.format(count=len(selected_charts), plural="s" if len(selected_charts) > 1 else ""), unsafe_allow_html=True)
            
        if selected_charts and st.button("🚀 Generate Interactive Dashboard", type="primary", use_container_width=True):
            st.session_state.selected_charts = selected_charts
            
            with st.spinner("🎨 Creating your dashboard..."):
                try:
                    # Generate charts
                    charts = executor_agent.generate_dashboard(
                        st.session_state.csv_data,
                        selected_charts
                    )
                    
                    # Display dashboard with Tailwind header
                    st.markdown("""
                    <div class="text-center my-8">
                        <h2 class="text-3xl font-bold text-gray-800 mb-2">📊 Your Interactive Dashboard</h2>
                        <p class="text-gray-600">AI-generated visualizations based on your data analysis</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
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

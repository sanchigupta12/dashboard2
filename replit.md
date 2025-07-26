# CSV to Dashboard AI - Repository Analysis

## Overview

This is a Streamlit-based AI-powered application that transforms CSV files into intelligent dashboards. The system uses a multi-agent architecture with Google's Gemini AI to analyze data, suggest visualizations, and provide interactive chat capabilities for business insights.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a multi-agent architecture pattern with clear separation of concerns:

### Frontend Architecture
- **Framework**: Streamlit web application
- **UI Pattern**: Step-by-step workflow (upload → analyze → interact)
- **State Management**: Streamlit session state for maintaining user context
- **Layout**: Wide layout with responsive design

### Backend Architecture
- **Pattern**: Agent-based system with specialized roles
- **Core Agents**:
  - DataIntelligenceAgent: CSV analysis and domain detection
  - PlannerAgent: Task recommendation using ReAct methodology
  - VisualizationAgent: AI-powered chart suggestions
  - ExecutorAgent: Chat handling and dashboard generation
  - MemoryAgent: Context and interaction storage
- **AI Integration**: Google Gemini API for natural language processing

## Key Components

### 1. Data Processing Layer (`utils/`)
- **CSVProcessor**: Handles file upload with multiple encoding support
- **ChartGenerator**: Creates Plotly visualizations from configurations

### 2. Agent System (`agents/`)
- **DataIntelligenceAgent**: Analyzes data structure, detects business domains, assesses quality
- **PlannerAgent**: Implements ReAct reasoning to suggest available tasks
- **VisualizationAgent**: Generates domain-specific visualization recommendations
- **ExecutorAgent**: Manages chat interactions and dashboard creation
- **MemoryAgent**: Maintains conversation context and user preferences

### 3. Main Application (`app.py`)
- Entry point with Streamlit configuration
- Session state management
- Agent orchestration
- UI workflow coordination

## Data Flow

1. **File Upload**: User uploads CSV file
2. **Data Processing**: CSVProcessor handles encoding and cleaning
3. **Intelligence Analysis**: DataIntelligenceAgent analyzes structure and domain
4. **Task Planning**: PlannerAgent determines available actions
5. **User Interaction**: Two main paths:
   - Chat: ExecutorAgent handles Q&A with business context
   - Visualization: VisualizationAgent suggests charts, ChartGenerator creates them
6. **Memory Storage**: MemoryAgent stores interactions for context

## External Dependencies

### AI Services
- **Google Gemini API**: Core AI functionality for analysis and chat
- **API Key Management**: Environment variable or hardcoded fallback

### Python Libraries
- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive visualization library
- **NumPy**: Numerical computing support

### Data Formats
- **CSV Support**: Multiple encodings (UTF-8, Latin1, CP1252, ISO-8859-1)
- **JSON**: Internal data exchange format

## Deployment Strategy

### Current Setup
- **Platform**: Streamlit-based web application
- **Configuration**: Page config with dashboard branding
- **API Integration**: Direct Google Gemini API calls

### Architecture Decisions

#### Multi-Agent Design
- **Problem**: Complex CSV analysis and visualization generation
- **Solution**: Specialized agents for different responsibilities
- **Benefits**: Modular, maintainable, clear separation of concerns
- **Trade-offs**: More complex than monolithic approach

#### Streamlit Frontend
- **Problem**: Need for rapid prototyping and data science workflows
- **Solution**: Streamlit for quick web interface development
- **Benefits**: Fast development, built-in data handling, session state
- **Trade-offs**: Limited customization compared to full web frameworks

#### Session State Management
- **Problem**: Maintaining context across user interactions
- **Solution**: Streamlit session state with MemoryAgent
- **Benefits**: Persistent conversation context, user preference tracking
- **Trade-offs**: Memory usage grows with session length

#### Plotly Visualization
- **Problem**: Need for interactive, business-quality charts
- **Solution**: Plotly Express and Graph Objects
- **Benefits**: Interactive charts, professional appearance, web-native
- **Trade-offs**: Larger bundle size compared to static charts

#### AI-Powered Domain Detection
- **Problem**: Generic visualizations don't provide business value
- **Solution**: Gemini AI analyzes data to detect business domain
- **Benefits**: Context-aware suggestions, domain-specific insights
- **Trade-offs**: API dependency, potential accuracy issues

The system is designed for data analysts and business users who need quick insights from CSV files without technical expertise in data visualization or analysis.
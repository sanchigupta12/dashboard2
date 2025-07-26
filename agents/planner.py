class PlannerAgent:
    """Planner Agent: Uses ReAct methodology to plan available tasks"""
    
    def __init__(self):
        self.available_tasks = {
            'chat': {
                'name': 'Chat with Data',
                'description': 'Ask questions about your business data and get AI-powered insights',
                'requirements': ['analyzed_data'],
                'benefits': ['Business insights', 'Data exploration', 'Question answering']
            },
            'visualize': {
                'name': 'Create Visualizations',
                'description': 'Generate domain-specific charts and interactive dashboards',
                'requirements': ['analyzed_data', 'domain_detected'],
                'benefits': ['Interactive charts', 'Domain-specific visualizations', 'Dashboard creation']
            }
        }
    
    def get_available_tasks(self, analysis_results):
        """
        Analyze current context and return available tasks
        ReAct: Reason about what tasks are possible given current state
        """
        
        # Reasoning: Check what tasks are available based on analysis
        available = {}
        
        if analysis_results:
            # Chat is always available if we have analyzed data
            available['chat'] = self.available_tasks['chat']
            
            # Visualizations are available if domain is detected with reasonable confidence
            if (analysis_results.get('domain', {}).get('confidence', 0) > 0.3 or 
                len(analysis_results.get('column_analysis', {}).get('numeric', [])) > 0):
                available['visualize'] = self.available_tasks['visualize']
        
        return available
    
    def recommend_task(self, analysis_results, user_context=None):
        """
        ReAct: Recommend the best task based on data characteristics
        """
        if not analysis_results:
            return None
        
        domain_confidence = analysis_results.get('domain', {}).get('confidence', 0)
        numeric_columns = len(analysis_results.get('column_analysis', {}).get('numeric', []))
        
        # Action: Recommend based on data characteristics
        if domain_confidence > 0.7 and numeric_columns >= 2:
            return {
                'task': 'visualize',
                'reason': 'Strong domain detection and multiple numeric columns make visualization highly valuable',
                'confidence': 0.9
            }
        elif domain_confidence > 0.5:
            return {
                'task': 'chat',
                'reason': 'Good domain understanding enables insightful data conversations',
                'confidence': 0.7
            }
        else:
            return {
                'task': 'chat',
                'reason': 'Start with data exploration through questions',
                'confidence': 0.6
            }
    
    def plan_workflow(self, analysis_results):
        """
        ReAct: Plan the optimal workflow sequence
        """
        workflow = []
        
        # Thought: Always start with understanding the data better
        workflow.append({
            'step': 1,
            'task': 'chat',
            'purpose': 'Explore and understand data characteristics',
            'suggested_questions': [
                'What are the key trends in this data?',
                'What business insights can you provide?',
                'Are there any data quality issues?'
            ]
        })
        
        # Observation: If domain is well-detected, visualization is valuable
        if analysis_results.get('domain', {}).get('confidence', 0) > 0.5:
            workflow.append({
                'step': 2,
                'task': 'visualize',
                'purpose': 'Create domain-specific visualizations',
                'benefits': ['Visual insights', 'Dashboard creation', 'Data presentation']
            })
        
        return workflow

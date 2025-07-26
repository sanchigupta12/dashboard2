import json
from datetime import datetime

class MemoryAgent:
    """Memory Agent: Stores and manages conversation context and interactions"""
    
    def __init__(self):
        self.interactions = []
        self.analysis_context = None
        self.user_preferences = {}
        self.session_start = datetime.now()
    
    def store_analysis(self, analysis_results):
        """Store the initial data analysis results"""
        self.analysis_context = {
            'timestamp': datetime.now().isoformat(),
            'analysis': analysis_results
        }
        
        self.interactions.append({
            'type': 'analysis',
            'timestamp': datetime.now().isoformat(),
            'data': {
                'domain': analysis_results.get('domain', {}),
                'columns_analyzed': len(analysis_results.get('column_analysis', {}).get('numeric', [])) + 
                                  len(analysis_results.get('column_analysis', {}).get('categorical', [])),
                'quality_score': analysis_results.get('quality', {}).get('completeness', 0)
            }
        })
    
    def store_interaction(self, interaction_type, interaction_data):
        """Store user interactions (chat, visualization, etc.)"""
        self.interactions.append({
            'type': interaction_type,
            'timestamp': datetime.now().isoformat(),
            'data': interaction_data
        })
        
        # Update user preferences based on interactions
        self._update_preferences(interaction_type, interaction_data)
    
    def get_conversation_context(self):
        """Get relevant context for continuing conversations"""
        context = {
            'session_duration': (datetime.now() - self.session_start).total_seconds() / 60,  # minutes
            'total_interactions': len(self.interactions),
            'analysis_context': self.analysis_context,
            'recent_interactions': self.interactions[-5:] if len(self.interactions) > 5 else self.interactions,
            'user_preferences': self.user_preferences
        }
        return context
    
    def get_interaction_summary(self):
        """Get summary of all interactions"""
        summary = {
            'total': len(self.interactions),
            'chat': 0,
            'visualization': 0,
            'analysis': 0
        }
        
        for interaction in self.interactions:
            interaction_type = interaction['type']
            if interaction_type in summary:
                summary[interaction_type] += 1
        
        return summary
    
    def get_domain_insights(self):
        """Get insights about detected domain and user behavior"""
        if not self.analysis_context:
            return None
        
        domain_info = self.analysis_context['analysis'].get('domain', {})
        interaction_patterns = self._analyze_interaction_patterns()
        
        return {
            'detected_domain': domain_info.get('type', 'unknown'),
            'domain_confidence': domain_info.get('confidence', 0),
            'user_engagement': interaction_patterns,
            'session_insights': self._get_session_insights()
        }
    
    def _update_preferences(self, interaction_type, interaction_data):
        """Update user preferences based on their behavior"""
        if interaction_type == 'visualization':
            # Track preferred chart types
            if 'selected_charts' in interaction_data:
                chart_types = [chart.get('chart_type') for chart in interaction_data['selected_charts']]
                for chart_type in chart_types:
                    if 'preferred_chart_types' not in self.user_preferences:
                        self.user_preferences['preferred_chart_types'] = {}
                    
                    current_count = self.user_preferences['preferred_chart_types'].get(chart_type, 0)
                    self.user_preferences['preferred_chart_types'][chart_type] = current_count + 1
        
        elif interaction_type == 'chat':
            # Track question patterns
            if 'question' in interaction_data:
                question_lower = interaction_data['question'].lower()
                question_keywords = ['trend', 'average', 'total', 'compare', 'analyze', 'insight']
                
                for keyword in question_keywords:
                    if keyword in question_lower:
                        if 'question_interests' not in self.user_preferences:
                            self.user_preferences['question_interests'] = {}
                        
                        current_count = self.user_preferences['question_interests'].get(keyword, 0)
                        self.user_preferences['question_interests'][keyword] = current_count + 1
    
    def _analyze_interaction_patterns(self):
        """Analyze user interaction patterns"""
        if not self.interactions:
            return {}
        
        patterns = {
            'most_used_feature': None,
            'interaction_frequency': len(self.interactions),
            'feature_usage': {}
        }
        
        # Count feature usage
        for interaction in self.interactions:
            feature = interaction['type']
            patterns['feature_usage'][feature] = patterns['feature_usage'].get(feature, 0) + 1
        
        # Find most used feature
        if patterns['feature_usage']:
            patterns['most_used_feature'] = max(patterns['feature_usage'], key=patterns['feature_usage'].get)
        
        return patterns
    
    def _get_session_insights(self):
        """Generate insights about the current session"""
        session_duration = (datetime.now() - self.session_start).total_seconds() / 60
        
        insights = {
            'session_duration_minutes': round(session_duration, 1),
            'engagement_level': 'high' if len(self.interactions) > 5 else 'medium' if len(self.interactions) > 2 else 'low',
            'workflow_completion': self._assess_workflow_completion()
        }
        
        return insights
    
    def _assess_workflow_completion(self):
        """Assess how much of the workflow the user has completed"""
        completed_steps = set()
        
        for interaction in self.interactions:
            if interaction['type'] == 'analysis':
                completed_steps.add('data_upload')
                completed_steps.add('data_analysis')
            elif interaction['type'] == 'chat':
                completed_steps.add('data_exploration')
            elif interaction['type'] == 'visualization':
                completed_steps.add('visualization_creation')
        
        total_possible_steps = {'data_upload', 'data_analysis', 'data_exploration', 'visualization_creation'}
        completion_percentage = len(completed_steps) / len(total_possible_steps)
        
        return {
            'completed_steps': list(completed_steps),
            'completion_percentage': completion_percentage,
            'next_suggested_step': self._suggest_next_step(completed_steps)
        }
    
    def _suggest_next_step(self, completed_steps):
        """Suggest the next logical step based on completed steps"""
        if 'data_analysis' in completed_steps and 'data_exploration' not in completed_steps:
            return 'chat_with_data'
        elif 'data_exploration' in completed_steps and 'visualization_creation' not in completed_steps:
            return 'create_visualizations'
        elif 'visualization_creation' in completed_steps:
            return 'explore_additional_insights'
        else:
            return 'continue_analysis'

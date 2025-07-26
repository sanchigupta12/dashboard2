import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

class ChartGenerator:
    """Utility class for generating Plotly charts"""
    
    def __init__(self):
        self.color_palette = px.colors.qualitative.Set3
    
    def create_chart(self, df, chart_config):
        """Create a Plotly chart based on configuration"""
        
        chart_type = chart_config.get('chart_type', '').lower()
        title = chart_config.get('title', 'Chart')
        x_axis = chart_config.get('x_axis')
        y_axis = chart_config.get('y_axis')
        color_by = chart_config.get('color_by')
        
        try:
            # Validate columns exist
            if x_axis and x_axis not in df.columns:
                x_axis = None
            if y_axis and y_axis not in df.columns:
                y_axis = None
            if color_by and color_by not in df.columns:
                color_by = None
            
            # Route to appropriate chart creation method
            if chart_type == 'bar':
                return self._create_bar_chart(df, title, x_axis, y_axis, color_by)
            elif chart_type == 'line':
                return self._create_line_chart(df, title, x_axis, y_axis, color_by)
            elif chart_type == 'scatter':
                return self._create_scatter_chart(df, title, x_axis, y_axis, color_by)
            elif chart_type == 'pie':
                return self._create_pie_chart(df, title, x_axis, color_by)
            elif chart_type == 'histogram':
                return self._create_histogram(df, title, x_axis, color_by)
            elif chart_type == 'box':
                return self._create_box_plot(df, title, x_axis, y_axis, color_by)
            elif chart_type == 'heatmap':
                return self._create_heatmap(df, title, x_axis, y_axis)
            else:
                # Default to bar chart
                return self._create_bar_chart(df, title, x_axis, y_axis, color_by)
                
        except Exception as e:
            print(f"Error creating {chart_type} chart: {e}")
            return self._create_error_chart(title, str(e))
    
    def _create_bar_chart(self, df, title, x_axis, y_axis, color_by):
        """Create a bar chart"""
        
        if not x_axis:
            # If no x_axis specified, use first categorical or all columns
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns
            x_axis = categorical_cols[0] if len(categorical_cols) > 0 else df.columns[0]
        
        if not y_axis:
            # If no y_axis specified, use count or first numeric column
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                y_axis = numeric_cols[0]
            else:
                # Use value counts
                value_counts = df[x_axis].value_counts()
                fig = px.bar(
                    x=value_counts.index,
                    y=value_counts.values,
                    title=title,
                    labels={'x': x_axis, 'y': 'Count'}
                )
                return fig
        
        # Create grouped bar chart if color_by is specified
        if color_by:
            # Group by x_axis and color_by, aggregate y_axis
            grouped_df = df.groupby([x_axis, color_by])[y_axis].sum().reset_index()
            fig = px.bar(
                grouped_df,
                x=x_axis,
                y=y_axis,
                color=color_by,
                title=title,
                color_discrete_sequence=self.color_palette
            )
        else:
            fig = px.bar(df, x=x_axis, y=y_axis, title=title)
        
        fig.update_layout(xaxis_tickangle=-45)
        return fig
    
    def _create_line_chart(self, df, title, x_axis, y_axis, color_by):
        """Create a line chart"""
        
        if not x_axis or not y_axis:
            return self._create_error_chart(title, "Line chart requires both X and Y axes")
        
        # Sort by x_axis for better line visualization
        df_sorted = df.sort_values(by=x_axis)
        
        if color_by:
            fig = px.line(
                df_sorted,
                x=x_axis,
                y=y_axis,
                color=color_by,
                title=title,
                color_discrete_sequence=self.color_palette
            )
        else:
            fig = px.line(df_sorted, x=x_axis, y=y_axis, title=title)
        
        return fig
    
    def _create_scatter_chart(self, df, title, x_axis, y_axis, color_by):
        """Create a scatter plot"""
        
        if not x_axis or not y_axis:
            return self._create_error_chart(title, "Scatter plot requires both X and Y axes")
        
        if color_by:
            fig = px.scatter(
                df,
                x=x_axis,
                y=y_axis,
                color=color_by,
                title=title,
                color_discrete_sequence=self.color_palette
            )
        else:
            fig = px.scatter(df, x=x_axis, y=y_axis, title=title)
        
        return fig
    
    def _create_pie_chart(self, df, title, x_axis, color_by):
        """Create a pie chart"""
        
        if not x_axis:
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns
            x_axis = categorical_cols[0] if len(categorical_cols) > 0 else df.columns[0]
        
        # Get value counts for the pie chart
        value_counts = df[x_axis].value_counts()
        
        fig = px.pie(
            values=value_counts.values,
            names=value_counts.index,
            title=title,
            color_discrete_sequence=self.color_palette
        )
        
        return fig
    
    def _create_histogram(self, df, title, x_axis, color_by):
        """Create a histogram"""
        
        if not x_axis:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            x_axis = numeric_cols[0] if len(numeric_cols) > 0 else df.columns[0]
        
        if color_by:
            fig = px.histogram(
                df,
                x=x_axis,
                color=color_by,
                title=title,
                color_discrete_sequence=self.color_palette
            )
        else:
            fig = px.histogram(df, x=x_axis, title=title)
        
        return fig
    
    def _create_box_plot(self, df, title, x_axis, y_axis, color_by):
        """Create a box plot"""
        
        if not y_axis:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            y_axis = numeric_cols[0] if len(numeric_cols) > 0 else None
        
        if not y_axis:
            return self._create_error_chart(title, "Box plot requires a numeric Y axis")
        
        if x_axis:
            if color_by:
                fig = px.box(
                    df,
                    x=x_axis,
                    y=y_axis,
                    color=color_by,
                    title=title,
                    color_discrete_sequence=self.color_palette
                )
            else:
                fig = px.box(df, x=x_axis, y=y_axis, title=title)
        else:
            fig = px.box(df, y=y_axis, title=title)
        
        return fig
    
    def _create_heatmap(self, df, title, x_axis, y_axis):
        """Create a heatmap (correlation matrix if no axes specified)"""
        
        if not x_axis or not y_axis:
            # Create correlation heatmap for numeric columns
            numeric_df = df.select_dtypes(include=[np.number])
            if numeric_df.empty:
                return self._create_error_chart(title, "No numeric columns available for heatmap")
            
            corr_matrix = numeric_df.corr()
            
            fig = px.imshow(
                corr_matrix,
                title=f"{title} - Correlation Matrix",
                color_continuous_scale='RdBu_r',
                aspect='auto'
            )
        else:
            # Create pivot table heatmap
            try:
                # Try to create a pivot table
                pivot_df = df.pivot_table(
                    index=y_axis,
                    columns=x_axis,
                    values=df.select_dtypes(include=[np.number]).columns[0],
                    aggfunc='mean'
                )
                
                fig = px.imshow(
                    pivot_df,
                    title=title,
                    color_continuous_scale='Viridis',
                    aspect='auto'
                )
            except Exception:
                return self._create_error_chart(title, "Could not create pivot table for heatmap")
        
        return fig
    
    def _create_error_chart(self, title, error_message):
        """Create an error chart when chart generation fails"""
        
        fig = go.Figure()
        fig.add_annotation(
            text=f"Error creating chart:<br>{error_message}",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            xanchor='center', yanchor='middle',
            showarrow=False,
            font_size=16
        )
        fig.update_layout(
            title=title,
            xaxis={'visible': False},
            yaxis={'visible': False}
        )
        
        return fig

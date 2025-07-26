// Global variables
let csvData = null;
let analysisResults = null;
let selectedCharts = [];
let chatHistory = [];
let interactionCount = 0;

// Configuration
const API_BASE_URL = 'http://localhost:5001'; // Will connect to Python backend

// Utility functions
function updateWorkflowStep(step, status) {
    const steps = ['upload', 'analysis', 'planning', 'execution'];
    const stepElements = document.querySelectorAll('.workflow-step');
    
    steps.forEach((stepName, index) => {
        const stepElement = stepElements[index];
        const indicator = stepElement.querySelector('.step-indicator');
        const container = stepElement.querySelector('div');
        
        if (stepName === step) {
            if (status === 'active') {
                indicator.className = 'step-indicator step-active';
                container.className = 'flex items-center rounded-lg p-4 bg-white bg-opacity-30 border-l-4 border-yellow-400';
                stepElement.querySelector('span:last-child').innerHTML = `🔄 ${getStepName(stepName)}`;
            } else if (status === 'completed') {
                indicator.className = 'step-indicator step-completed';
                container.className = 'flex items-center rounded-lg p-4 bg-white bg-opacity-20 border-l-4 border-green-400';
                stepElement.querySelector('span:last-child').innerHTML = `✅ ${getStepName(stepName)}`;
            }
        } else if (steps.indexOf(stepName) < steps.indexOf(step)) {
            indicator.className = 'step-indicator step-completed';
            container.className = 'flex items-center rounded-lg p-4 bg-white bg-opacity-20 border-l-4 border-green-400';
            stepElement.querySelector('span:last-child').innerHTML = `✅ ${getStepName(stepName)}`;
        }
    });
}

function getStepName(step) {
    const stepNames = {
        'upload': 'Data Upload',
        'analysis': 'Data Intelligence Analysis',
        'planning': 'Task Planning',
        'execution': 'Task Execution'
    };
    return stepNames[step] || step;
}

function showSection(sectionId) {
    // Hide all sections
    const sections = ['upload-section', 'analysis-section', 'planning-section', 'chat-section', 'visualization-section'];
    sections.forEach(id => {
        document.getElementById(id).classList.add('hidden');
    });
    
    // Show target section
    document.getElementById(sectionId).classList.remove('hidden');
}

function updateSessionInfo() {
    document.getElementById('interaction-count').textContent = interactionCount;
}

// File upload handling
function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    if (!file.name.endsWith('.csv')) {
        alert('Please select a CSV file');
        return;
    }
    
    if (file.size > 10 * 1024 * 1024) { // 10MB limit
        alert('File size must be less than 10MB');
        return;
    }
    
    // Read file content
    const reader = new FileReader();
    reader.onload = function(e) {
        const csvContent = e.target.result;
        csvData = parseCSV(csvContent);
        
        // Update UI
        document.querySelector('.upload-area').innerHTML = `
            <div class="mb-4">
                <i class="fas fa-check-circle text-4xl text-green-500 mb-4"></i>
            </div>
            <h3 class="text-xl font-semibold text-gray-700 mb-2">✅ File Uploaded Successfully</h3>
            <p class="text-gray-500 mb-2">${file.name}</p>
            <p class="text-sm text-gray-400">${csvData.length} rows × ${csvData[0] ? Object.keys(csvData[0]).length : 0} columns</p>
        `;
        
        document.getElementById('analyzeBtn').classList.remove('hidden');
        updateWorkflowStep('upload', 'completed');
    };
    
    reader.readAsText(file);
}

// CSV parsing function
function parseCSV(csvContent) {
    const lines = csvContent.split('\n');
    const headers = lines[0].split(',').map(h => h.trim());
    const data = [];
    
    for (let i = 1; i < lines.length; i++) {
        if (lines[i].trim()) {
            const values = lines[i].split(',').map(v => v.trim());
            const row = {};
            headers.forEach((header, index) => {
                row[header] = values[index] || '';
            });
            data.push(row);
        }
    }
    
    return data;
}

// Analysis functions
async function startAnalysis() {
    showSection('analysis-section');
    updateWorkflowStep('analysis', 'active');
    
    // Simulate analysis process
    setTimeout(() => {
        analyzeData();
    }, 2000);
}

function analyzeData() {
    if (!csvData || csvData.length === 0) return;
    
    // Analyze data structure
    const columns = Object.keys(csvData[0]);
    const numericColumns = columns.filter(col => 
        csvData.some(row => row[col] && !isNaN(parseFloat(row[col])))
    );
    const categoricalColumns = columns.filter(col => 
        !numericColumns.includes(col) && 
        new Set(csvData.map(row => row[col])).size < csvData.length * 0.5
    );
    
    // Detect business domain (simplified)
    const domainType = detectBusinessDomain(columns);
    
    analysisResults = {
        basic_stats: {
            rows: csvData.length,
            columns: columns.length
        },
        column_analysis: {
            numeric: numericColumns,
            categorical: categoricalColumns
        },
        domain: {
            type: domainType,
            confidence: 0.85,
            indicators: [`Found ${numericColumns.length} numeric columns`, `Detected ${categoricalColumns.length} categorical fields`]
        }
    };
    
    // Update UI
    document.getElementById('analysis-spinner').classList.add('hidden');
    document.getElementById('analysis-results').classList.remove('hidden');
    
    // Populate data metrics
    document.getElementById('data-metrics').innerHTML = `
        <div class="bg-blue-50 p-4 rounded-lg">
            <div class="text-2xl font-bold text-blue-800">${analysisResults.basic_stats.rows.toLocaleString()}</div>
            <div class="text-sm text-blue-600">Rows</div>
        </div>
        <div class="bg-green-50 p-4 rounded-lg">
            <div class="text-2xl font-bold text-green-800">${analysisResults.basic_stats.columns}</div>
            <div class="text-sm text-green-600">Columns</div>
        </div>
        <div class="bg-purple-50 p-4 rounded-lg">
            <div class="text-2xl font-bold text-purple-800">${numericColumns.length}</div>
            <div class="text-sm text-purple-600">Numeric Columns</div>
        </div>
    `;
    
    // Populate domain info
    document.getElementById('domain-info').innerHTML = `
        <div class="bg-indigo-50 p-4 rounded-lg">
            <div class="text-2xl font-bold text-indigo-800">${domainType.charAt(0).toUpperCase() + domainType.slice(1)}</div>
            <div class="text-sm text-indigo-600">Detected Domain</div>
        </div>
        <div class="bg-amber-50 p-4 rounded-lg">
            <div class="text-2xl font-bold text-amber-800">${(analysisResults.domain.confidence * 100).toFixed(0)}%</div>
            <div class="text-sm text-amber-600">Confidence</div>
        </div>
        <div class="text-sm text-gray-600">
            <strong>Key Indicators:</strong>
            <ul class="list-disc list-inside mt-2">
                ${analysisResults.domain.indicators.map(indicator => `<li>${indicator}</li>`).join('')}
            </ul>
        </div>
    `;
    
    document.getElementById('continueToPlanning').classList.remove('hidden');
    updateWorkflowStep('analysis', 'completed');
    interactionCount++;
    updateSessionInfo();
}

function detectBusinessDomain(columns) {
    const columnNames = columns.map(col => col.toLowerCase());
    
    // Simple domain detection logic
    const ecommerceKeywords = ['price', 'product', 'order', 'customer', 'sales', 'revenue'];
    const saasKeywords = ['user', 'subscription', 'trial', 'plan', 'feature'];
    const financeKeywords = ['amount', 'balance', 'transaction', 'account', 'payment'];
    
    const ecommerceScore = ecommerceKeywords.filter(keyword => 
        columnNames.some(col => col.includes(keyword))
    ).length;
    
    const saasScore = saasKeywords.filter(keyword => 
        columnNames.some(col => col.includes(keyword))
    ).length;
    
    const financeScore = financeKeywords.filter(keyword => 
        columnNames.some(col => col.includes(keyword))
    ).length;
    
    if (ecommerceScore >= saasScore && ecommerceScore >= financeScore) {
        return 'e-commerce';
    } else if (saasScore >= financeScore) {
        return 'saas';
    } else if (financeScore > 0) {
        return 'finance';
    } else {
        return 'general';
    }
}

// Planning functions
function showPlanning() {
    showSection('planning-section');
    updateWorkflowStep('planning', 'active');
}

function startChat() {
    showSection('chat-section');
    updateWorkflowStep('execution', 'active');
    
    // Populate chat context
    if (analysisResults) {
        document.getElementById('chat-context').innerHTML = `
            <strong>Domain:</strong> ${analysisResults.domain.type} (${(analysisResults.domain.confidence * 100).toFixed(0)}% confidence)<br>
            <strong>Data Shape:</strong> ${analysisResults.basic_stats.rows} rows × ${analysisResults.basic_stats.columns} columns
        `;
    }
}

function startVisualization() {
    showSection('visualization-section');
    updateWorkflowStep('execution', 'active');
    
    // Generate visualization suggestions
    setTimeout(() => {
        generateVisualizationSuggestions();
    }, 2000);
}

// Chat functions
function sendChatMessage() {
    const input = document.getElementById('chatInput');
    const question = input.value.trim();
    
    if (!question) return;
    
    // Add question to chat history
    const chatHistoryDiv = document.getElementById('chat-history');
    chatHistoryDiv.innerHTML += `
        <div class="mb-4">
            <div class="font-bold text-gray-800">You:</div>
            <div class="text-gray-600">${question}</div>
        </div>
    `;
    
    // Simulate AI response
    chatHistoryDiv.innerHTML += `
        <div class="mb-4">
            <div class="font-bold text-blue-600">AI:</div>
            <div class="text-gray-600 bg-blue-50 p-3 rounded">
                <i class="fas fa-spinner fa-spin mr-2"></i>Analyzing your question...
            </div>
        </div>
    `;
    
    // Scroll to bottom
    chatHistoryDiv.scrollTop = chatHistoryDiv.scrollHeight;
    
    // Clear input
    input.value = '';
    
    // Simulate response delay
    setTimeout(() => {
        const response = generateChatResponse(question);
        const responseElements = chatHistoryDiv.querySelectorAll('.bg-blue-50');
        const lastResponse = responseElements[responseElements.length - 1];
        lastResponse.innerHTML = response;
        
        chatHistory.push({ question, response });
        interactionCount++;
        updateSessionInfo();
    }, 2000);
}

function generateChatResponse(question) {
    if (!analysisResults) return "I need to analyze your data first before I can answer questions.";
    
    const domainType = analysisResults.domain.type;
    const rowCount = analysisResults.basic_stats.rows;
    const columnCount = analysisResults.basic_stats.columns;
    
    // Simple response generation based on question keywords
    const questionLower = question.toLowerCase();
    
    if (questionLower.includes('trend') || questionLower.includes('pattern')) {
        return `Based on your ${domainType} dataset with ${rowCount} records, I can see several interesting patterns. The data spans ${columnCount} different attributes, which suggests rich analytical possibilities. Key trends would be visible through time-series analysis of your numeric columns.`;
    } else if (questionLower.includes('insight') || questionLower.includes('analysis')) {
        return `Your ${domainType} data contains ${rowCount} records across ${columnCount} dimensions. Key insights include the distribution patterns in your categorical variables and correlations between numeric fields. The data quality appears good with a confidence level of ${(analysisResults.domain.confidence * 100).toFixed(0)}% for domain classification.`;
    } else if (questionLower.includes('recommend') || questionLower.includes('suggest')) {
        return `For your ${domainType} dataset, I recommend focusing on the ${analysisResults.column_analysis.numeric.length} numeric columns for quantitative analysis and the ${analysisResults.column_analysis.categorical.length} categorical columns for segmentation. Consider creating time-series visualizations if you have date columns.`;
    } else {
        return `That's an interesting question about your ${domainType} data. With ${rowCount} records and ${columnCount} columns, there are many analytical angles to explore. Could you be more specific about what aspect of the data you'd like to understand better?`;
    }
}

// Visualization functions
function generateVisualizationSuggestions() {
    document.getElementById('viz-loading').classList.add('hidden');
    document.getElementById('viz-suggestions').classList.remove('hidden');
    
    if (!analysisResults) return;
    
    const domainType = analysisResults.domain.type;
    document.getElementById('domain-type').textContent = domainType.charAt(0).toUpperCase() + domainType.slice(1);
    
    // Generate suggestions based on domain and data structure
    const suggestions = generateChartSuggestions(domainType, analysisResults);
    
    const chartSuggestionsDiv = document.getElementById('chart-suggestions');
    chartSuggestionsDiv.innerHTML = '';
    
    suggestions.forEach((suggestion, index) => {
        const chartCard = document.createElement('div');
        chartCard.className = 'chart-card bg-white rounded-xl p-6 shadow-lg border-2 border-gray-200 hover:border-blue-300 transition-all duration-200 cursor-pointer';
        chartCard.onclick = () => toggleChartSelection(index, chartCard);
        
        chartCard.innerHTML = `
            <div class="flex items-start justify-between mb-3">
                <h3 class="text-lg font-bold text-gray-800">${suggestion.title}</h3>
                <span class="bg-gradient-to-r from-blue-500 to-purple-600 text-white text-xs font-medium px-3 py-1 rounded-full">
                    ${suggestion.chart_type.charAt(0).toUpperCase() + suggestion.chart_type.slice(1)}
                </span>
            </div>
            <p class="text-gray-600 text-sm mb-3">${suggestion.description}</p>
            <div class="text-xs text-gray-500">
                <strong>Business Value:</strong> ${suggestion.domain_value}
            </div>
            <div class="hidden mt-3">
                <i class="fas fa-check-circle text-green-500 text-xl"></i>
            </div>
        `;
        
        chartSuggestionsDiv.appendChild(chartCard);
    });
    
    // Store suggestions globally
    window.chartSuggestions = suggestions;
}

function generateChartSuggestions(domainType, analysisResults) {
    const numericCols = analysisResults.column_analysis.numeric;
    const categoricalCols = analysisResults.column_analysis.categorical;
    
    const suggestions = [];
    
    if (domainType === 'e-commerce') {
        suggestions.push(
            {
                title: 'Revenue Trends Over Time',
                chart_type: 'line',
                description: 'Track sales performance and identify seasonal patterns',
                domain_value: 'Essential for understanding business growth and forecasting'
            },
            {
                title: 'Product Category Performance',
                chart_type: 'bar',
                description: 'Compare revenue across different product categories',
                domain_value: 'Helps identify top-performing product lines'
            },
            {
                title: 'Customer Segmentation',
                chart_type: 'pie',
                description: 'Visualize customer distribution by segments',
                domain_value: 'Supports targeted marketing strategies'
            }
        );
    } else if (domainType === 'saas') {
        suggestions.push(
            {
                title: 'User Growth Metrics',
                chart_type: 'line',
                description: 'Monitor user acquisition and retention trends',
                domain_value: 'Critical for understanding product adoption'
            },
            {
                title: 'Feature Usage Analysis',
                chart_type: 'bar',
                description: 'Compare usage across different product features',
                domain_value: 'Guides product development priorities'
            },
            {
                title: 'Subscription Plans Distribution',
                chart_type: 'pie',
                description: 'Analyze subscription tier preferences',
                domain_value: 'Informs pricing strategy decisions'
            }
        );
    } else {
        // General suggestions
        if (numericCols.length > 0) {
            suggestions.push({
                title: `${numericCols[0]} Distribution`,
                chart_type: 'histogram',
                description: `Analyze the distribution pattern of ${numericCols[0]} values`,
                domain_value: 'Understanding data distribution is crucial for analysis'
            });
        }
        
        if (categoricalCols.length > 0) {
            suggestions.push({
                title: `${categoricalCols[0]} Breakdown`,
                chart_type: 'pie',
                description: `Show the composition of different ${categoricalCols[0]} categories`,
                domain_value: 'Category analysis helps identify key segments'
            });
        }
        
        if (numericCols.length >= 2) {
            suggestions.push({
                title: `${numericCols[0]} vs ${numericCols[1]}`,
                chart_type: 'scatter',
                description: `Explore relationship between ${numericCols[0]} and ${numericCols[1]}`,
                domain_value: 'Correlation analysis reveals important relationships'
            });
        }
    }
    
    return suggestions;
}

function toggleChartSelection(index, cardElement) {
    const checkIcon = cardElement.querySelector('.fas.fa-check-circle').parentElement;
    
    if (selectedCharts.includes(index)) {
        // Deselect
        selectedCharts = selectedCharts.filter(i => i !== index);
        cardElement.classList.remove('selected');
        cardElement.classList.remove('border-blue-400', 'bg-blue-50');
        cardElement.classList.add('border-gray-200');
        checkIcon.classList.add('hidden');
    } else {
        // Select
        selectedCharts.push(index);
        cardElement.classList.add('selected');
        cardElement.classList.remove('border-gray-200');
        cardElement.classList.add('border-blue-400', 'bg-blue-50');
        checkIcon.classList.remove('hidden');
    }
    
    updateSelectedCount();
}

function updateSelectedCount() {
    const countElement = document.getElementById('selected-count');
    const generateButton = document.getElementById('generateDashboard');
    
    if (selectedCharts.length > 0) {
        countElement.textContent = `✅ ${selectedCharts.length} visualization${selectedCharts.length > 1 ? 's' : ''} selected`;
        generateButton.classList.remove('hidden');
    } else {
        countElement.textContent = '';
        generateButton.classList.add('hidden');
    }
}

function generateDashboard() {
    if (selectedCharts.length === 0) return;
    
    document.getElementById('dashboard').classList.remove('hidden');
    document.getElementById('custom-viz').classList.remove('hidden');
    
    const dashboardChartsDiv = document.getElementById('dashboard-charts');
    dashboardChartsDiv.innerHTML = '';
    
    selectedCharts.forEach((chartIndex, displayIndex) => {
        const suggestion = window.chartSuggestions[chartIndex];
        const chartDiv = document.createElement('div');
        chartDiv.className = 'bg-white rounded-lg shadow-lg p-4';
        chartDiv.innerHTML = `
            <h4 class="text-lg font-bold text-gray-800 mb-4">${suggestion.title}</h4>
            <div id="chart-${displayIndex}" style="height: 400px;"></div>
        `;
        dashboardChartsDiv.appendChild(chartDiv);
        
        // Generate sample chart
        setTimeout(() => {
            createSampleChart(`chart-${displayIndex}`, suggestion.chart_type, suggestion.title);
        }, 100);
    });
    
    interactionCount++;
    updateSessionInfo();
}

function createSampleChart(elementId, chartType, title) {
    if (!csvData || csvData.length === 0) return;
    
    const element = document.getElementById(elementId);
    if (!element) return;
    
    // Generate sample data based on chart type and actual CSV data
    let plotData, layout;
    
    if (chartType === 'bar') {
        const categories = ['Category A', 'Category B', 'Category C', 'Category D'];
        const values = [23, 45, 56, 78];
        
        plotData = [{
            x: categories,
            y: values,
            type: 'bar',
            marker: { color: '#3b82f6' }
        }];
        
        layout = {
            title: title,
            xaxis: { title: 'Categories' },
            yaxis: { title: 'Values' }
        };
    } else if (chartType === 'line') {
        const x = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
        const y = [10, 15, 13, 17, 21, 25];
        
        plotData = [{
            x: x,
            y: y,
            type: 'scatter',
            mode: 'lines+markers',
            line: { color: '#10b981' }
        }];
        
        layout = {
            title: title,
            xaxis: { title: 'Time' },
            yaxis: { title: 'Value' }
        };
    } else if (chartType === 'pie') {
        const labels = ['Segment 1', 'Segment 2', 'Segment 3', 'Segment 4'];
        const values = [30, 25, 25, 20];
        
        plotData = [{
            labels: labels,
            values: values,
            type: 'pie',
            textinfo: 'label+percent'
        }];
        
        layout = {
            title: title
        };
    } else if (chartType === 'scatter') {
        const x = Array.from({length: 20}, () => Math.random() * 100);
        const y = Array.from({length: 20}, () => Math.random() * 100);
        
        plotData = [{
            x: x,
            y: y,
            mode: 'markers',
            type: 'scatter',
            marker: { color: '#8b5cf6', size: 10 }
        }];
        
        layout = {
            title: title,
            xaxis: { title: 'X Axis' },
            yaxis: { title: 'Y Axis' }
        };
    } else {
        // Default histogram
        const values = Array.from({length: 100}, () => Math.random() * 100);
        
        plotData = [{
            x: values,
            type: 'histogram',
            marker: { color: '#f59e0b' }
        }];
        
        layout = {
            title: title,
            xaxis: { title: 'Value' },
            yaxis: { title: 'Frequency' }
        };
    }
    
    Plotly.newPlot(elementId, plotData, layout, {
        responsive: true,
        displayModeBar: false
    });
}

function createCustomVisualization() {
    const input = document.getElementById('customVizInput');
    const request = input.value.trim();
    
    if (!request) return;
    
    // Create a new chart container
    const dashboardChartsDiv = document.getElementById('dashboard-charts');
    const chartIndex = dashboardChartsDiv.children.length;
    
    const chartDiv = document.createElement('div');
    chartDiv.className = 'bg-white rounded-lg shadow-lg p-4';
    chartDiv.innerHTML = `
        <h4 class="text-lg font-bold text-gray-800 mb-4">Custom: ${request}</h4>
        <div id="custom-chart-${chartIndex}" style="height: 400px;"></div>
    `;
    dashboardChartsDiv.appendChild(chartDiv);
    
    // Generate chart based on request
    setTimeout(() => {
        createSampleChart(`custom-chart-${chartIndex}`, 'line', request);
    }, 100);
    
    input.value = '';
    interactionCount++;
    updateSessionInfo();
}

// Session management
function resetSession() {
    if (confirm('Are you sure you want to start over? This will clear all current data and progress.')) {
        // Reset all global variables
        csvData = null;
        analysisResults = null;
        selectedCharts = [];
        chatHistory = [];
        interactionCount = 0;
        
        // Reset UI
        showSection('upload-section');
        updateWorkflowStep('upload', 'pending');
        document.getElementById('csvFile').value = '';
        document.getElementById('analyzeBtn').classList.add('hidden');
        
        // Reset upload area
        document.querySelector('.upload-area').innerHTML = `
            <div class="mb-4">
                <i class="fas fa-cloud-upload-alt text-4xl text-gray-400 mb-4"></i>
            </div>
            <h3 class="text-xl font-semibold text-gray-700 mb-2">📁 Upload Your CSV File</h3>
            <p class="text-gray-500 mb-2">Drag and drop your CSV file here, or click to browse</p>
            <p class="text-sm text-gray-400">Supports CSV files up to 10MB</p>
        `;
        
        updateSessionInfo();
        document.getElementById('session-status').textContent = 'Ready';
    }
}

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    updateSessionInfo();
    
    // Add enter key listener for chat
    document.getElementById('chatInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendChatMessage();
        }
    });
    
    // Add enter key listener for custom viz
    document.getElementById('customVizInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            createCustomVisualization();
        }
    });
    
    // Set initial status
    document.getElementById('session-status').textContent = 'Ready';
});
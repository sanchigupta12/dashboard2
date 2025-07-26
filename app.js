// Global variables
let csvData = null;
let analysisResults = null;
let selectedCharts = [];
let chatHistory = [];
let interactionCount = 0;

// Configuration
const API_BASE_URL = 'http://localhost:5001';

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing app...');
    showUpload();
});

// Utility functions
function showSection(sectionId) {
    const sections = ['upload-section', 'analysis-section', 'planning-section', 'chat-section', 'visualization-section'];
    sections.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.classList.add('hidden');
        }
    });
    
    const targetElement = document.getElementById(sectionId);
    if (targetElement) {
        targetElement.classList.remove('hidden');
    }
}

function showUpload() {
    showSection('upload-section');
}

function showAnalysis() {
    showSection('analysis-section');
}

function showPlanning() {
    showSection('planning-section');
    
    // Update workflow progress
    updateWorkflowStep('planning', 'active');
}

function updateWorkflowStep(step, status) {
    console.log(`Updating workflow step: ${step} to ${status}`);
    
    const stepElement = document.querySelector(`[data-step="${step}"]`);
    if (!stepElement) return;
    
    const circle = stepElement.querySelector('.step-icon');
    
    if (status === 'completed') {
        stepElement.className = 'workflow-step completed p-4';
        circle.className = 'step-icon';
        circle.innerHTML = '<i class="fas fa-check"></i>';
        circle.style.backgroundColor = '#22c55e';
        circle.style.color = 'white';
    } else if (status === 'active') {
        stepElement.className = 'workflow-step active p-4';
        circle.className = 'step-icon';
        circle.style.backgroundColor = '#3b82f6';
        circle.style.color = 'white';
    } else if (status === 'pending') {
        stepElement.className = 'workflow-step pending p-4';
        circle.className = 'step-icon';
        circle.style.backgroundColor = '#e5e7eb';
        circle.style.color = '#6b7280';
    }
}

function updateSessionInfo() {
    const interactionElement = document.getElementById('interaction-count');
    if (interactionElement) {
        interactionElement.textContent = interactionCount;
    }
}

function resetApp() {
    csvData = null;
    analysisResults = null;
    selectedCharts = [];
    chatHistory = [];
    interactionCount = 0;
    showUpload();
    
    const fileInput = document.getElementById('csvFile');
    if (fileInput) fileInput.value = '';
    
    const analyzeBtn = document.getElementById('analyzeBtn');
    if (analyzeBtn) analyzeBtn.classList.add('hidden');
}

// File upload handling
function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    if (!file.name.endsWith('.csv')) {
        alert('Please select a CSV file');
        return;
    }
    
    if (file.size > 10 * 1024 * 1024) {
        alert('File size must be less than 10MB');
        return;
    }
    
    const reader = new FileReader();
    reader.onload = function(e) {
        const csvContent = e.target.result;
        csvData = parseCSV(csvContent);
        
        // Update UI
        const uploadArea = document.querySelector('.upload-area');
        if (uploadArea) {
            uploadArea.innerHTML = `
                <div class="mb-6">
                    <i class="fas fa-check-circle text-3xl text-green-600"></i>
                </div>
                <h3 class="text-lg font-semibold text-gray-900 mb-2">File Uploaded Successfully</h3>
                <p class="text-gray-500 mb-2">${file.name}</p>
                <div class="flex items-center justify-center text-sm text-gray-400 mt-4">
                    <i class="fas fa-check-circle mr-2 text-green-500"></i>
                    <span>${csvData.length} rows × ${csvData[0] ? Object.keys(csvData[0]).length : 0} columns</span>
                </div>
            `;
        }
        
        const analyzeBtn = document.getElementById('analyzeBtn');
        if (analyzeBtn) analyzeBtn.classList.remove('hidden');
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
function startAnalysis() {
    if (!csvData) {
        alert('Please upload a CSV file first');
        return;
    }
    
    console.log('Starting analysis...');
    showSection('analysis-section');
    
    // Hide results and show spinner
    const spinner = document.getElementById('analysis-spinner');
    const results = document.getElementById('analysis-results');
    
    if (spinner) spinner.classList.remove('hidden');
    if (results) results.classList.add('hidden');
    
    // Simulate analysis process
    setTimeout(() => {
        performAnalysis();
    }, 1500);
}

function performAnalysis() {
    if (!csvData || csvData.length === 0) return;
    
    // Basic analysis
    const columns = Object.keys(csvData[0]);
    const numericColumns = columns.filter(col => 
        csvData.some(row => row[col] && !isNaN(parseFloat(row[col])))
    );
    
    const domainType = detectBusinessDomain(columns);
    
    analysisResults = {
        basic_stats: {
            rows: csvData.length,
            columns: columns.length
        },
        domain: {
            type: domainType,
            confidence: 0.85
        },
        columns: columns,
        numeric_columns: numericColumns,
        sample_data: csvData.slice(0, 5) // Store sample for analysis
    };
    
    // Update UI
    const spinner = document.getElementById('analysis-spinner');
    const results = document.getElementById('analysis-results');
    
    if (spinner) spinner.classList.add('hidden');
    if (results) results.classList.remove('hidden');
    
    // Update summary cards
    const rowsCount = document.getElementById('rows-count');
    const columnsCount = document.getElementById('columns-count');
    const domainTypeElement = document.getElementById('domain-type');
    
    if (rowsCount) rowsCount.textContent = analysisResults.basic_stats.rows.toLocaleString();
    if (columnsCount) columnsCount.textContent = analysisResults.basic_stats.columns;
    if (domainTypeElement) domainTypeElement.textContent = analysisResults.domain.type;
    
    // Update workflow progress
    updateWorkflowStep('upload', 'completed');
    updateWorkflowStep('analysis', 'completed');
    
    // Show continue button
    const continueBtn = document.getElementById('continueToPlanning');
    if (continueBtn) continueBtn.classList.remove('hidden');
    
    console.log('Analysis completed successfully');
}

function detectBusinessDomain(columns) {
    const columnNames = columns.map(col => col.toLowerCase());
    
    const restaurantKeywords = ['restaurant', 'menu', 'food', 'order', 'meal', 'dish', 'cuisine'];
    const ecommerceKeywords = ['price', 'product', 'order', 'customer', 'sales', 'revenue'];
    const saasKeywords = ['user', 'subscription', 'trial', 'plan', 'feature'];
    const financeKeywords = ['amount', 'balance', 'transaction', 'account', 'payment'];
    
    const restaurantScore = restaurantKeywords.filter(keyword => 
        columnNames.some(col => col.includes(keyword))
    ).length;
    
    const ecommerceScore = ecommerceKeywords.filter(keyword => 
        columnNames.some(col => col.includes(keyword))
    ).length;
    
    const saasScore = saasKeywords.filter(keyword => 
        columnNames.some(col => col.includes(keyword))
    ).length;
    
    const financeScore = financeKeywords.filter(keyword => 
        columnNames.some(col => col.includes(keyword))
    ).length;
    
    if (restaurantScore > 0) {
        return 'Restaurant';
    } else if (ecommerceScore >= saasScore && ecommerceScore >= financeScore) {
        return 'E-commerce';
    } else if (saasScore >= financeScore) {
        return 'SaaS';
    } else if (financeScore > 0) {
        return 'Finance';
    } else {
        return 'General';
    }
}

// Planning functions
function startChat() {
    showSection('chat-section');
    
    // Update workflow progress
    updateWorkflowStep('planning', 'completed');
    updateWorkflowStep('execution', 'active');
    
    // Set up chat context
    if (analysisResults) {
        const chatContext = document.getElementById('chat-context');
        if (chatContext) {
            chatContext.innerHTML = `
                <strong>Domain:</strong> ${analysisResults.domain.type} (${(analysisResults.domain.confidence * 100).toFixed(0)}% confidence)<br>
                <strong>Data Shape:</strong> ${analysisResults.basic_stats.rows} rows × ${analysisResults.basic_stats.columns} columns<br>
                <strong>Key Columns:</strong> ${analysisResults.columns.slice(0, 5).join(', ')}${analysisResults.columns.length > 5 ? '...' : ''}
            `;
        }
    }
}

function startVisualization() {
    showSection('visualization-section');
    
    // Update workflow progress
    updateWorkflowStep('planning', 'completed');
    updateWorkflowStep('execution', 'active');
    
    // Show loading, hide other elements
    const loading = document.getElementById('viz-loading');
    const suggestions = document.getElementById('viz-suggestions');
    
    if (loading) loading.classList.remove('hidden');
    if (suggestions) suggestions.classList.add('hidden');
    
    // Generate suggestions after delay
    setTimeout(() => {
        generateVisualizationSuggestions();
        if (loading) loading.classList.add('hidden');
        if (suggestions) suggestions.classList.remove('hidden');
        
        // Show custom visualization section
        const customViz = document.getElementById('custom-viz');
        if (customViz) customViz.classList.remove('hidden');
    }, 2000);
}

// Chat functions
function sendChatMessage() {
    const input = document.getElementById('chatInput');
    const question = input.value.trim();
    
    if (!question) return;
    
    // Add to chat history
    addChatMessage('user', question);
    input.value = '';
    
    // Simulate AI response
    setTimeout(() => {
        const response = generateChatResponse(question);
        addChatMessage('assistant', response);
    }, 1000);
}

function addChatMessage(role, message) {
    const chatHistory = document.getElementById('chat-history');
    if (!chatHistory) return;
    
    // Clear initial message if this is the first chat
    if (chatHistory.children.length === 1 && chatHistory.children[0].textContent.includes('Ask your first question')) {
        chatHistory.innerHTML = '';
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `mb-4 ${role === 'user' ? 'text-right' : 'text-left'}`;
    
    messageDiv.innerHTML = `
        <div class="inline-block max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
            role === 'user' 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-200 text-gray-800'
        }">
            ${message}
        </div>
    `;
    
    chatHistory.appendChild(messageDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

function generateChatResponse(question) {
    if (!analysisResults) {
        return "Please analyze your data first before asking questions.";
    }
    
    const questionLower = question.toLowerCase();
    const domain = analysisResults.domain.type;
    const rows = analysisResults.basic_stats.rows;
    const cols = analysisResults.basic_stats.columns;
    const columns = analysisResults.columns;
    const numericCols = analysisResults.numeric_columns;
    
    // Senior Data Analyst responses based on question context
    if (questionLower.includes('trend') || questionLower.includes('pattern')) {
        return `As your Senior Data Analyst, I can see several interesting trends in your ${domain} dataset. With ${rows.toLocaleString()} records, I'd recommend focusing on time-based analysis using columns like ${numericCols.slice(0,2).join(' and ')}. The data shows ${cols} dimensions we can explore for pattern recognition.`;
    }
    
    if (questionLower.includes('revenue') || questionLower.includes('sales') || questionLower.includes('money')) {
        return `From a financial perspective, your ${domain} data contains ${rows.toLocaleString()} transactions. I'd analyze the revenue streams by examining ${numericCols.length > 0 ? numericCols[0] : 'financial columns'} and correlating with categorical data. This could reveal peak performance periods and growth opportunities.`;
    }
    
    if (questionLower.includes('customer') || questionLower.includes('user')) {
        return `Looking at customer behavior in your ${domain} dataset, I see ${rows.toLocaleString()} data points. Customer segmentation analysis would be valuable here. I'd segment by ${columns.slice(1,3).join(' and ')} to identify high-value customer groups and retention patterns.`;
    }
    
    if (questionLower.includes('recommend') || questionLower.includes('suggest')) {
        return `Based on my analysis of your ${domain} data, I recommend starting with: 1) Time-series analysis of your key metrics, 2) Customer segmentation using ${columns.slice(0,2).join(' and ')}, 3) Performance correlation analysis. With ${rows.toLocaleString()} records, we have strong statistical power for these analyses.`;
    }
    
    if (questionLower.includes('insight') || questionLower.includes('finding')) {
        return `Here are my key insights from your ${domain} dataset: The ${rows.toLocaleString()} records show ${numericCols.length} quantitative measures we can analyze. I notice ${columns.length} different dimensions - this suggests opportunities for multi-dimensional analysis and cross-correlation studies.`;
    }
    
    if (questionLower.includes('performance') || questionLower.includes('metric')) {
        return `From a performance standpoint, your ${domain} data with ${rows.toLocaleString()} records offers rich analytics potential. I'd focus on KPI tracking using ${numericCols.slice(0,2).join(' and ')}, benchmark analysis, and performance trending over time periods.`;
    }
    
    // Default senior analyst response
    return `As your Senior Data Analyst, I've examined your ${domain} dataset containing ${rows.toLocaleString()} records across ${cols} fields. Based on the data structure, I see strong potential for ${numericCols.length > 0 ? 'quantitative analysis' : 'categorical analysis'}. What specific business question would you like me to investigate further?`;
}

// Visualization functions
function generateVisualizationSuggestions() {
    const chartSuggestions = document.getElementById('chart-suggestions');
    if (!chartSuggestions) return;
    
    // Generate domain-specific chart suggestions
    const domain = analysisResults ? analysisResults.domain.type : 'General';
    const chartTypes = getChartSuggestionsForDomain(domain);
    
    chartSuggestions.innerHTML = chartTypes.map((chart, index) => `
        <div class="bg-white rounded-xl p-6 shadow-sm border hover:shadow-md transition-all duration-200 cursor-pointer chart-option" 
             data-chart-type="${chart.type}" onclick="selectChart('${chart.type}', this)">
            <div class="flex items-start space-x-4">
                <div class="w-12 h-12 bg-${chart.color}-100 rounded-lg flex items-center justify-center flex-shrink-0">
                    <i class="fas fa-${chart.icon} text-xl text-${chart.color}-600"></i>
                </div>
                <div class="flex-1">
                    <h4 class="text-lg font-semibold text-gray-900 mb-2">${chart.title}</h4>
                    <p class="text-gray-600 text-sm mb-3">${chart.description}</p>
                    <div class="flex items-center justify-between">
                        <span class="text-xs text-gray-500">${chart.recommended ? 'Recommended' : 'Optional'}</span>
                        <div class="w-4 h-4 border-2 border-gray-300 rounded checkbox"></div>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
    
    // Show generate button
    const generateBtn = document.getElementById('generateDashboard');
    if (generateBtn) generateBtn.classList.remove('hidden');
}

function getChartSuggestionsForDomain(domain) {
    const suggestions = {
        'Restaurant': [
            { type: 'revenue-trend', title: 'Revenue Trends', description: 'Track daily/weekly revenue patterns', icon: 'chart-line', color: 'blue', recommended: true },
            { type: 'menu-performance', title: 'Menu Item Performance', description: 'Best and worst selling dishes', icon: 'utensils', color: 'green', recommended: true },
            { type: 'customer-peak-hours', title: 'Peak Hours Analysis', description: 'Busiest times and customer flow', icon: 'clock', color: 'purple', recommended: true },
            { type: 'order-size-dist', title: 'Order Size Distribution', description: 'Average order values and patterns', icon: 'chart-pie', color: 'orange', recommended: false },
            { type: 'customer-satisfaction', title: 'Rating Analysis', description: 'Customer satisfaction trends', icon: 'star', color: 'yellow', recommended: false }
        ],
        'E-commerce': [
            { type: 'sales-funnel', title: 'Sales Funnel', description: 'Conversion rates through purchase stages', icon: 'funnel-dollar', color: 'blue', recommended: true },
            { type: 'product-performance', title: 'Product Performance', description: 'Top selling products and categories', icon: 'box', color: 'green', recommended: true },
            { type: 'customer-segments', title: 'Customer Segmentation', description: 'User behavior and purchase patterns', icon: 'users', color: 'purple', recommended: false }
        ],
        'General': [
            { type: 'data-overview', title: 'Data Overview', description: 'General statistics and distributions', icon: 'chart-bar', color: 'blue', recommended: true },
            { type: 'trend-analysis', title: 'Trend Analysis', description: 'Time-based patterns in your data', icon: 'chart-line', color: 'green', recommended: true },
            { type: 'correlation-matrix', title: 'Data Relationships', description: 'How different variables relate to each other', icon: 'project-diagram', color: 'purple', recommended: false }
        ]
    };
    
    return suggestions[domain] || suggestions['General'];
}

function selectChart(chartType, element) {
    const checkbox = element.querySelector('.checkbox');
    const isSelected = element.classList.contains('selected');
    
    if (isSelected) {
        element.classList.remove('selected');
        checkbox.innerHTML = '';
        checkbox.className = 'w-4 h-4 border-2 border-gray-300 rounded checkbox';
    } else {
        element.classList.add('selected');
        checkbox.innerHTML = '<i class="fas fa-check text-white text-xs"></i>';
        checkbox.className = 'w-4 h-4 bg-blue-600 border-2 border-blue-600 rounded checkbox flex items-center justify-center';
    }
    
    updateSelectedCount();
}

function updateSelectedCount() {
    const selectedElements = document.querySelectorAll('.chart-option.selected');
    const totalSelectedElement = document.getElementById('total-selected');
    if (totalSelectedElement) {
        totalSelectedElement.textContent = `${selectedElements.length} Selected`;
    }
}

function generateDashboard() {
    const selectedCharts = document.querySelectorAll('.chart-option.selected');
    if (selectedCharts.length === 0) {
        alert('Please select at least one chart to generate your dashboard.');
        return;
    }
    
    // Hide suggestions and show dashboard
    document.getElementById('viz-suggestions').classList.add('hidden');
    document.getElementById('dashboard').classList.remove('hidden');
    
    // Generate sample dashboard content
    generateDashboardContent(selectedCharts);
}

function generateDashboardContent(selectedCharts) {
    const dashboardCharts = document.getElementById('dashboard-charts');
    const keyInsights = document.getElementById('key-insights');
    
    if (dashboardCharts) {
        dashboardCharts.innerHTML = Array.from(selectedCharts).map((chart, index) => {
            const chartType = chart.dataset.chartType;
            const chartTitle = chart.querySelector('h4').textContent;
            
            return `
                <div class="bg-white rounded-lg p-6 shadow-sm border">
                    <div class="flex items-center justify-between mb-4">
                        <h3 class="text-lg font-semibold text-gray-900">${chartTitle}</h3>
                        <div class="flex items-center space-x-2">
                            <button class="text-gray-400 hover:text-gray-600">
                                <i class="fas fa-expand-alt"></i>
                            </button>
                            <button class="text-gray-400 hover:text-gray-600">
                                <i class="fas fa-download"></i>
                            </button>
                        </div>
                    </div>
                    <div class="h-64 bg-gray-50 rounded-lg p-4">
                        ${generateChartVisualization(chartType, index)}
                    </div>
                </div>
            `;
        }).join('');
    }
    
    if (keyInsights) {
        keyInsights.innerHTML = `
            <div class="text-center">
                <div class="text-2xl font-bold text-blue-800">${analysisResults ? analysisResults.basic_stats.rows.toLocaleString() : '12,500'}</div>
                <div class="text-sm text-blue-600">Total Records</div>
            </div>
            <div class="text-center">
                <div class="text-2xl font-bold text-green-800">${analysisResults ? analysisResults.basic_stats.columns : '15'}</div>
                <div class="text-sm text-green-600">Data Fields</div>
            </div>
            <div class="text-center">
                <div class="text-2xl font-bold text-purple-800">${analysisResults ? (analysisResults.domain.confidence * 100).toFixed(0) : '85'}%</div>
                <div class="text-sm text-purple-600">Analysis Confidence</div>
            </div>
        `;
    }
    
    // Update dashboard info
    const dashboardInfo = document.getElementById('dashboard-info');
    if (dashboardInfo) {
        dashboardInfo.textContent = `${analysisResults ? analysisResults.basic_stats.rows.toLocaleString() : '12,500'} rows processed`;
    }
    
    const generatedCount = document.getElementById('generated-count');
    if (generatedCount) {
        generatedCount.textContent = `Generated ${selectedCharts.length} visualizations!`;
    }
}

function createCustomVisualization() {
    const input = document.getElementById('customVizInput');
    const request = input.value.trim();
    
    if (!request) {
        alert('Please describe what you\'d like to visualize.');
        return;
    }
    
    // Generate AI response for custom chart request
    const response = generateCustomChartResponse(request);
    
    // Add to custom visualization area if dashboard is visible
    const dashboard = document.getElementById('dashboard');
    if (!dashboard.classList.contains('hidden')) {
        const dashboardCharts = document.getElementById('dashboard-charts');
        if (dashboardCharts) {
            const customChart = document.createElement('div');
            customChart.className = 'bg-white rounded-lg p-6 shadow-sm border border-purple-200';
            customChart.innerHTML = `
                <div class="flex items-center justify-between mb-4">
                    <h3 class="text-lg font-semibold text-gray-900">Custom: ${request}</h3>
                    <span class="text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded">AI Generated</span>
                </div>
                <div class="h-64 bg-gradient-to-br from-purple-50 to-blue-50 rounded-lg p-4">
                    ${generateCustomChartVisualization(request)}
                </div>
                <div class="mt-4 p-3 bg-blue-50 rounded-lg">
                    <p class="text-sm text-blue-800"><strong>AI Analyst:</strong> ${response}</p>
                </div>
            `;
            
            dashboardCharts.appendChild(customChart);
        }
    } else {
        // Show response in the custom viz area
        alert(`AI Analyst Response: ${response}`);
    }
    
    input.value = '';
}

function generateCustomChartResponse(request) {
    const domain = analysisResults ? analysisResults.domain.type : 'your business';
    const columns = analysisResults ? analysisResults.columns : [];
    const rows = analysisResults ? analysisResults.basic_stats.rows : 0;
    
    const requestLower = request.toLowerCase();
    
    if (requestLower.includes('correlation') || requestLower.includes('relationship')) {
        return `I'll create a correlation analysis for your ${domain} data. With ${rows.toLocaleString()} records, we can examine relationships between ${columns.slice(0,3).join(', ')} to identify patterns and dependencies.`;
    }
    
    if (requestLower.includes('time') || requestLower.includes('trend') || requestLower.includes('over time')) {
        return `Perfect! Time series analysis is crucial for ${domain} businesses. I'll create a temporal visualization showing trends across your ${rows.toLocaleString()} data points to reveal seasonal patterns and growth trajectories.`;
    }
    
    if (requestLower.includes('distribution') || requestLower.includes('breakdown')) {
        return `Distribution analysis coming up! For your ${domain} dataset, I'll break down the data by key categories. This will help identify the most significant segments in your ${rows.toLocaleString()} records.`;
    }
    
    return `Excellent request! I'm creating a custom ${domain} visualization based on "${request}". This analysis will leverage your ${rows.toLocaleString()} data points to provide actionable insights for your business strategy.`;
}

function generateCustomChartVisualization(request) {
    return `
        <div class="h-full flex items-center justify-center">
            <div class="text-center">
                <div class="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <i class="fas fa-chart-line text-2xl text-purple-600"></i>
                </div>
                <h4 class="font-semibold text-gray-800 mb-2">Custom Analysis: "${request}"</h4>
                <div class="space-y-2 text-sm text-gray-600">
                    <div class="flex justify-between"><span>Data Points:</span><span>${analysisResults ? analysisResults.basic_stats.rows.toLocaleString() : '12,500'}</span></div>
                    <div class="flex justify-between"><span>Analysis Type:</span><span>Custom Request</span></div>
                    <div class="flex justify-between"><span>Confidence:</span><span>95%</span></div>
                </div>
            </div>
        </div>
    `;
}

function generateChartVisualization(chartType, index) {
    const colors = ['blue', 'green', 'purple', 'orange', 'red'];
    const color = colors[index % colors.length];
    const rows = analysisResults ? analysisResults.basic_stats.rows : 12500;
    
    return `
        <div class="h-full flex flex-col">
            <div class="flex-1 flex items-center justify-center">
                <div class="text-center">
                    <div class="w-12 h-12 bg-${color}-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                        <i class="fas fa-chart-${index % 2 === 0 ? 'line' : 'bar'} text-xl text-${color}-600"></i>
                    </div>
                    <div class="space-y-1">
                        <div class="flex justify-center space-x-4 text-xs text-gray-500">
                            <span>Data: ${rows.toLocaleString()} points</span>
                            <span>Type: Interactive</span>
                        </div>
                        <div class="w-32 h-1 bg-${color}-200 rounded-full mx-auto">
                            <div class="w-3/4 h-1 bg-${color}-600 rounded-full"></div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="mt-auto">
                <div class="grid grid-cols-3 gap-2 text-xs text-center">
                    <div class="bg-${color}-50 rounded p-1">
                        <div class="font-semibold text-${color}-800">${Math.floor(Math.random() * 100)}%</div>
                        <div class="text-${color}-600">Growth</div>
                    </div>
                    <div class="bg-${color}-50 rounded p-1">
                        <div class="font-semibold text-${color}-800">${Math.floor(Math.random() * 50 + 50)}</div>
                        <div class="text-${color}-600">Score</div>
                    </div>
                    <div class="bg-${color}-50 rounded p-1">
                        <div class="font-semibold text-${color}-800">${Math.floor(Math.random() * 10 + 5)}k</div>
                        <div class="text-${color}-600">Volume</div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// Event handlers for enter key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
        const activeElement = document.activeElement;
        if (activeElement && activeElement.id === 'chatInput') {
            event.preventDefault();
            sendChatMessage();
        }
    }
});

console.log('App script loaded successfully');
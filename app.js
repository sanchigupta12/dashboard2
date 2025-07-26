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
}

function updateWorkflowStep(step, status) {
    console.log(`Updating workflow step: ${step} to ${status}`);
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
        }
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
    
    // Set up chat context
    if (analysisResults) {
        const chatContext = document.getElementById('chat-context');
        if (chatContext) {
            chatContext.innerHTML = `
                <strong>Domain:</strong> ${analysisResults.domain.type} (${(analysisResults.domain.confidence * 100).toFixed(0)}% confidence)<br>
                <strong>Data Shape:</strong> ${analysisResults.basic_stats.rows} rows × ${analysisResults.basic_stats.columns} columns
            `;
        }
    }
}

function startVisualization() {
    showSection('visualization-section');
    
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
    
    const responses = [
        `Based on your ${analysisResults.domain.type} data with ${analysisResults.basic_stats.rows} rows, here's what I found: The dataset shows interesting patterns that could help with business decisions.`,
        `Looking at your ${analysisResults.basic_stats.columns} columns of data, I can see several key insights. The ${analysisResults.domain.type} domain suggests specific analysis opportunities.`,
        `Your dataset contains ${analysisResults.basic_stats.rows} records across ${analysisResults.basic_stats.columns} fields. For ${analysisResults.domain.type} businesses, this data can reveal important trends.`
    ];
    
    return responses[Math.floor(Math.random() * responses.length)];
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
                    <div class="h-64 bg-gray-50 rounded-lg flex items-center justify-center">
                        <div class="text-center">
                            <i class="fas fa-chart-${index % 2 === 0 ? 'line' : 'bar'} text-4xl text-gray-400 mb-4"></i>
                            <p class="text-gray-500">Interactive ${chartTitle.toLowerCase()} visualization</p>
                            <p class="text-sm text-gray-400 mt-2">Based on ${analysisResults ? analysisResults.basic_stats.rows : 'your'} data points</p>
                        </div>
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
    
    // Add custom visualization request
    const dashboardCharts = document.getElementById('dashboard-charts');
    if (dashboardCharts) {
        const customChart = document.createElement('div');
        customChart.className = 'bg-white rounded-lg p-6 shadow-sm border border-purple-200';
        customChart.innerHTML = `
            <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-semibold text-gray-900">Custom Visualization</h3>
                <span class="text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded">AI Generated</span>
            </div>
            <div class="h-64 bg-gradient-to-br from-purple-50 to-blue-50 rounded-lg flex items-center justify-center">
                <div class="text-center">
                    <i class="fas fa-magic text-4xl text-purple-500 mb-4"></i>
                    <p class="text-gray-700 font-medium">"${request}"</p>
                    <p class="text-sm text-gray-500 mt-2">Custom visualization based on your request</p>
                </div>
            </div>
        `;
        
        dashboardCharts.appendChild(customChart);
    }
    
    input.value = '';
    alert('Custom visualization added to your dashboard!');
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
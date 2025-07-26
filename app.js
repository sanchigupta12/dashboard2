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
}

function startVisualization() {
    showSection('visualization-section');
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
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;
    
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
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
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
    const suggestions = document.getElementById('viz-suggestions');
    if (!suggestions) return;
    
    suggestions.innerHTML = `
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="bg-white p-6 rounded-lg border cursor-pointer hover:shadow-md">
                <h4 class="font-semibold mb-2">Sales Trend Chart</h4>
                <p class="text-gray-600 text-sm">Track performance over time</p>
            </div>
            <div class="bg-white p-6 rounded-lg border cursor-pointer hover:shadow-md">
                <h4 class="font-semibold mb-2">Category Distribution</h4>
                <p class="text-gray-600 text-sm">See data breakdown by category</p>
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
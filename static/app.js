/**
 * DU Admission Analyzer - Frontend Application
 * Modern, responsive web interface with interactive visualizations
 */

class DUAnalyzerApp {
    constructor() {
        this.currentView = 'dashboard';
        this.processId = null;
        this.charts = {};
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadDashboard();
        this.loadFiles();
        this.setupRealTimeUpdates();
    }

    setupEventListeners() {
        // File upload
        document.addEventListener('change', (e) => {
            if (e.target.id === 'file-upload') {
                this.handleFileUpload(e.target.files[0]);
            }
        });

        // Navigation
        document.addEventListener('click', (e) => {
            if (e.target.dataset.view) {
                this.switchView(e.target.dataset.view);
            }
            if (e.target.dataset.action) {
                this.handleAction(e.target.dataset.action, e.target.dataset);
            }
        });

        // Responsive navigation
        document.addEventListener('click', (e) => {
            if (e.target.id === 'mobile-menu-button') {
                this.toggleMobileMenu();
            }
        });
    }

    async loadFiles() {
        try {
            const response = await fetch('/api/files');
            const data = await response.json();
            this.renderFilesList(data);
        } catch (error) {
            console.error('Error loading files:', error);
        }
    }

    async handleFileUpload(file) {
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        try {
            this.showProcessingModal('Uploading file...');
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            this.processId = result.process_id;
            this.startPolling();
        } catch (error) {
            this.hideProcessingModal();
            this.showError('Upload failed: ' + error.message);
        }
    }

    async processExistingFile(filename) {
        try {
            this.showProcessingModal('Starting processing...');
            const response = await fetch(`/api/process/${filename}`, {
                method: 'POST'
            });

            const result = await response.json();
            this.processId = result.process_id;
            this.startPolling();
        } catch (error) {
            this.hideProcessingModal();
            this.showError('Processing failed: ' + error.message);
        }
    }

    startPolling() {
        const poll = setInterval(async () => {
            try {
                const response = await fetch(`/api/status/${this.processId}`);
                const status = await response.json();

                this.updateProcessingModal(status);

                if (status.status === 'completed') {
                    clearInterval(poll);
                    this.hideProcessingModal();
                    this.loadAnalytics();
                    this.loadFiles();
                    this.showSuccess('Processing completed successfully!');
                } else if (status.status === 'error') {
                    clearInterval(poll);
                    this.hideProcessingModal();
                    this.showError('Processing failed: ' + status.message);
                }
            } catch (error) {
                clearInterval(poll);
                this.hideProcessingModal();
                this.showError('Status check failed: ' + error.message);
            }
        }, 2000);
    }

    async loadAnalytics() {
        try {
            const response = await fetch('/api/chart-data');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            this.currentData = data; // Store current data
            
            // Also fetch raw data for filtering
            try {
                const rawResponse = await fetch('/api/raw-data');
                if (rawResponse.ok) {
                    this.globalData = await rawResponse.json();
                    console.log(`Loaded ${this.globalData.length} records for filtering`);
                }
            } catch (error) {
                console.warn('Could not load raw data for filtering:', error);
            }
            
            this.renderAnalytics(data);
            
            // Auto-run all charts with animation
            this.autoRunAllCharts();
            
        } catch (error) {
            console.error('Error loading analytics:', error);
            // Show error message if charts can't load
            document.getElementById('charts-container').innerHTML = `
                <div class="text-center p-8">
                    <div class="text-red-500 text-lg mb-4">
                        <i class="fas fa-exclamation-triangle mr-2"></i>
                        Unable to load chart data
                    </div>
                    <p class="text-gray-600">Please try refreshing the page or upload a new PDF file.</p>
                </div>
            `;
        }
    }

    autoRunAllCharts() {
        // Auto-run all charts with staggered animation
        const chartTypes = ['category', 'college', 'program', 'college-vs-seats', 
                          'program-distribution', 'category-comparison', 'seats-trend', 'category-overview'];
        
        chartTypes.forEach((chartType, index) => {
            setTimeout(() => {
                // Find the play button for this chart type
                const playBtns = document.querySelectorAll('.play-btn');
                const chartBtn = Array.from(playBtns).find(btn => {
                    return btn.getAttribute('onclick')?.includes(chartType);
                });
                
                if (chartBtn) {
                    chartBtn.classList.add('playing');
                    chartBtn.innerHTML = '<i class="fas fa-cog fa-spin text-blue-500"></i>';
                    
                    setTimeout(() => {
                        chartBtn.classList.remove('playing');
                        chartBtn.innerHTML = '<i class="fas fa-check text-green-500"></i>';
                        
                        // Change back to play icon after 1 second
                        setTimeout(() => {
                            chartBtn.innerHTML = '<i class="fas fa-play text-green-500"></i>';
                        }, 1000);
                    }, 1500);
                }
            }, index * 200); // Stagger by 200ms
        });
        
        // Auto-populate filter options and refresh data table
        setTimeout(() => {
            this.populateFilterOptions();
            this.refreshDataTable();
        }, chartTypes.length * 200 + 500);
    }

    loadDashboard() {
        document.getElementById('app').innerHTML = this.getDashboardHTML();
        this.setupCharts();
    }

    getDashboardHTML() {
        return `
            <!-- Navigation -->
            <nav class="gradient-bg shadow-lg">
                <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div class="flex justify-between h-16">
                        <div class="flex items-center">
                            <div class="flex-shrink-0">
                                <h1 class="text-white text-xl font-bold">
                                    <i class="fas fa-graduation-cap mr-2"></i>
                                    DU Admission Analyzer
                                </h1>
                            </div>
                            <div class="hidden md:ml-6 md:flex md:space-x-8">
                                <a href="#" data-view="dashboard" class="text-white hover:text-gray-200 px-3 py-2 text-sm font-medium">
                                    <i class="fas fa-chart-line mr-1"></i> Dashboard
                                </a>
                                <a href="#" data-view="search" class="text-white hover:text-gray-200 px-3 py-2 text-sm font-medium">
                                    <i class="fas fa-search mr-1"></i> Advanced Search
                                </a>
                                <a href="#" data-view="files" class="text-white hover:text-gray-200 px-3 py-2 text-sm font-medium">
                                    <i class="fas fa-folder mr-1"></i> Files
                                </a>
                                <a href="#" data-view="analytics" class="text-white hover:text-gray-200 px-3 py-2 text-sm font-medium">
                                    <i class="fas fa-chart-bar mr-1"></i> Analytics
                                </a>
                            </div>
                        </div>
                        <div class="md:hidden">
                            <button id="mobile-menu-button" class="text-white hover:text-gray-200">
                                <i class="fas fa-bars"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </nav>

            <!-- Main Content -->
            <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
                <!-- Upload Section -->
                <div class="mb-8">
                    <div class="bg-white rounded-lg shadow-lg p-6 card-hover">
                        <h2 class="text-2xl font-bold text-gray-900 mb-4">
                            <i class="fas fa-upload mr-2 text-blue-600"></i>
                            Upload & Process PDF
                        </h2>
                        <div class="flex flex-col md:flex-row gap-4">
                            <div class="flex-1">
                                <div class="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-400 transition-colors">
                                    <input type="file" id="file-upload" accept=".pdf" class="hidden">
                                    <label for="file-upload" class="cursor-pointer">
                                        <i class="fas fa-cloud-upload-alt text-4xl text-gray-400 mb-4"></i>
                                        <p class="text-lg text-gray-600">Click to upload PDF file</p>
                                        <p class="text-sm text-gray-400">or drag and drop</p>
                                    </label>
                                </div>
                            </div>
                            <div class="flex-1">
                                <h3 class="text-lg font-semibold mb-2">Available PDFs</h3>
                                <div id="available-pdfs" class="space-y-2 max-h-40 overflow-y-auto">
                                    <!-- PDFs will be loaded here -->
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Summary Cards -->
                <div id="summary-cards" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                    <!-- Cards will be loaded here -->
                </div>

                <!-- Advanced Charts Section -->
                <div class="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6 mb-8">
                    <!-- Category Distribution -->
                    <div class="bg-white rounded-lg shadow-lg p-6 card-hover">
                        <div class="flex justify-between items-center mb-4">
                            <h3 class="text-lg font-semibold">
                                <i class="fas fa-chart-pie mr-2 text-purple-600"></i>
                                Category Distribution
                            </h3>
                            <button onclick="app.runChart('category')" class="play-btn">
                                <i class="fas fa-play text-green-500"></i>
                            </button>
                        </div>
                        <div class="relative h-64">
                            <canvas id="category-chart"></canvas>
                        </div>
                    </div>

                    <!-- Top Colleges -->
                    <div class="bg-white rounded-lg shadow-lg p-6 card-hover">
                        <div class="flex justify-between items-center mb-4">
                            <h3 class="text-lg font-semibold">
                                <i class="fas fa-university mr-2 text-green-600"></i>
                                Top Colleges by Seats
                            </h3>
                            <button onclick="app.runChart('college')" class="play-btn">
                                <i class="fas fa-play text-green-500"></i>
                            </button>
                        </div>
                        <div class="relative h-64">
                            <canvas id="college-chart"></canvas>
                        </div>
                    </div>

                    <!-- Top Programs -->
                    <div class="bg-white rounded-lg shadow-lg p-6 card-hover">
                        <div class="flex justify-between items-center mb-4">
                            <h3 class="text-lg font-semibold">
                                <i class="fas fa-graduation-cap mr-2 text-blue-600"></i>
                                Top Programs by Seats
                            </h3>
                            <button onclick="app.runChart('program')" class="play-btn">
                                <i class="fas fa-play text-green-500"></i>
                            </button>
                        </div>
                        <div class="relative h-64">
                            <canvas id="program-chart"></canvas>
                        </div>
                    </div>

                    <!-- College vs Seats Comparison -->
                    <div class="bg-white rounded-lg shadow-lg p-6 card-hover">
                        <div class="flex justify-between items-center mb-4">
                            <h3 class="text-lg font-semibold">
                                <i class="fas fa-chart-bar mr-2 text-indigo-600"></i>
                                College vs Seats Analysis
                            </h3>
                            <button onclick="app.runChart('college-vs-seats')" class="play-btn">
                                <i class="fas fa-play text-green-500"></i>
                            </button>
                        </div>
                        <div class="relative h-64">
                            <canvas id="college-vs-seats-chart"></canvas>
                        </div>
                    </div>

                    <!-- Program Distribution -->
                    <div class="bg-white rounded-lg shadow-lg p-6 card-hover">
                        <div class="flex justify-between items-center mb-4">
                            <h3 class="text-lg font-semibold">
                                <i class="fas fa-chart-doughnut mr-2 text-pink-600"></i>
                                Program Distribution
                            </h3>
                            <button onclick="app.runChart('program-distribution')" class="play-btn">
                                <i class="fas fa-play text-green-500"></i>
                            </button>
                        </div>
                        <div class="relative h-64">
                            <canvas id="program-distribution-chart"></canvas>
                        </div>
                    </div>

                    <!-- Category Comparison -->
                    <div class="bg-white rounded-lg shadow-lg p-6 card-hover">
                        <div class="flex justify-between items-center mb-4">
                            <h3 class="text-lg font-semibold">
                                <i class="fas fa-chart-area mr-2 text-teal-600"></i>
                                Category Comparison
                            </h3>
                            <button onclick="app.runChart('category-comparison')" class="play-btn">
                                <i class="fas fa-play text-green-500"></i>
                            </button>
                        </div>
                        <div class="relative h-64">
                            <canvas id="category-comparison-chart"></canvas>
                        </div>
                    </div>
                </div>

                <!-- Advanced Analytics Row -->
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                    <!-- Seats Trend Line -->
                    <div class="bg-white rounded-lg shadow-lg p-6 card-hover">
                        <div class="flex justify-between items-center mb-4">
                            <h3 class="text-lg font-semibold">
                                <i class="fas fa-chart-line mr-2 text-orange-600"></i>
                                Seats Trend Analysis
                            </h3>
                            <button onclick="app.runChart('seats-trend')" class="play-btn">
                                <i class="fas fa-play text-green-500"></i>
                            </button>
                        </div>
                        <div class="relative h-64">
                            <canvas id="seats-trend-chart"></canvas>
                        </div>
                    </div>

                    <!-- Category Trend -->
                    <div class="bg-white rounded-lg shadow-lg p-6 card-hover">
                        <div class="flex justify-between items-center mb-4">
                            <h3 class="text-lg font-semibold">
                                <i class="fas fa-chart-line mr-2 text-red-600"></i>
                                Category Overview
                            </h3>
                            <button onclick="app.runChart('category-overview')" class="play-btn">
                                <i class="fas fa-play text-green-500"></i>
                            </button>
                        </div>
                        <div class="relative h-64">
                            <canvas id="trend-chart"></canvas>
                        </div>
                    </div>
                </div>

                <!-- Data Tables Section -->
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                    <!-- Advanced Data Table -->
                    <div class="bg-white rounded-lg shadow-lg p-6">
                        <div class="flex justify-between items-center mb-4">
                            <h3 class="text-lg font-semibold">
                                <i class="fas fa-table mr-2 text-gray-600"></i>
                                College Data Table
                            </h3>
                            <button onclick="app.runChart('data-table')" class="play-btn">
                                <i class="fas fa-play text-green-500"></i>
                            </button>
                        </div>
                        
                        <!-- Enhanced Search and Filter Section -->
                        <div class="mb-4 p-4 bg-gray-50 rounded-lg">
                            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <div>
                                    <label class="block text-sm font-medium text-gray-700 mb-1">Search College</label>
                                    <input type="text" id="college-search" placeholder="Type college name..." 
                                           class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                                           oninput="app.filterDataTable()">
                                </div>
                                <div>
                                    <label class="block text-sm font-medium text-gray-700 mb-1">Filter Program</label>
                                    <select id="program-filter" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                                            onchange="app.filterDataTable()">
                                        <option value="">All Programs</option>
                                    </select>
                                </div>
                                <div>
                                    <label class="block text-sm font-medium text-gray-700 mb-1">Filter Category</label>
                                    <select id="category-filter" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                                            onchange="app.filterDataTable()">
                                        <option value="">All Categories</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                        
                        <div id="college-data-table" class="overflow-x-auto">
                            <!-- Advanced table will be loaded here -->
                        </div>
                    </div>

                    <!-- Files Table -->
                    <div class="bg-white rounded-lg shadow-lg p-6">
                        <h3 class="text-lg font-semibold mb-4">
                            <i class="fas fa-file-alt mr-2 text-gray-600"></i>
                            Recent Files
                        </h3>
                        <div id="files-table" class="overflow-x-auto">
                            <!-- Files table will be loaded here -->
                        </div>
                    </div>
                </div>
            </div>

            <!-- Processing Modal -->
            <div id="processing-modal" class="hidden fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
                <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
                    <div class="mt-3 text-center">
                        <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-blue-100">
                            <i class="fas fa-spinner fa-spin text-blue-600 text-xl"></i>
                        </div>
                        <h3 class="text-lg leading-6 font-medium text-gray-900 mt-4">Processing PDF</h3>
                        <div class="mt-4">
                            <div id="progress-bar" class="w-full bg-gray-200 rounded-full h-2.5">
                                <div id="progress-fill" class="bg-blue-600 h-2.5 rounded-full transition-all duration-300" style="width: 0%"></div>
                            </div>
                            <p id="progress-text" class="text-sm text-gray-500 mt-2">Initializing...</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Toast Notifications -->
            <div id="toast-container" class="fixed top-4 right-4 z-50 space-y-2">
                <!-- Toasts will appear here -->
            </div>
        `;
    }

    setupCharts() {
        this.setupCategoryChart();
        this.setupCollegeChart();
        this.setupProgramChart();
        this.setupTrendChart();
        this.setupCollegeVsSeatsChart();
        this.setupProgramDistributionChart();
        this.setupCategoryComparisonChart();
        this.setupSeatsTrendChart();
    }

    setupCategoryChart() {
        const ctx = document.getElementById('category-chart');
        if (!ctx) return;

        this.charts.category = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: [],
                datasets: [{
                    data: [],
                    backgroundColor: [
                        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
                        '#9966FF', '#FF9F40', '#FF6384'
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    setupCollegeChart() {
        const ctx = document.getElementById('college-chart');
        if (!ctx) return;

        this.charts.college = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Total Seats',
                    data: [],
                    backgroundColor: 'rgba(34, 197, 94, 0.8)',
                    borderColor: 'rgba(34, 197, 94, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }

    setupProgramChart() {
        const ctx = document.getElementById('program-chart');
        if (!ctx) return;

        this.charts.program = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Total Seats',
                    data: [],
                    backgroundColor: 'rgba(59, 130, 246, 0.8)',
                    borderColor: 'rgba(59, 130, 246, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        beginAtZero: true
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }

    setupTrendChart() {
        const ctx = document.getElementById('trend-chart');
        if (!ctx) return;

        this.charts.trend = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Seats',
                    data: [],
                    borderColor: 'rgba(249, 115, 22, 1)',
                    backgroundColor: 'rgba(249, 115, 22, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }

    setupCollegeVsSeatsChart() {
        const ctx = document.getElementById('college-vs-seats-chart');
        if (!ctx) return;

        this.charts.collegeVsSeats = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: []
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                }
            }
        });
    }

    setupProgramDistributionChart() {
        const ctx = document.getElementById('program-distribution-chart');
        if (!ctx) return;

        this.charts.programDistribution = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: [],
                datasets: [{
                    data: [],
                    backgroundColor: [],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    setupCategoryComparisonChart() {
        const ctx = document.getElementById('category-comparison-chart');
        if (!ctx) return;

        this.charts.categoryComparison = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: []
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        stacked: false
                    },
                    x: {
                        stacked: false
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                }
            }
        });
    }

    setupSeatsTrendChart() {
        const ctx = document.getElementById('seats-trend-chart');
        if (!ctx) return;

        this.charts.seatsTrend = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: []
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                }
            }
        });
    }

    renderAnalytics(data) {
        this.updateSummaryCards(data.summary_cards);
        this.updateCharts(data);
    }

    updateSummaryCards(cards) {
        const container = document.getElementById('summary-cards');
        if (!container || !cards) return;

        container.innerHTML = cards.map(card => `
            <div class="bg-white rounded-lg shadow-lg p-6 card-hover">
                <div class="flex items-center">
                    <div class="p-3 rounded-full bg-${card.color}-100">
                        <i class="${card.icon} text-${card.color}-600 text-xl"></i>
                    </div>
                    <div class="ml-4">
                        <p class="text-sm font-medium text-gray-500">${card.title}</p>
                        <p class="text-2xl font-bold text-gray-900">${card.value.toLocaleString()}</p>
                        <p class="text-sm text-green-600">${card.change}</p>
                    </div>
                </div>
            </div>
        `).join('');
    }

    updateCharts(data) {
        if (this.charts.category && data.category_pie) {
            this.charts.category.data.labels = data.category_pie.labels;
            this.charts.category.data.datasets[0].data = data.category_pie.data;
            this.charts.category.update();
        }

        if (this.charts.college && data.college_bar) {
            this.charts.college.data.labels = data.college_bar.labels;
            this.charts.college.data.datasets[0].data = data.college_bar.data;
            this.charts.college.update();
        }

        if (this.charts.program && data.program_bar) {
            this.charts.program.data.labels = data.program_bar.labels;
            this.charts.program.data.datasets[0].data = data.program_bar.data;
            this.charts.program.update();
        }

        if (this.charts.trend && data.trend_line) {
            this.charts.trend.data.labels = data.trend_line.labels;
            this.charts.trend.data.datasets[0].data = data.trend_line.data;
            this.charts.trend.update();
        }

        // Update new charts
        if (this.charts.collegeVsSeats && data.college_vs_seats) {
            this.charts.collegeVsSeats.data.labels = data.college_vs_seats.labels;
            this.charts.collegeVsSeats.data.datasets = data.college_vs_seats.datasets;
            this.charts.collegeVsSeats.update();
        }

        if (this.charts.programDistribution && data.program_distribution) {
            this.charts.programDistribution.data.labels = data.program_distribution.labels;
            this.charts.programDistribution.data.datasets[0].data = data.program_distribution.data;
            this.charts.programDistribution.data.datasets[0].backgroundColor = data.program_distribution.backgroundColor;
            this.charts.programDistribution.update();
        }

        if (this.charts.categoryComparison && data.category_comparison) {
            this.charts.categoryComparison.data.labels = data.category_comparison.labels;
            this.charts.categoryComparison.data.datasets = data.category_comparison.datasets;
            this.charts.categoryComparison.update();
        }

        if (this.charts.seatsTrend && data.seats_trend_line) {
            this.charts.seatsTrend.data.labels = data.seats_trend_line.labels;
            this.charts.seatsTrend.data.datasets = data.seats_trend_line.datasets;
            this.charts.seatsTrend.update();
        }

        // Render advanced data table
        this.renderAdvancedDataTable(data);
    }

    renderAdvancedDataTable(data) {
        const container = document.getElementById('college-data-table');
        if (!container || !data.college_bar) return;

        const tableHTML = `
            <div class="overflow-x-auto">
                <table class="min-w-full bg-white border border-gray-200 rounded-lg">
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="px-6 py-3 border-b border-gray-200 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Rank
                            </th>
                            <th class="px-6 py-3 border-b border-gray-200 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                College Name
                            </th>
                            <th class="px-6 py-3 border-b border-gray-200 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Total Seats
                            </th>
                            <th class="px-6 py-3 border-b border-gray-200 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Action
                            </th>
                        </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                        ${data.college_bar.labels.map((college, index) => `
                            <tr class="hover:bg-gray-50 transition-colors">
                                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                        #${index + 1}
                                    </span>
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                    <div class="flex items-center">
                                        <i class="fas fa-university text-gray-400 mr-2"></i>
                                        ${college}
                                    </div>
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                    <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                                        ${data.college_bar.data[index]} seats
                                    </span>
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                    <button onclick="app.viewCollegeDetails('${college.replace(/'/g, "\\'")}')" 
                                            class="text-blue-600 hover:text-blue-900 transition-colors">
                                        <i class="fas fa-eye mr-1"></i>View Details
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;

        container.innerHTML = tableHTML;
    }

    viewCollegeDetails(collegeName) {
        console.log('Viewing details for:', collegeName);
        
        // Filter data for this college
        const collegeData = this.globalData.filter(record => 
            record.College && record.College.toString().toLowerCase().includes(collegeName.toLowerCase())
        );

        if (collegeData.length === 0) {
            alert('No data found for this college');
            return;
        }

        // Show modal with college details
        this.showCollegeModal(collegeName, collegeData);
    }

    showCollegeModal(collegeName, data) {
        const modalHTML = `
            <div id="college-modal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center">
                <div class="bg-white rounded-lg max-w-4xl w-full mx-4 max-h-96 overflow-y-auto">
                    <div class="p-6">
                        <div class="flex justify-between items-center mb-4">
                            <h3 class="text-lg font-semibold text-gray-900">
                                <i class="fas fa-university text-blue-600 mr-2"></i>
                                ${collegeName}
                            </h3>
                            <button onclick="document.getElementById('college-modal').remove()" 
                                    class="text-gray-400 hover:text-gray-600">
                                <i class="fas fa-times text-xl"></i>
                            </button>
                        </div>
                        
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                            <div class="bg-blue-50 p-4 rounded-lg">
                                <h4 class="font-semibold text-blue-800 mb-2">Total Programs</h4>
                                <p class="text-2xl font-bold text-blue-600">${data.length}</p>
                            </div>
                            <div class="bg-green-50 p-4 rounded-lg">
                                <h4 class="font-semibold text-green-800 mb-2">Total Seats</h4>
                                <p class="text-2xl font-bold text-green-600">
                                    ${data.reduce((sum, record) => sum + (parseInt(record['Seats']) || 0), 0)}
                                </p>
                            </div>
                        </div>

                        <div class="overflow-x-auto">
                            <table class="min-w-full bg-white border border-gray-200">
                                <thead class="bg-gray-50">
                                    <tr>
                                        <th class="px-4 py-2 border text-left text-xs font-medium text-gray-500 uppercase">Program</th>
                                        <th class="px-4 py-2 border text-left text-xs font-medium text-gray-500 uppercase">Seats</th>
                                        <th class="px-4 py-2 border text-left text-xs font-medium text-gray-500 uppercase">Category</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${data.map(record => `
                                        <tr class="hover:bg-gray-50">
                                            <td class="px-4 py-2 border text-sm">${record['Program'] || 'N/A'}</td>
                                            <td class="px-4 py-2 border text-sm">
                                                <span class="bg-blue-100 text-blue-800 px-2 py-1 rounded">
                                                    ${record['Seats'] || 'N/A'}
                                                </span>
                                            </td>
                                            <td class="px-4 py-2 border text-sm">${record['Category'] || 'N/A'}</td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHTML);
    }

    runChart(chartType) {
        console.log(`Running chart: ${chartType}`);
        
        // Add playing animation to the button
        const playBtn = event.target.closest('.play-btn');
        if (playBtn) {
            playBtn.classList.add('playing');
            playBtn.innerHTML = '<i class="fas fa-spinner fa-spin text-blue-500"></i>';
            
            // Remove animation after 2 seconds
            setTimeout(() => {
                playBtn.classList.remove('playing');
                playBtn.innerHTML = '<i class="fas fa-play text-green-500"></i>';
            }, 2000);
        }
        
        // Run specific chart based on type
        switch(chartType) {
            case 'category':
                this.updateChart('category-chart');
                break;
            case 'college':
                this.updateChart('college-chart');
                break;
            case 'program':
                this.updateChart('program-chart');
                break;
            case 'college-vs-seats':
                this.updateChart('college-vs-seats-chart');
                break;
            case 'program-distribution':
                this.updateChart('program-distribution-chart');
                break;
            case 'category-comparison':
                this.updateChart('category-comparison-chart');
                break;
            case 'seats-trend':
                this.updateChart('seats-trend-chart');
                break;
            case 'category-overview':
                this.updateChart('trend-chart');
                break;
            case 'data-table':
                this.refreshDataTable();
                break;
            default:
                this.loadAnalytics();
        }
    }

    updateChart(chartId) {
        const canvas = document.getElementById(chartId);
        if (canvas && this.currentData) {
            // Add loading effect
            const container = canvas.parentElement;
            container.style.opacity = '0.5';
            
            setTimeout(() => {
                // Re-render the specific chart
                this.renderSpecificChart(chartId, this.currentData);
                container.style.opacity = '1';
            }, 500);
        }
    }

    renderSpecificChart(chartId, data) {
        // Map chart IDs to their specific setup methods
        const chartMap = {
            'category-chart': () => this.setupCategoryChart(),
            'college-chart': () => this.setupCollegeChart(),
            'program-chart': () => this.setupProgramChart(),
            'college-vs-seats-chart': () => this.setupCollegeVsSeatsChart(),
            'program-distribution-chart': () => this.setupProgramDistributionChart(),
            'category-comparison-chart': () => this.setupCategoryComparisonChart(),
            'seats-trend-chart': () => this.setupSeatsTrendChart(),
            'trend-chart': () => this.setupTrendChart()
        };

        if (chartMap[chartId]) {
            // Destroy existing chart if it exists
            if (this.charts[chartId.replace('-chart', '').replace('-', '_')]) {
                this.charts[chartId.replace('-chart', '').replace('-', '_')].destroy();
            }
            
            // Re-create the chart
            chartMap[chartId]();
            
            // Update with current data
            this.updateCharts(data);
        }
    }

    refreshDataTable() {
        if (this.currentData) {
            this.renderAdvancedDataTable(this.currentData);
            this.populateFilterOptions();
        }
    }

    populateFilterOptions() {
        // Populate filter dropdowns with all available options
        fetch('/api/filters')
            .then(response => response.json())
            .then(data => {
                const programSelect = document.getElementById('program-filter');
                const categorySelect = document.getElementById('category-filter');
                
                if (programSelect && data.programs) {
                    programSelect.innerHTML = '<option value="">All Programs</option>';
                    data.programs.forEach(program => {
                        programSelect.innerHTML += `<option value="${program}">${program}</option>`;
                    });
                }
                
                if (categorySelect && data.categories) {
                    categorySelect.innerHTML = '<option value="">All Categories</option>';
                    data.categories.forEach(category => {
                        categorySelect.innerHTML += `<option value="${category}">${category}</option>`;
                    });
                }
            })
            .catch(error => console.error('Error loading filter options:', error));
    }

    filterDataTable() {
        const collegeSearch = document.getElementById('college-search').value.toLowerCase();
        const programFilter = document.getElementById('program-filter').value;
        const categoryFilter = document.getElementById('category-filter').value;
        
        if (!this.globalData) return;
        
        // Filter the data based on search criteria
        let filteredData = this.globalData.filter(record => {
            const collegeMatch = !collegeSearch || 
                (record.College && record.College.toString().toLowerCase().includes(collegeSearch));
            const programMatch = !programFilter || 
                (record.Program && record.Program.toString() === programFilter);
            const categoryMatch = !categoryFilter || 
                (record.Category && record.Category.toString() === categoryFilter);
            
            return collegeMatch && programMatch && categoryMatch;
        });
        
        // Re-render table with filtered data
        this.renderFilteredDataTable(filteredData);
    }

    renderFilteredDataTable(data) {
        const container = document.getElementById('college-data-table');
        if (!container) return;

        if (data.length === 0) {
            container.innerHTML = `
                <div class="text-center p-8 text-gray-500">
                    <i class="fas fa-search text-4xl mb-4"></i>
                    <p>No results found matching your search criteria.</p>
                </div>
            `;
            return;
        }

        // Group by college for table display
        const collegeGroups = {};
        data.forEach(record => {
            const college = record.College || 'Unknown College';
            if (!collegeGroups[college]) {
                collegeGroups[college] = [];
            }
            collegeGroups[college].push(record);
        });

        const tableHTML = `
            <div class="overflow-x-auto">
                <table class="min-w-full bg-white border border-gray-200 rounded-lg">
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="px-6 py-3 border-b border-gray-200 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                College Name
                            </th>
                            <th class="px-6 py-3 border-b border-gray-200 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Programs
                            </th>
                            <th class="px-6 py-3 border-b border-gray-200 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Total Seats
                            </th>
                            <th class="px-6 py-3 border-b border-gray-200 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Action
                            </th>
                        </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                        ${Object.entries(collegeGroups).map(([college, records]) => `
                            <tr class="hover:bg-gray-50 transition-colors">
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                    <div class="flex items-center">
                                        <i class="fas fa-university text-gray-400 mr-2"></i>
                                        ${college}
                                    </div>
                                </td>
                                <td class="px-6 py-4 text-sm text-gray-900">
                                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                        ${records.length} programs
                                    </span>
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                    <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                                        ${records.reduce((sum, record) => sum + (parseInt(record.Seats) || 0), 0)} seats
                                    </span>
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                    <button onclick="app.viewCollegeDetails('${college.replace(/'/g, "\\'")}')" 
                                            class="text-blue-600 hover:text-blue-900 transition-colors">
                                        <i class="fas fa-eye mr-1"></i>View Details
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
                <div class="mt-4 text-sm text-gray-600">
                    Showing ${data.length} records from ${Object.keys(collegeGroups).length} colleges
                </div>
            </div>
        `;

        container.innerHTML = tableHTML;
    }

    renderFilesList(data) {
        const pdfContainer = document.getElementById('available-pdfs');
        const tableContainer = document.getElementById('files-table');

        if (pdfContainer) {
            pdfContainer.innerHTML = data.pdf_files.map(file => `
                <div class="flex items-center justify-between p-2 bg-gray-50 rounded hover:bg-gray-100 cursor-pointer" 
                     data-action="process" data-filename="${file.name}">
                    <div class="flex items-center">
                        <i class="fas fa-file-pdf text-red-500 mr-2"></i>
                        <span class="text-sm font-medium">${file.name}</span>
                    </div>
                    <i class="fas fa-play text-green-500"></i>
                </div>
            `).join('') || '<p class="text-gray-500 text-sm">No PDFs available</p>';
        }

        if (tableContainer) {
            tableContainer.innerHTML = `
                <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">File</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Size</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Modified</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                        </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                        ${[...data.pdf_files, ...data.processed_files].map(file => `
                            <tr class="hover:bg-gray-50">
                                <td class="px-6 py-4 whitespace-nowrap">
                                    <div class="flex items-center">
                                        <i class="fas fa-file-${file.type === 'pdf' ? 'pdf text-red-500' : 'excel text-green-500'} mr-2"></i>
                                        <span class="text-sm font-medium text-gray-900">${file.name}</span>
                                    </div>
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${file.type.toUpperCase()}</td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${this.formatFileSize(file.size)}</td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${new Date(file.modified).toLocaleDateString()}</td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                                    <button class="text-blue-600 hover:text-blue-900" data-action="download" data-filename="${file.name}">
                                        <i class="fas fa-download"></i>
                                    </button>
                                    ${file.type === 'pdf' ? `
                                        <button class="text-green-600 hover:text-green-900" data-action="process" data-filename="${file.name}">
                                            <i class="fas fa-play"></i>
                                        </button>
                                    ` : ''}
                                    <button class="text-red-600 hover:text-red-900" data-action="delete" data-filename="${file.name}">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        }
    }

    handleAction(action, data) {
        switch (action) {
            case 'process':
                this.processExistingFile(data.filename);
                break;
            case 'download':
                window.open(`/api/download/${data.filename}`, '_blank');
                break;
            case 'delete':
                if (confirm(`Are you sure you want to delete ${data.filename}?`)) {
                    this.deleteFile(data.filename);
                }
                break;
        }
    }

    async deleteFile(filename) {
        try {
            await fetch(`/api/files/${filename}`, { method: 'DELETE' });
            this.loadFiles();
            this.showSuccess('File deleted successfully');
        } catch (error) {
            this.showError('Delete failed: ' + error.message);
        }
    }

    showProcessingModal(message) {
        const modal = document.getElementById('processing-modal');
        const text = document.getElementById('progress-text');
        const fill = document.getElementById('progress-fill');
        
        if (modal && text && fill) {
            text.textContent = message;
            fill.style.width = '0%';
            modal.classList.remove('hidden');
        }
    }

    updateProcessingModal(status) {
        const text = document.getElementById('progress-text');
        const fill = document.getElementById('progress-fill');
        
        if (text && fill) {
            text.textContent = status.message;
            fill.style.width = status.progress + '%';
        }
    }

    hideProcessingModal() {
        const modal = document.getElementById('processing-modal');
        if (modal) {
            modal.classList.add('hidden');
        }
    }

    showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        if (!container) return;

        const colors = {
            success: 'bg-green-500',
            error: 'bg-red-500',
            info: 'bg-blue-500'
        };

        const toast = document.createElement('div');
        toast.className = `${colors[type]} text-white px-6 py-4 rounded-lg shadow-lg transform transition-all duration-300 translate-x-full`;
        toast.innerHTML = `
            <div class="flex items-center justify-between">
                <span>${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" class="ml-4 text-white hover:text-gray-200">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

        container.appendChild(toast);
        setTimeout(() => toast.classList.remove('translate-x-full'), 100);
        setTimeout(() => toast.remove(), 5000);
    }

    showSuccess(message) {
        this.showToast(message, 'success');
    }

    showError(message) {
        this.showToast(message, 'error');
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    setupRealTimeUpdates() {
        // Auto-refresh files every 30 seconds
        setInterval(() => {
            this.loadFiles();
        }, 30000);
    }

    toggleMobileMenu() {
        // Implementation for mobile menu toggle
        console.log('Mobile menu toggled');
    }

    switchView(view) {
        this.currentView = view;
        
        switch(view) {
            case 'dashboard':
                this.loadDashboard();
                break;
            case 'search':
                this.loadSearchView();
                break;
            case 'files':
                this.loadFilesView();
                break;
            case 'analytics':
                this.loadAnalyticsView();
                break;
            default:
                this.loadDashboard();
        }
        
        // Update active navigation
        document.querySelectorAll('[data-view]').forEach(el => {
            el.classList.remove('bg-blue-700');
            if (el.dataset.view === view) {
                el.classList.add('bg-blue-700');
            }
        });
    }

    loadSearchView() {
        document.getElementById('app').innerHTML = this.getSearchHTML();
        this.initializeSearch();
    }

    loadFilesView() {
        document.getElementById('app').innerHTML = this.getFilesHTML();
        this.loadFiles();
    }

    loadAnalyticsView() {
        document.getElementById('app').innerHTML = this.getAnalyticsHTML();
        this.loadAnalytics();
    }

    getSearchHTML() {
        return `
            <!-- Navigation -->
            <nav class="gradient-bg shadow-lg">
                <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div class="flex justify-between h-16">
                        <div class="flex items-center">
                            <div class="flex-shrink-0">
                                <h1 class="text-white text-xl font-bold">
                                    <i class="fas fa-graduation-cap mr-2"></i>
                                    DU Admission Analyzer
                                </h1>
                            </div>
                            <div class="hidden md:ml-6 md:flex md:space-x-8">
                                <a href="#" data-view="dashboard" class="text-white hover:text-gray-200 px-3 py-2 text-sm font-medium">
                                    <i class="fas fa-chart-line mr-1"></i> Dashboard
                                </a>
                                <a href="#" data-view="search" class="text-white hover:text-gray-200 px-3 py-2 text-sm font-medium bg-blue-700">
                                    <i class="fas fa-search mr-1"></i> Advanced Search
                                </a>
                                <a href="#" data-view="files" class="text-white hover:text-gray-200 px-3 py-2 text-sm font-medium">
                                    <i class="fas fa-folder mr-1"></i> Files
                                </a>
                                <a href="#" data-view="analytics" class="text-white hover:text-gray-200 px-3 py-2 text-sm font-medium">
                                    <i class="fas fa-chart-bar mr-1"></i> Analytics
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </nav>

            <!-- Advanced Search Content -->
            <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
                <!-- Search Form -->
                <div class="bg-white rounded-lg shadow-lg p-6 mb-6">
                    <h2 class="text-2xl font-bold text-gray-900 mb-6">
                        <i class="fas fa-search mr-2 text-blue-600"></i>
                        Advanced Search & Filter
                    </h2>
                    
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                        <!-- College Search -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">
                                College Name
                            </label>
                            <div class="relative">
                                <input type="text" id="college-search" 
                                       class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                       placeholder="Search or select college...">
                                <div id="college-dropdown" class="hidden absolute z-10 w-full bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-y-auto">
                                    <!-- Options will be populated here -->
                                </div>
                            </div>
                        </div>

                        <!-- Program Search -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">
                                Program Name
                            </label>
                            <div class="relative">
                                <input type="text" id="program-search" 
                                       class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                       placeholder="Search or select program...">
                                <div id="program-dropdown" class="hidden absolute z-10 w-full bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-y-auto">
                                    <!-- Options will be populated here -->
                                </div>
                            </div>
                        </div>

                        <!-- Category Filter -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">
                                Category
                            </label>
                            <select id="category-filter" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                                <option value="">All Categories</option>
                                <option value="UR">UR (Unreserved)</option>
                                <option value="OBC">OBC</option>
                                <option value="SC">SC</option>
                                <option value="ST">ST</option>
                                <option value="EWS">EWS</option>
                                <option value="SIKH">SIKH</option>
                                <option value="PwBD">PwBD</option>
                            </select>
                        </div>
                    </div>

                    <div class="flex justify-center">
                        <button id="search-btn" class="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors">
                            <i class="fas fa-search mr-2"></i>
                            Search
                        </button>
                        <button id="clear-btn" class="ml-4 px-6 py-2 bg-gray-400 text-white rounded-md hover:bg-gray-500 transition-colors">
                            <i class="fas fa-times mr-2"></i>
                            Clear
                        </button>
                    </div>
                </div>

                <!-- Search Results -->
                <div id="search-results" class="hidden">
                    <!-- Results Summary -->
                    <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                        <div class="flex items-center">
                            <i class="fas fa-info-circle text-blue-600 mr-2"></i>
                            <span id="results-summary" class="text-blue-800"></span>
                        </div>
                    </div>

                    <!-- Results Tabs -->
                    <div class="bg-white rounded-lg shadow-lg">
                        <div class="border-b border-gray-200">
                            <nav class="-mb-px flex space-x-8 px-6">
                                <button id="colleges-tab" class="py-4 px-1 border-b-2 border-blue-500 font-medium text-sm text-blue-600">
                                    Colleges (<span id="colleges-count">0</span>)
                                </button>
                                <button id="programs-tab" class="py-4 px-1 border-b-2 border-transparent font-medium text-sm text-gray-500 hover:text-gray-700">
                                    Programs (<span id="programs-count">0</span>)
                                </button>
                            </nav>
                        </div>

                        <!-- Colleges Results -->
                        <div id="colleges-results" class="p-6">
                            <div id="colleges-list" class="space-y-4">
                                <!-- College results will be populated here -->
                            </div>
                        </div>

                        <!-- Programs Results -->
                        <div id="programs-results" class="p-6 hidden">
                            <div id="programs-list" class="space-y-4">
                                <!-- Program results will be populated here -->
                            </div>
                        </div>
                    </div>
                </div>

                <!-- No Data Message -->
                <div id="no-data-message" class="text-center py-12">
                    <i class="fas fa-database text-6xl text-gray-300 mb-4"></i>
                    <h3 class="text-xl font-medium text-gray-500">No Data Available</h3>
                    <p class="text-gray-400 mt-2">Please upload and process a PDF file first to use the search feature.</p>
                    <button data-view="dashboard" class="mt-4 px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors">
                        <i class="fas fa-upload mr-2"></i>
                        Go to Upload
                    </button>
                </div>
            </div>
        `;
    }

    getFilesHTML() {
        return `
            <!-- Navigation with Files active -->
            <nav class="gradient-bg shadow-lg">
                <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div class="flex justify-between h-16">
                        <div class="flex items-center">
                            <div class="flex-shrink-0">
                                <h1 class="text-white text-xl font-bold">
                                    <i class="fas fa-graduation-cap mr-2"></i>
                                    DU Admission Analyzer
                                </h1>
                            </div>
                            <div class="hidden md:ml-6 md:flex md:space-x-8">
                                <a href="#" data-view="dashboard" class="text-white hover:text-gray-200 px-3 py-2 text-sm font-medium">
                                    <i class="fas fa-chart-line mr-1"></i> Dashboard
                                </a>
                                <a href="#" data-view="search" class="text-white hover:text-gray-200 px-3 py-2 text-sm font-medium">
                                    <i class="fas fa-search mr-1"></i> Advanced Search
                                </a>
                                <a href="#" data-view="files" class="text-white hover:text-gray-200 px-3 py-2 text-sm font-medium bg-blue-700">
                                    <i class="fas fa-folder mr-1"></i> Files
                                </a>
                                <a href="#" data-view="analytics" class="text-white hover:text-gray-200 px-3 py-2 text-sm font-medium">
                                    <i class="fas fa-chart-bar mr-1"></i> Analytics
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </nav>

            <!-- Files Content -->
            <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
                <div class="bg-white rounded-lg shadow-lg p-6">
                    <h2 class="text-2xl font-bold text-gray-900 mb-6">
                        <i class="fas fa-folder mr-2 text-blue-600"></i>
                        File Management
                    </h2>
                    <div id="files-container">
                        <!-- Files will be loaded here -->
                    </div>
                </div>
            </div>
        `;
    }

    getAnalyticsHTML() {
        return `
            <!-- Navigation with Analytics active -->
            <nav class="gradient-bg shadow-lg">
                <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div class="flex justify-between h-16">
                        <div class="flex items-center">
                            <div class="flex-shrink-0">
                                <h1 class="text-white text-xl font-bold">
                                    <i class="fas fa-graduation-cap mr-2"></i>
                                    DU Admission Analyzer
                                </h1>
                            </div>
                            <div class="hidden md:ml-6 md:flex md:space-x-8">
                                <a href="#" data-view="dashboard" class="text-white hover:text-gray-200 px-3 py-2 text-sm font-medium">
                                    <i class="fas fa-chart-line mr-1"></i> Dashboard
                                </a>
                                <a href="#" data-view="search" class="text-white hover:text-gray-200 px-3 py-2 text-sm font-medium">
                                    <i class="fas fa-search mr-1"></i> Advanced Search
                                </a>
                                <a href="#" data-view="files" class="text-white hover:text-gray-200 px-3 py-2 text-sm font-medium">
                                    <i class="fas fa-folder mr-1"></i> Files
                                </a>
                                <a href="#" data-view="analytics" class="text-white hover:text-gray-200 px-3 py-2 text-sm font-medium bg-blue-700">
                                    <i class="fas fa-chart-bar mr-1"></i> Analytics
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </nav>

            <!-- Analytics Content -->
            <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
                <div class="bg-white rounded-lg shadow-lg p-6">
                    <h2 class="text-2xl font-bold text-gray-900 mb-6">
                        <i class="fas fa-chart-bar mr-2 text-blue-600"></i>
                        Advanced Analytics
                    </h2>
                    <div id="analytics-container">
                        <!-- Analytics will be loaded here -->
                    </div>
                </div>
            </div>
        `;
    }

    async initializeSearch() {
        try {
            // Load filter options
            const response = await fetch('/api/filters');
            if (response.ok) {
                this.filterOptions = await response.json();
                this.setupSearchEventListeners();
                this.populateSearchOptions();
                document.getElementById('no-data-message').style.display = 'none';
            } else {
                document.getElementById('no-data-message').style.display = 'block';
                document.getElementById('search-results').style.display = 'none';
            }
        } catch (error) {
            console.error('Error loading filter options:', error);
            document.getElementById('no-data-message').style.display = 'block';
        }
    }

    setupSearchEventListeners() {
        // Search button
        document.getElementById('search-btn').addEventListener('click', () => {
            this.performSearch();
        });

        // Clear button
        document.getElementById('clear-btn').addEventListener('click', () => {
            this.clearSearch();
        });

        // Tab switching
        document.getElementById('colleges-tab').addEventListener('click', () => {
            this.switchResultsTab('colleges');
        });
        document.getElementById('programs-tab').addEventListener('click', () => {
            this.switchResultsTab('programs');
        });

        // Dropdown functionality
        this.setupDropdown('college-search', 'college-dropdown', this.filterOptions.colleges);
        this.setupDropdown('program-search', 'program-dropdown', this.filterOptions.programs);

        // Enter key search
        ['college-search', 'program-search', 'category-filter'].forEach(id => {
            document.getElementById(id).addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.performSearch();
                }
            });
        });
    }

    setupDropdown(inputId, dropdownId, options) {
        const input = document.getElementById(inputId);
        const dropdown = document.getElementById(dropdownId);

        input.addEventListener('input', () => {
            const value = input.value.toLowerCase();
            const filtered = options.filter(option => 
                option.toLowerCase().includes(value)
            );
            
            this.renderDropdownOptions(dropdown, filtered, input);
            dropdown.classList.remove('hidden');
        });

        input.addEventListener('focus', () => {
            this.renderDropdownOptions(dropdown, options, input);
            dropdown.classList.remove('hidden');
        });

        document.addEventListener('click', (e) => {
            if (!input.contains(e.target) && !dropdown.contains(e.target)) {
                dropdown.classList.add('hidden');
            }
        });
    }

    renderDropdownOptions(dropdown, options, input) {
        dropdown.innerHTML = options.slice(0, 10).map(option => `
            <div class="px-3 py-2 hover:bg-gray-100 cursor-pointer text-sm" 
                 onclick="document.getElementById('${input.id}').value='${option}'; this.parentElement.classList.add('hidden');">
                ${option}
            </div>
        `).join('');
    }

    populateSearchOptions() {
        // This method can be used to preload recent searches or popular options
        console.log('Filter options loaded:', this.filterOptions);
    }

    async performSearch() {
        const criteria = {
            college: document.getElementById('college-search').value,
            program: document.getElementById('program-search').value,
            category: document.getElementById('category-filter').value
        };

        // Check if at least one criteria is provided
        if (!criteria.college && !criteria.program && !criteria.category) {
            this.showError('Please enter at least one search criteria');
            return;
        }

        try {
            const response = await fetch('/api/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ criteria })
            });

            if (response.ok) {
                const results = await response.json();
                this.displaySearchResults(results);
            } else {
                const error = await response.json();
                this.showError(error.error || 'Search failed');
            }
        } catch (error) {
            console.error('Search error:', error);
            this.showError('Search failed: ' + error.message);
        }
    }

    displaySearchResults(results) {
        const resultsDiv = document.getElementById('search-results');
        const summarySpan = document.getElementById('results-summary');
        
        // Update summary
        summarySpan.textContent = `Found ${results.total_results} results (${results.summary.colleges_found} colleges, ${results.summary.programs_found} programs)`;
        
        // Update counts
        document.getElementById('colleges-count').textContent = results.summary.colleges_found;
        document.getElementById('programs-count').textContent = results.summary.programs_found;
        
        // Render colleges
        this.renderCollegeResults(results.colleges);
        
        // Render programs
        this.renderProgramResults(results.programs);
        
        resultsDiv.classList.remove('hidden');
        this.switchResultsTab('colleges');
    }

    renderCollegeResults(colleges) {
        const container = document.getElementById('colleges-list');
        
        if (colleges.length === 0) {
            container.innerHTML = `
                <div class="text-center py-8 text-gray-500">
                    <i class="fas fa-university text-4xl mb-4"></i>
                    <p>No colleges found matching your criteria</p>
                </div>
            `;
            return;
        }

        container.innerHTML = colleges.map(college => `
            <div class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <div class="flex justify-between items-start mb-3">
                    <h3 class="text-lg font-semibold text-gray-900">${college.name}</h3>
                    <span class="bg-blue-100 text-blue-800 text-sm px-2 py-1 rounded">
                        ${college.total_seats} seats
                    </span>
                </div>
                
                <div class="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
                    ${Object.entries(college.categories).map(([cat, seats]) => `
                        <div class="bg-gray-50 px-2 py-1 rounded">
                            <span class="font-medium">${cat}:</span> ${seats}
                        </div>
                    `).join('')}
                </div>
                
                <div class="mt-3 flex justify-end">
                    <button class="text-blue-600 hover:text-blue-800 text-sm" 
                            onclick="app.viewCollegeDetails('${college.name}')">
                        <i class="fas fa-eye mr-1"></i>View Details
                    </button>
                </div>
            </div>
        `).join('');
    }

    renderProgramResults(programs) {
        const container = document.getElementById('programs-list');
        
        if (programs.length === 0) {
            container.innerHTML = `
                <div class="text-center py-8 text-gray-500">
                    <i class="fas fa-graduation-cap text-4xl mb-4"></i>
                    <p>No programs found matching your criteria</p>
                </div>
            `;
            return;
        }

        container.innerHTML = programs.map(program => `
            <div class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <div class="flex justify-between items-start mb-3">
                    <h3 class="text-lg font-semibold text-gray-900">${program.name}</h3>
                    <span class="bg-green-100 text-green-800 text-sm px-2 py-1 rounded">
                        ${program.total_seats} seats
                    </span>
                </div>
                
                <div class="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
                    ${Object.entries(program.categories).map(([cat, seats]) => `
                        <div class="bg-gray-50 px-2 py-1 rounded">
                            <span class="font-medium">${cat}:</span> ${seats}
                        </div>
                    `).join('')}
                </div>
            </div>
        `).join('');
    }

    switchResultsTab(tab) {
        // Update tab appearance
        const collegesTab = document.getElementById('colleges-tab');
        const programsTab = document.getElementById('programs-tab');
        const collegesResults = document.getElementById('colleges-results');
        const programsResults = document.getElementById('programs-results');

        if (tab === 'colleges') {
            collegesTab.classList.add('border-blue-500', 'text-blue-600');
            collegesTab.classList.remove('border-transparent', 'text-gray-500');
            programsTab.classList.add('border-transparent', 'text-gray-500');
            programsTab.classList.remove('border-blue-500', 'text-blue-600');
            collegesResults.classList.remove('hidden');
            programsResults.classList.add('hidden');
        } else {
            programsTab.classList.add('border-blue-500', 'text-blue-600');
            programsTab.classList.remove('border-transparent', 'text-gray-500');
            collegesTab.classList.add('border-transparent', 'text-gray-500');
            collegesTab.classList.remove('border-blue-500', 'text-blue-600');
            programsResults.classList.remove('hidden');
            collegesResults.classList.add('hidden');
        }
    }

    clearSearch() {
        document.getElementById('college-search').value = '';
        document.getElementById('program-search').value = '';
        document.getElementById('category-filter').value = '';
        document.getElementById('search-results').classList.add('hidden');
    }

    async viewCollegeDetails(collegeName) {
        try {
            const response = await fetch(`/api/college/${encodeURIComponent(collegeName)}`);
            if (response.ok) {
                const details = await response.json();
                this.showCollegeModal(details);
            } else {
                const error = await response.json();
                this.showError(error.error || 'Failed to load college details');
            }
        } catch (error) {
            console.error('Error loading college details:', error);
            this.showError('Failed to load college details');
        }
    }

    showCollegeModal(details) {
        // Create and show modal with college details
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50';
        modal.innerHTML = `
            <div class="relative top-20 mx-auto p-5 border w-11/12 max-w-4xl shadow-lg rounded-md bg-white">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-xl font-bold text-gray-900">${details.name}</h3>
                    <button class="text-gray-400 hover:text-gray-600" onclick="this.closest('.fixed').remove()">
                        <i class="fas fa-times text-xl"></i>
                    </button>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <h4 class="font-semibold mb-2">Total Seats</h4>
                        <p class="text-2xl font-bold text-blue-600">${details.total_seats}</p>
                    </div>
                    
                    <div>
                        <h4 class="font-semibold mb-2">Category-wise Distribution</h4>
                        <div class="space-y-2">
                            ${Object.entries(details.categories || {}).map(([cat, seats]) => `
                                <div class="flex justify-between">
                                    <span>${cat}:</span>
                                    <span class="font-medium">${seats}</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
                
                <div class="mt-6 flex justify-end">
                    <button class="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
                            onclick="this.closest('.fixed').remove()">
                        Close
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    }

    loadAnalytics() {
        // Placeholder for analytics loading
        const container = document.getElementById('analytics-container');
        container.innerHTML = `
            <div class="text-center py-12">
                <i class="fas fa-chart-bar text-6xl text-gray-300 mb-4"></i>
                <h3 class="text-xl font-medium text-gray-500">Advanced Analytics</h3>
                <p class="text-gray-400 mt-2">Coming soon - detailed analytics and insights.</p>
            </div>
        `;
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new DUAnalyzerApp();
});

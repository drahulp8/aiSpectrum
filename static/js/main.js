document.addEventListener('DOMContentLoaded', () => {
    // Main elements
    const submitBtn = document.getElementById('submit-btn');
    const queryInput = document.getElementById('query-input');
    const loadingIndicator = document.getElementById('loading-indicator');
    const responsesContainer = document.getElementById('responses-container');
    const followupContainer = document.getElementById('followup-container');
    const followupInput = document.getElementById('followup-input');
    const followupBtn = document.getElementById('followup-btn');
    const activeModelsCount = document.getElementById('active-models-count');
    const summaryContainer = document.getElementById('summary-container');
    const summaryContent = document.getElementById('summary-content');
    const mainContent = document.getElementById('main-content');
    const toggleLayoutBtn = document.getElementById('toggle-layout');
    
    // Sidebar elements
    const openSidebarBtn = document.getElementById('open-sidebar');
    const closeSidebarBtn = document.getElementById('close-sidebar');
    const sidebar = document.getElementById('sidebar');
    const modelSelectorsContainer = document.getElementById('model-selectors');
    const queryHistoryContainer = document.getElementById('query-history');
    const userProfileElement = document.getElementById('user-profile');
    const enableSummaryCheckbox = document.getElementById('enable-summary');
    const darkModeCheckbox = document.getElementById('dark-mode');
    
    // API Tester Panel
    const openApiTesterBtn = document.getElementById('open-api-tester');
    const closeApiTesterBtn = document.getElementById('close-api-tester');
    const apiTesterPanel = document.getElementById('api-tester-panel');
    const apiTestProviderSelect = document.getElementById('api-test-provider');
    const apiTestKeyInput = document.getElementById('api-test-key');
    const testApiBtn = document.getElementById('test-api-btn');
    const apiTestResult = document.getElementById('api-test-result');
    const savedKeysContainer = document.getElementById('saved-keys-container');
    const saveAllKeysBtn = document.getElementById('save-all-keys');
    
    // Toast elements
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toast-message');
    
    // State variables
    let currentLayout = 'grid'; // grid or column
    let currentQuery = '';
    let queryHistory = JSON.parse(localStorage.getItem('query-history') || '[]');
    let availableModels = {};
    let activeModels = JSON.parse(localStorage.getItem('active-models') || '["openai", "anthropic", "deepseek"]');
    let userProfile = null;
    let enableSummary = localStorage.getItem('enable-summary') === 'true';

    // Initialize the UI
    initializeUI();
    
    async function initializeUI() {
        // Check authentication status
        await checkAuthStatus();
        
        // Fetch available models
        await fetchAvailableModels();
        
        // Render model selectors
        renderModelSelectors();
        
        // Update active models count
        updateActiveModelsCount();
        
        // Render query history
        renderQueryHistory();
        
        // Load saved API keys
        renderSavedAPIKeys();
        
        // Set up event listeners
        setupEventListeners();
        
        // Set initial options state
        if (enableSummaryCheckbox) {
            enableSummaryCheckbox.checked = enableSummary;
        }
        
        // Update main content layout (sidebar shift effect)
        updateMainContentLayout();
    }
    
    function updateMainContentLayout() {
        // Check if sidebar is open and window is wide enough
        if (window.innerWidth >= 1280 && sidebar.classList.contains('open')) {
            mainContent.classList.add('content-shifted');
        } else {
            mainContent.classList.remove('content-shifted');
        }
    }
    
    async function checkAuthStatus() {
        try {
            const response = await fetch('/api/auth/status', {
                credentials: 'include'
            });
            
            const data = await response.json();
            
            if (data.authenticated) {
                userProfile = data.user;
                renderUserProfile();
            } else {
                renderLoginButton();
            }
        } catch (error) {
            console.error('Error checking auth status:', error);
            renderLoginButton();
        }
    }
    
    function renderUserProfile() {
        if (!userProfileElement) return;
        
        if (userProfile) {
            userProfileElement.innerHTML = `
                <div class="flex items-center space-x-3">
                    <img src="${userProfile.picture || `https://ui-avatars.com/api/?name=${encodeURIComponent(userProfile.name)}&background=9181F7&color=fff`}" 
                         class="w-10 h-10 rounded-full border border-neon-secondary" alt="Profile">
                    <div>
                        <p class="text-sm font-medium text-gray-200">${userProfile.name}</p>
                        <p class="text-xs text-gray-400">${userProfile.email}</p>
                    </div>
                    <button id="logout-btn" class="text-gray-400 hover:text-red-400 ml-auto">
                        <i class="fas fa-sign-out-alt"></i>
                    </button>
                </div>
            `;
            
            // Add logout event listener
            document.getElementById('logout-btn').addEventListener('click', logout);
        } else {
            renderLoginButton();
        }
    }
    
    function renderLoginButton() {
        if (!userProfileElement) return;
        
        userProfileElement.innerHTML = `
            <a href="/login" class="flex items-center space-x-2 text-neon-secondary hover:text-neon-primary transition-colors">
                <i class="fas fa-sign-in-alt"></i>
                <span>Sign In</span>
            </a>
        `;
    }
    
    async function logout() {
        try {
            const response = await fetch('/api/auth/logout', {
                method: 'POST',
                credentials: 'include'
            });
            
            const data = await response.json();
            
            if (data.success) {
                userProfile = null;
                renderLoginButton();
                showToast('Logged out successfully');
            }
        } catch (error) {
            console.error('Error logging out:', error);
            showToast('Error logging out', 'error');
        }
    }
    
    async function fetchAvailableModels() {
        try {
            const response = await fetch('/api/models');
            availableModels = await response.json();
        } catch (error) {
            console.error('Error fetching models:', error);
            showToast('Error fetching available models', 'error');
        }
    }
    
    function renderModelSelectors() {
        if (!modelSelectorsContainer) return;
        
        modelSelectorsContainer.innerHTML = '';
        
        // Create model selector checkboxes
        Object.keys(availableModels).forEach(modelId => {
            const model = availableModels[modelId];
            const isActive = activeModels.includes(modelId);
            const hasAPIKey = localStorage.getItem(`${modelId}-key`);
            
            const modelSelector = document.createElement('div');
            modelSelector.className = 'flex items-center p-3 hover:bg-mocha-medium rounded-lg transition-all duration-300 retro-card';
            
            modelSelector.innerHTML = `
                <input type="checkbox" id="model-${modelId}" class="h-4 w-4 rounded bg-mocha-darkest border-mocha-light 
                    focus:ring-accent-gold focus:ring-2 text-accent-gold" 
                    data-model-id="${modelId}" ${isActive ? 'checked' : ''} ${!hasAPIKey ? 'disabled' : ''}>
                <label for="model-${modelId}" class="ml-3 text-sm font-medium ${hasAPIKey ? 'text-cream-light' : 'text-cream-dark'} flex-grow cursor-pointer">${model.name}</label>
                <span class="text-xs px-2 py-1 rounded-full ${getModelBadgeColor(model.color)}">${model.models.length}</span>
            `;
            
            modelSelectorsContainer.appendChild(modelSelector);
            
            // Add event listener
            const checkbox = modelSelector.querySelector(`#model-${modelId}`);
            checkbox.addEventListener('change', (e) => {
                toggleModelActive(modelId, e.target.checked);
            });
            
            // Add event listener to label to open API tester panel if no API key
            if (!hasAPIKey) {
                const label = modelSelector.querySelector(`label[for="model-${modelId}"]`);
                label.addEventListener('click', (e) => {
                    // Prevent checkbox change
                    e.preventDefault();
                    
                    // Open API tester panel and select this provider
                    openApiTesterPanel(modelId);
                });
            }
        });
    }
    
    function getModelBadgeColor(color) {
        const colorMap = {
            'green': 'bg-mocha-dark border border-accent-teal text-accent-teal',
            'purple': 'bg-mocha-dark border border-accent-coral text-accent-coral',
            'blue': 'bg-mocha-dark border border-accent-teal text-accent-teal',
            'yellow': 'bg-mocha-dark border border-accent-gold text-accent-gold',
            'teal': 'bg-mocha-dark border border-accent-teal text-accent-teal',
            'pink': 'bg-mocha-dark border border-accent-coral text-accent-coral',
            'lime': 'bg-mocha-dark border border-accent-gold text-accent-gold',
            'indigo': 'bg-mocha-dark border border-accent-teal text-accent-teal',
            'gray': 'bg-mocha-dark border border-cream-dark text-cream-dark'
        };
        
        return colorMap[color] || 'bg-mocha-dark border border-cream-dark text-cream-dark';
    }
    
    function toggleModelActive(modelId, isActive) {
        if (isActive && !activeModels.includes(modelId)) {
            // Add model to active models
            activeModels.push(modelId);
            createResponseContainer(modelId);
        } else if (!isActive && activeModels.includes(modelId)) {
            // Remove model from active models
            activeModels = activeModels.filter(id => id !== modelId);
            removeResponseContainer(modelId);
        }
        
        // Save active models to localStorage
        localStorage.setItem('active-models', JSON.stringify(activeModels));
        
        // Update active models count
        updateActiveModelsCount();
    }
    
    function renderSavedAPIKeys() {
        if (!savedKeysContainer) return;
        
        savedKeysContainer.innerHTML = '';
        let hasKeys = false;
        
        Object.keys(availableModels).forEach(modelId => {
            const model = availableModels[modelId];
            const savedKey = localStorage.getItem(`${modelId}-key`);
            
            if (savedKey) {
                hasKeys = true;
                const keyItem = document.createElement('div');
                keyItem.className = 'flex items-center justify-between p-2 border border-gray-800 rounded bg-terminal-bg';
                
                // Masked key display for security
                const maskedKey = savedKey.substring(0, 3) + '•'.repeat(Math.max(0, savedKey.length - 6)) + savedKey.substring(savedKey.length - 3);
                
                keyItem.innerHTML = `
                    <div>
                        <div class="font-medium text-sm text-gray-300">${model.name}</div>
                        <div class="text-xs text-gray-500">${maskedKey}</div>
                    </div>
                    <button class="text-red-500 hover:text-red-400 delete-key-btn" data-model="${modelId}">
                        <i class="fas fa-trash-alt"></i>
                    </button>
                `;
                
                savedKeysContainer.appendChild(keyItem);
                
                // Add delete button event listener
                const deleteBtn = keyItem.querySelector('.delete-key-btn');
                deleteBtn.addEventListener('click', () => {
                    deleteAPIKey(modelId);
                });
            }
        });
        
        if (!hasKeys) {
            savedKeysContainer.innerHTML = '<div class="text-sm text-gray-500">No API keys saved yet</div>';
        }
    }
    
    function deleteAPIKey(modelId) {
        localStorage.removeItem(`${modelId}-key`);
        
        // Update UI
        renderSavedAPIKeys();
        renderModelSelectors();
        
        // If model was active, remove it
        if (activeModels.includes(modelId)) {
            toggleModelActive(modelId, false);
        }
        
        showToast(`${availableModels[modelId].name} API key removed`);
    }
    
    function createResponseContainer(modelId) {
        if (!responsesContainer || !availableModels[modelId]) return;
        
        const model = availableModels[modelId];
        const modelColor = getModelColor(model.color);
        
        // Create response container
        const responseContainer = document.createElement('div');
        responseContainer.id = `${modelId}-container`;
        responseContainer.className = 'retro-card rounded-lg shadow-lg overflow-hidden transition-all duration-300';
        
        responseContainer.innerHTML = `
            <div class="mocha-gradient p-4 model-header flex justify-between items-center border-b border-mocha-light">
                <h3 class="font-serif font-medium" style="color: ${modelColor}">${model.name} <span id="${modelId}-model-display" class="text-sm font-mono opacity-80"></span></h3>
                <button class="copy-btn text-cream-dark hover:text-accent-coral p-1 transition-colors duration-300" data-model="${modelId}">
                    <i class="fas fa-copy"></i>
                </button>
            </div>
            <div id="${modelId}-response" class="p-5 markdown-content overflow-auto h-96 terminal-font text-cream-light"></div>
        `;
        
        responsesContainer.appendChild(responseContainer);
        
        // Add event listener for copy button
        const copyBtn = responseContainer.querySelector('.copy-btn');
        copyBtn.addEventListener('click', () => {
            const contentElement = document.getElementById(`${modelId}-response`);
            copyToClipboard(contentElement.textContent || '');
            showToast(`${model.name} response copied to clipboard`);
        });
    }
    
    function getModelColor(color) {
        const colorMap = {
            'green': '#68BFB7',    // accent-teal
            'purple': '#D4AF37',   // accent-gold
            'blue': '#68BFB7',     // accent-teal
            'yellow': '#D4AF37',   // accent-gold
            'teal': '#68BFB7',     // accent-teal
            'pink': '#FF8E72',     // accent-coral
            'lime': '#D4AF37',     // accent-gold
            'indigo': '#68BFB7',   // accent-teal
            'gray': '#D4C6B6'      // cream-dark
        };
        
        return colorMap[color] || '#D4C6B6'; // Default to cream-dark
    }
    
    function removeResponseContainer(modelId) {
        const container = document.getElementById(`${modelId}-container`);
        if (container) {
            container.remove();
        }
    }
    
    function setupEventListeners() {
        // Sidebar toggle
        if (openSidebarBtn) {
            openSidebarBtn.addEventListener('click', () => {
                sidebar.classList.add('open');
                updateMainContentLayout();
            });
        }
        
        if (closeSidebarBtn) {
            closeSidebarBtn.addEventListener('click', () => {
                sidebar.classList.remove('open');
                updateMainContentLayout();
            });
        }
        
        // API Tester panel
        if (openApiTesterBtn) {
            openApiTesterBtn.addEventListener('click', () => {
                openApiTesterPanel();
            });
        }
        
        if (closeApiTesterBtn) {
            closeApiTesterBtn.addEventListener('click', () => {
                apiTesterPanel.classList.remove('open');
            });
        }
        
        // Test API button
        if (testApiBtn) {
            testApiBtn.addEventListener('click', testAPIKey);
        }
        
        // Save all keys
        if (saveAllKeysBtn) {
            saveAllKeysBtn.addEventListener('click', saveAllAPIKeys);
        }
        
        // Toggle layout button
        if (toggleLayoutBtn) {
            toggleLayoutBtn.addEventListener('click', toggleLayout);
        }
        
        // Submit query button
        if (submitBtn) {
            submitBtn.addEventListener('click', () => sendQuery(queryInput.value));
        }
        
        // Follow-up query button
        if (followupBtn) {
            followupBtn.addEventListener('click', () => sendQuery(followupInput.value, true));
        }
        
        // Enter key in query input
        if (queryInput) {
            queryInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && e.ctrlKey) {
                    sendQuery(queryInput.value);
                }
            });
        }
        
        // Enter key in follow-up input
        if (followupInput) {
            followupInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && e.ctrlKey) {
                    sendQuery(followupInput.value, true);
                }
            });
        }
        
        // Enable summary checkbox
        if (enableSummaryCheckbox) {
            enableSummaryCheckbox.addEventListener('change', (e) => {
                enableSummary = e.target.checked;
                localStorage.setItem('enable-summary', enableSummary);
            });
        }
        
        // Window resize event for responsive layout
        window.addEventListener('resize', updateMainContentLayout);
    }
    
    function openApiTesterPanel(providerId = '') {
        if (apiTesterPanel) {
            apiTesterPanel.classList.add('open');
            
            // If a provider ID was specified, select it
            if (providerId && apiTestProviderSelect) {
                apiTestProviderSelect.value = providerId;
            }
        }
    }
    
    async function testAPIKey() {
        const provider = apiTestProviderSelect.value;
        const apiKey = apiTestKeyInput.value;
        
        if (!provider || !apiKey) {
            showToast('Please select a provider and enter an API key', 'error');
            return;
        }
        
        // Show loading state
        testApiBtn.disabled = true;
        testApiBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Testing...';
        apiTestResult.classList.add('hidden');
        
        try {
            const response = await fetch('/api/validate-key', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    provider,
                    api_key: apiKey
                })
            });
            
            const data = await response.json();
            
            // Show result
            apiTestResult.classList.remove('hidden');
            
            if (data.valid) {
                apiTestResult.innerHTML = `
                    <div class="flex items-center">
                        <i class="fas fa-check-circle text-green-500 mr-2"></i>
                        <span>${data.message}</span>
                    </div>
                `;
                
                // Save the API key
                localStorage.setItem(`${provider}-key`, apiKey);
                
                // Update saved keys display
                renderSavedAPIKeys();
                
                // Update model selectors (to enable the checkbox)
                renderModelSelectors();
                
                // Auto-enable the model
                if (!activeModels.includes(provider)) {
                    toggleModelActive(provider, true);
                }
                
                // Clear the input
                apiTestKeyInput.value = '';
            } else {
                apiTestResult.innerHTML = `
                    <div class="flex items-center">
                        <i class="fas fa-times-circle text-red-500 mr-2"></i>
                        <span>${data.message}</span>
                    </div>
                `;
            }
        } catch (error) {
            console.error('Error testing API key:', error);
            
            apiTestResult.classList.remove('hidden');
            apiTestResult.innerHTML = `
                <div class="flex items-center">
                    <i class="fas fa-exclamation-triangle text-yellow-500 mr-2"></i>
                    <span>Error testing API key: ${error.message}</span>
                </div>
            `;
        } finally {
            // Reset button
            testApiBtn.disabled = false;
            testApiBtn.innerHTML = '<i class="fas fa-vial mr-2"></i> Test API Key';
        }
    }
    
    function saveAllAPIKeys() {
        const providers = Object.keys(availableModels);
        let savedCount = 0;
        
        // Collect API keys from the API tester panel
        const providerSelect = apiTestProviderSelect.value;
        const apiKey = apiTestKeyInput.value;
        
        if (providerSelect && apiKey) {
            localStorage.setItem(`${providerSelect}-key`, apiKey);
            savedCount++;
            apiTestKeyInput.value = '';
        }
        
        // Show success message
        showToast(savedCount > 0 ? 
            `${savedCount} API key(s) saved successfully` : 
            'No new API keys to save');
        
        // Update UI
        renderSavedAPIKeys();
        renderModelSelectors();
    }
    
    function toggleLayout() {
        if (currentLayout === 'grid') {
            // Switch to column layout
            responsesContainer.classList.remove('md:grid-cols-2', 'xl:grid-cols-3');
            responsesContainer.classList.add('grid-cols-1');
            currentLayout = 'column';
            toggleLayoutBtn.innerHTML = '<i class="fas fa-th-large"></i>';
        } else {
            // Switch to grid layout
            responsesContainer.classList.remove('grid-cols-1');
            responsesContainer.classList.add('md:grid-cols-2', 'xl:grid-cols-3');
            currentLayout = 'grid';
            toggleLayoutBtn.innerHTML = '<i class="fas fa-columns"></i>';
        }
    }
    
    function updateActiveModelsCount() {
        if (!activeModelsCount) return;
        
        let count = 0;
        
        // Count active models with API keys
        activeModels.forEach(modelId => {
            if (localStorage.getItem(`${modelId}-key`)) count++;
        });
        
        activeModelsCount.textContent = `${count} models active`;
    }
    
    function addToQueryHistory(query) {
        // Add to beginning of array (most recent first)
        queryHistory.unshift({
            query,
            timestamp: new Date().toISOString()
        });
        
        // Limit to last 10 queries
        if (queryHistory.length > 10) {
            queryHistory = queryHistory.slice(0, 10);
        }
        
        // Save to localStorage
        localStorage.setItem('query-history', JSON.stringify(queryHistory));
        
        // Re-render the history
        renderQueryHistory();
    }
    
    function renderQueryHistory() {
        if (!queryHistoryContainer) return;
        
        queryHistoryContainer.innerHTML = '';
        
        if (queryHistory.length === 0) {
            queryHistoryContainer.innerHTML = '<div class="text-gray-500 text-sm">No queries yet</div>';
            return;
        }
        
        queryHistory.forEach((item, index) => {
            const historyItem = document.createElement('div');
            historyItem.className = 'query-history-item text-gray-300 text-sm hover:bg-terminal-bg rounded';
            
            // Format date nicely
            const date = new Date(item.timestamp);
            const formattedDate = date.toLocaleString();
            
            // Truncate query if too long
            const truncatedQuery = item.query.length > 30 
                ? item.query.substring(0, 30) + '...' 
                : item.query;
            
            historyItem.innerHTML = `
                <div class="font-medium">${truncatedQuery}</div>
                <div class="text-gray-500 text-xs">${formattedDate}</div>
            `;
            
            historyItem.addEventListener('click', () => {
                queryInput.value = item.query;
                sidebar.classList.remove('open');
                queryInput.focus();
                updateMainContentLayout();
            });
            
            queryHistoryContainer.appendChild(historyItem);
        });
    }
    
    async function sendQuery(query, isFollowUp = false) {
        console.log('⚙️ SendQuery function called with query:', query, 'isFollowUp:', isFollowUp);
        query = query.trim();
        
        if (!query) {
            console.error('❌ Empty query provided');
            showToast('Please enter a query', 'error');
            return;
        }
        
        // Save the current query
        currentQuery = query;
        console.log('📌 Current query saved:', currentQuery);
        
        // Add to query history if not a follow-up
        if (!isFollowUp) {
            addToQueryHistory(query);
            console.log('📚 Added to query history');
        }
        
        // Collect API keys and models
        const apiKeys = {};
        console.log('🔑 Active models to check for API keys:', activeModels);
        
        // Get API keys for all active models
        activeModels.forEach(modelId => {
            const savedKey = localStorage.getItem(`${modelId}-key`);
            const savedModel = localStorage.getItem(`${modelId}-model`) || 
                               (availableModels[modelId] && availableModels[modelId].models[0].id);
            
            console.log(`🔐 Checking API key for ${modelId}: ${savedKey ? 'Found' : 'Not found'}`);
            console.log(`📋 Model selected for ${modelId}: ${savedModel || 'None'}`);
            
            if (savedKey && savedModel) {
                apiKeys[modelId] = {
                    key: savedKey,
                    model: savedModel
                };
                // Don't log the full API key for security
                console.log(`✅ Added API config for ${modelId} with model ${savedModel}`);
            }
        });
        
        console.log(`📊 Total API keys found: ${Object.keys(apiKeys).length}`);
        
        if (Object.keys(apiKeys).length === 0) {
            console.error('❌ No API keys found');
            showToast('Please add at least one API key', 'error');
            openApiTesterPanel();
            return;
        }
        
        // Show loading indicator
        console.log('⏳ Showing loading indicator');
        loadingIndicator.classList.remove('hidden');
        responsesContainer.classList.add('hidden');
        followupContainer.classList.add('hidden');
        summaryContainer.classList.add('hidden');
        
        // Clear previous responses
        console.log('🧹 Clearing previous responses');
        activeModels.forEach(modelId => {
            const responseElement = document.getElementById(`${modelId}-response`);
            if (responseElement) {
                responseElement.innerHTML = '';
            } else {
                console.warn(`⚠️ Response element for ${modelId} not found in DOM`);
            }
        });
        
        try {
            console.log('🚀 Sending API request to /api/query');
            console.log('📦 Request payload:', {
                query,
                api_keys_count: Object.keys(apiKeys).length,
                summarize: enableSummary
            });
            
            const response = await fetch('/api/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    query,
                    api_keys: apiKeys,
                    summarize: enableSummary
                }),
                credentials: 'include'
            });
            
            console.log(`🔄 Response status: ${response.status} ${response.statusText}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            console.log('✅ Response received, parsing JSON');
            const data = await response.json();
            console.log('📡 Response data:', data);
            
            // Display responses for each model
            console.log(`🖥️ Processing responses for ${Object.keys(data).length} models`);
            Object.keys(data).forEach(modelId => {
                if (modelId === 'summary') {
                    console.log('📑 Processing summary response');
                    // Handle summary separately
                    handleSummaryResponse(data[modelId]);
                    return;
                }
                
                console.log(`🤖 Processing response for ${modelId}`);
                const modelElement = document.getElementById(`${modelId}-container`);
                const modelDisplay = document.getElementById(`${modelId}-model-display`);
                const responseElement = document.getElementById(`${modelId}-response`);
                
                if (!modelElement) console.warn(`⚠️ Model container for ${modelId} not found in DOM`);
                if (!modelDisplay) console.warn(`⚠️ Model display for ${modelId} not found in DOM`);
                if (!responseElement) console.warn(`⚠️ Response element for ${modelId} not found in DOM`);
                
                if (modelDisplay && responseElement) {
                    // Show the proper model used
                    modelDisplay.textContent = apiKeys[modelId] ? 
                        `(${apiKeys[modelId].model})` : '';
                    
                    console.log(`🔍 Response status for ${modelId}: ${data[modelId].status}`);
                    if (data[modelId].status === 'success') {
                        console.log(`✅ Setting HTML content for ${modelId} (${data[modelId].content.length} chars)`);
                        responseElement.innerHTML = marked.parse(data[modelId].content);
                    } else {
                        console.error(`❌ Error response for ${modelId}: ${data[modelId].content}`);
                        responseElement.innerHTML = `<div class="text-red-500">${data[modelId].content}</div>`;
                    }
                    
                    // Ensure the container is visible
                    if (modelElement) {
                        console.log(`👁️ Making model container for ${modelId} visible`);
                        modelElement.classList.remove('hidden');
                    }
                }
            });
            
            // Show responses container
            console.log('👁️ Making responses container visible');
            responsesContainer.classList.remove('hidden');
            
            // Show follow-up container
            console.log('👁️ Making followup container visible');
            followupContainer.classList.remove('hidden');
            
            // Clear follow-up input if this was a follow-up
            if (isFollowUp) {
                console.log('🧹 Clearing followup input');
                followupInput.value = '';
            }
            
            // Auto-hide sidebar on mobile after getting results
            if (window.innerWidth < 768) {
                console.log('📱 Auto-hiding sidebar on mobile');
                sidebar.classList.remove('open');
                updateMainContentLayout();
            }
        } catch (error) {
            console.error('❌ Error fetching responses:', error);
            showToast(`Error: ${error.message}`, 'error');
        } finally {
            console.log('⏳ Hiding loading indicator');
            // Hide loading indicator
            loadingIndicator.classList.add('hidden');
        }
    }
    
    function handleSummaryResponse(summaryData) {
        if (!summaryContainer || !summaryContent || !enableSummary) return;
        
        if (summaryData.status === 'success') {
            summaryContent.innerHTML = marked.parse(summaryData.content);
            summaryContainer.classList.remove('hidden');
        } else {
            // If there was an error but the user wanted a summary, show the error
            summaryContent.innerHTML = `<div class="text-red-500">${summaryData.content}</div>`;
            summaryContainer.classList.remove('hidden');
        }
    }
    
    function copyToClipboard(text) {
        navigator.clipboard.writeText(text).catch(err => {
            console.error('Could not copy text: ', err);
        });
    }
    
    function showToast(message, type = 'success') {
        if (!toast || !toastMessage) return;
        
        // Set message
        toastMessage.textContent = message;
        
        // Set icon based on type
        const iconElement = toast.querySelector('i');
        if (iconElement) {
            iconElement.className = type === 'success' 
                ? 'fas fa-check-circle text-neon-primary mr-2' 
                : type === 'error' 
                    ? 'fas fa-exclamation-circle text-red-400 mr-2'
                    : 'fas fa-info-circle text-neon-accent mr-2';
        }
        
        // Show toast
        toast.classList.remove('translate-y-20', 'opacity-0');
        toast.classList.add('translate-y-0', 'opacity-100');
        
        // Hide toast after 3 seconds
        setTimeout(() => {
            toast.classList.remove('translate-y-0', 'opacity-100');
            toast.classList.add('translate-y-20', 'opacity-0');
        }, 3000);
    }
});
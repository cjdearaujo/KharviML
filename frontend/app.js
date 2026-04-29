document.addEventListener('DOMContentLoaded', () => {
    const API_BASE_URL = 'http://127.0.0.1:8000';
    
    // UI Elements
    const form = document.getElementById('predictionForm');
    const btnReset = document.getElementById('btnReset');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const resultCard = document.getElementById('resultCard');
    const errorCard = document.getElementById('errorCard');
    
    const resultValue = document.getElementById('resultValue');
    const resultUnit = document.getElementById('resultUnit');
    const resultTitle = document.getElementById('resultTitle');
    const resultDetails = document.getElementById('resultDetails');
    const resultIcon = document.getElementById('resultIcon');
    
    const errorMessage = document.getElementById('errorMessage');
    const apiStatusDot = document.getElementById('apiStatusDot');
    const apiStatusText = document.getElementById('apiStatusText');

    let currentEndpoint = null;

    // Check API Status
    async function checkApiStatus() {
        try {
            const response = await fetch(`${API_BASE_URL}/health`);
            if (response.ok) {
                apiStatusDot.className = 'status-indicator online';
                apiStatusText.textContent = 'API Online';
            } else {
                throw new Error('API not OK');
            }
        } catch (error) {
            apiStatusDot.className = 'status-indicator offline';
            apiStatusText.textContent = 'API Offline';
        }
    }

    // Run health check initially
    checkApiStatus();

    // Button event listeners to set endpoint
    document.getElementById('btnPredictPrice').addEventListener('click', (e) => {
        currentEndpoint = e.currentTarget.getAttribute('data-endpoint');
    });

    document.getElementById('btnPredictCatch').addEventListener('click', (e) => {
        currentEndpoint = e.currentTarget.getAttribute('data-endpoint');
    });

    // Reset button
    btnReset.addEventListener('click', () => {
        form.reset();
        hideAllCards();
    });

    // Form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        if (!currentEndpoint) return;

        // Gather and parse form data
        const formData = new FormData(form);
        const payload = {
            species: formData.get('species'),
            fishing_area: formData.get('fishing_area'),
            month: parseInt(formData.get('month'), 10),
            weight_g: parseFloat(formData.get('weight_g')),
            length_cm: parseFloat(formData.get('length_cm')),
            width_cm: parseFloat(formData.get('width_cm')),
            height_cm: parseFloat(formData.get('height_cm')),
            age_years: parseInt(formData.get('age_years'), 10),
            quality_score: parseFloat(formData.get('quality_score')),
            season_availability: parseFloat(formData.get('season_availability')),
            cost_tl: parseFloat(formData.get('cost_tl')),
            wind_speed_kmh: parseFloat(formData.get('wind_speed_kmh')),
            sea_surface_temp_c: parseFloat(formData.get('sea_surface_temp_c')),
            active_fishing_days: parseInt(formData.get('active_fishing_days'), 10),
            fishing_ban_flag: parseInt(formData.get('fishing_ban_flag'), 10)
        };

        await submitPrediction(currentEndpoint, payload);
    });

    async function submitPrediction(endpoint, payload) {
        showLoading();

        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Failed to get prediction');
            }

            showResult(endpoint, data);

        } catch (error) {
            showError(error.message || 'Unable to connect to the prediction API.');
        }
    }

    function showLoading() {
        resultCard.classList.add('hidden');
        errorCard.classList.add('hidden');
        loadingOverlay.classList.remove('hidden');
    }

    function hideAllCards() {
        resultCard.classList.add('hidden');
        errorCard.classList.add('hidden');
        loadingOverlay.classList.add('hidden');
    }

    function showError(message) {
        loadingOverlay.classList.add('hidden');
        resultCard.classList.add('hidden');
        
        errorMessage.textContent = message;
        errorCard.classList.remove('hidden');
    }

    function showResult(endpoint, data) {
        loadingOverlay.classList.add('hidden');
        errorCard.classList.add('hidden');

        // Configure Result UI based on endpoint
        if (endpoint === '/predict/price') {
            resultTitle.textContent = 'Predicted Price';
            resultIcon.textContent = 'payments';
            resultValue.textContent = data.predicted_price_TL.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
            resultUnit.textContent = 'TL';
        } else if (endpoint === '/predict/catch') {
            resultTitle.textContent = 'Predicted Catch Volume';
            resultIcon.textContent = 'phishing';
            resultValue.textContent = data.predicted_catch_tonnes.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
            resultUnit.textContent = 'Tonnes';
        }

        // Populate details
        resultDetails.innerHTML = `
            <div class="detail-row">
                <span class="detail-label">Species</span>
                <span class="detail-value">${data.species}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Area</span>
                <span class="detail-value">${data.fishing_area}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Month</span>
                <span class="detail-value">${data.month}</span>
            </div>
        `;

        resultCard.classList.remove('hidden');
    }
});

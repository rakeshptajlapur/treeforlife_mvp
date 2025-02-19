// Initialize map
const map = L.map('map', {
    minZoom: 4,
    maxZoom: 8,
    zoomControl: true,
    attributionControl: false
}).setView([23.5937, 78.9629], 5);

// Use a cleaner base map
L.tileLayer('https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png', {
    bounds: [[8.4, 68.7], [37.6, 97.25]],
}).addTo(map);

// Restrict map panning to India
map.setMaxBounds([[8.4, 68.7], [37.6, 97.25]]);

// Custom marker icon with ripple effect
const customIcon = L.divIcon({
    className: 'custom-marker',
    html: `
        <div class="marker-container">
            <div class="marker-pin"></div>
            <div class="marker-ripple"></div>
        </div>
    `,
    iconSize: [30, 30],
    iconAnchor: [15, 30]
});

// Add markers and restore autosuggest
const searchInput = document.getElementById('search-input');
const suggestions = new Set();

// Add markers for plantations
plantationData.forEach(plantation => {
    // Add to suggestions set
    suggestions.add(plantation.name);
    suggestions.add(plantation.state);
    suggestions.add(plantation.owner);
    suggestions.add(plantation.company);

    const marker = L.marker([plantation.location.lat, plantation.location.lng], {
        icon: customIcon
    }).addTo(map);

    const stateCount = plantationData.filter(p => p.state === plantation.state).length;
    
    marker.bindTooltip(`
        <div style="font-family: 'Poppins', sans-serif;">
            <a href="#${plantation.name.toLowerCase().replace(/\s+/g, '-')}" 
               style="text-decoration: none; color: inherit;">
                <strong>${plantation.name}</strong><br>
                ${plantation.state}<br>
                <small>${stateCount} plantation${stateCount > 1 ? 's' : ''} in ${plantation.state}</small>
            </a>
        </div>
    `, {
        offset: [0, -15],
        direction: 'top'
    });

    marker.on('click', function() {
        window.location.href = `#${plantation.name.toLowerCase().replace(/\s+/g, '-')}`;
    });
});

// Update stats
document.getElementById('states-count').textContent = [...new Set(plantationData.map(item => item.state))].length;
document.getElementById('plantations-count').textContent = plantationData.length;
document.getElementById('owners-count').textContent = [...new Set(plantationData.map(item => item.owner))].length;
document.getElementById('companies-count').textContent = [...new Set(plantationData.map(item => item.company))].length;

// Create custom dropdown for search
function createSearchDropdown() {
    const dropdownContainer = document.createElement('div');
    dropdownContainer.className = 'search-dropdown';
    dropdownContainer.style.display = 'none';
    document.querySelector('.search-container').appendChild(dropdownContainer);
    return dropdownContainer;
}

// Handle suggestion click
function handleSuggestionClick(suggestion) {
    searchInput.value = suggestion.text;
    dropdownContainer.style.display = 'none';

    // Clear existing markers
    map.eachLayer((layer) => {
        if (layer instanceof L.Marker) {
            map.removeLayer(layer);
        }
    });

    // Add filtered markers
    plantationData.forEach(plantation => {
        if (suggestion.type === 'state' && plantation.state === suggestion.text) {
            addMarker(plantation);
        } else if (suggestion.type === 'plantation' && plantation.name === suggestion.text) {
            addMarker(plantation);
            // Center map on selected plantation
            map.setView([plantation.location.lat, plantation.location.lng], 7);
        }
    });
}

// Add marker function
function addMarker(plantation) {
    const marker = L.marker([plantation.location.lat, plantation.location.lng], {
        icon: customIcon
    }).addTo(map);

    marker.bindTooltip(`
        <div style="font-family: 'Poppins', sans-serif;">
            <strong>${plantation.name}</strong><br>
            ${plantation.state}<br>
            <small>Owner: ${plantation.owner}</small><br>
            <small>Company: ${plantation.company}</small>
        </div>
    `, {
        offset: [0, -15],
        direction: 'top'
    });
}

// Format suggestion item
function createSuggestionItem(suggestion) {
    return `
        <div class="suggestion-item" data-type="${suggestion.type}" data-text="${suggestion.text}">
            <div class="suggestion-icon">${suggestion.type === 'state' ? '🌳' : '🏡'}</div>
            <div class="suggestion-text">
                <div class="suggestion-main">${suggestion.text}</div>
                ${suggestion.type === 'state' 
                    ? `<div class="suggestion-sub">${suggestion.count} plantation${suggestion.count > 1 ? 's' : ''}</div>`
                    : `<div class="suggestion-sub">${suggestion.state}</div>`}
            </div>
        </div>
    `;
}

// Search functionality with custom dropdown
const dropdownContainer = createSearchDropdown();

searchInput.addEventListener('input', (e) => {
    const searchTerm = e.target.value.toLowerCase();
    if (searchTerm.length < 1) {
        dropdownContainer.style.display = 'none';
        return;
    }

    // Generate suggestions
    const suggestions = [];
    
    // Add state suggestions
    const states = [...new Set(plantationData.map(item => item.state))];
    states.forEach(state => {
        if (state.toLowerCase().includes(searchTerm)) {
            const count = plantationData.filter(p => p.state === state).length;
            suggestions.push({
                type: 'state',
                text: state,
                count: count
            });
        }
    });

    // Add plantation suggestions
    plantationData.forEach(plantation => {
        if (plantation.name.toLowerCase().includes(searchTerm)) {
            suggestions.push({
                type: 'plantation',
                text: plantation.name,
                state: plantation.state
            });
        }
    });

    // Update dropdown
    if (suggestions.length > 0) {
        dropdownContainer.innerHTML = suggestions.map(suggestion => 
            createSuggestionItem(suggestion)
        ).join('');
        dropdownContainer.style.display = 'block';

        // Add click handlers to suggestions
        document.querySelectorAll('.suggestion-item').forEach(item => {
            item.addEventListener('click', () => {
                handleSuggestionClick({
                    type: item.dataset.type,
                    text: item.dataset.text
                });
            });
        });
    } else {
        dropdownContainer.style.display = 'none';
    }
});

// Close dropdown when clicking outside
document.addEventListener('click', (e) => {
    if (!e.target.closest('.search-container')) {
        dropdownContainer.style.display = 'none';
    }
});

// Initial load of all markers
plantationData.forEach(plantation => addMarker(plantation));

// Enhanced marker highlight with ripple effect
function createHighlightedMarker(lat, lng) {
    const highlightedIcon = L.divIcon({
        className: 'custom-marker-highlighted',
        html: `
            <div style="
                background-color: #ff4444;
                width: 24px;
                height: 24px;
                border-radius: 50%;
                border: 3px solid white;
                box-shadow: 0 0 8px rgba(255,0,0,0.5);
            "></div>
            <div class="ripple-effect" style="
                width: 24px;
                height: 24px;
            "></div>
        `,
        iconSize: [24, 24],
        iconAnchor: [12, 12]
    });

    return L.marker([lat, lng], {
        icon: highlightedIcon
    }).addTo(map);
}

// Add after your existing code
const resetButton = document.getElementById('reset-button');

function resetMap() {
    // Clear search input
    searchInput.value = '';
    
    // Hide dropdown
    dropdownContainer.style.display = 'none';
    
    // Clear existing markers
    map.eachLayer((layer) => {
        if (layer instanceof L.Marker) {
            map.removeLayer(layer);
        }
    });
    
    // Reset map view to initial position
    map.setView([23.5937, 78.9629], 5);
    
    // Re-add all markers
    plantationData.forEach(plantation => addMarker(plantation));
}

// Add click handler for reset button
resetButton.addEventListener('click', resetMap);

// Add after your map initialization
const mapStyleToggle = document.getElementById('mapStyleToggle');
const focusText = document.querySelector('.focus-text');
const detailedText = document.querySelector('.detailed-text');

// Define map styles
const focusStyle = 'https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png';
const detailedStyle = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';

// Initialize with detailed mode
let currentLayer = L.tileLayer(detailedStyle, {
    bounds: [[8.4, 68.7], [37.6, 97.25]]
}).addTo(map);

detailedText.classList.add('active');
focusText.classList.remove('active');

mapStyleToggle.addEventListener('change', function() {
    // Remove current layer
    map.removeLayer(currentLayer);
    
    if (this.checked) {
        // Detailed map
        currentLayer = L.tileLayer(detailedStyle, {
            bounds: [[8.4, 68.7], [37.6, 97.25]]
        }).addTo(map);
        detailedText.classList.add('active');
        focusText.classList.remove('active');
    } else {
        // Focus mode
        currentLayer = L.tileLayer(focusStyle, {
            bounds: [[8.4, 68.7], [37.6, 97.25]]
        }).addTo(map);
        focusText.classList.add('active');
        detailedText.classList.remove('active');
    }
}); 
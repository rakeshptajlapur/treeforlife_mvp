// Initialize map when document is ready
document.addEventListener('DOMContentLoaded', function() {
    // ... all your existing JavaScript code ...
     // Initialize map
     const indiaBounds = [
        [8.4, 68.7],
        [37.6, 97.25]
    ];

    const map = L.map('map', {
        maxBounds: indiaBounds,
        maxBoundsViscosity: 1.0,
        minZoom: 4,
        maxZoom: 18
    }).fitBounds(indiaBounds);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    // Remove this line as we're getting data from window object
    // const plantationData = {{ plantation_data|safe }};
    
    // Instead, use the global variable
    const plantationData = window.plantationData;

    // Search functionality
    const searchInput = document.querySelector('.search-input');
    const suggestionsContainer = document.querySelector('.search-suggestions');

    searchInput.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase();
        
        if (searchTerm.length < 2) {
            suggestionsContainer.style.display = 'none';
            return;
        }

        const matches = plantationData.filter(p => 
            p.name.toLowerCase().includes(searchTerm) ||
            p.state.toLowerCase().includes(searchTerm) ||
            p.owner.toLowerCase().includes(searchTerm)
        );

        if (matches.length > 0) {
            suggestionsContainer.innerHTML = matches.map(p => `
                <div class="suggestion-item" data-lat="${p.latitude}" data-lng="${p.longitude}">
                    <strong>${p.name}</strong><br>
                    <small>${p.state} | ${p.owner}</small>
                </div>
            `).join('');
            suggestionsContainer.style.display = 'block';
        } else {
            suggestionsContainer.style.display = 'none';
        }
    });

    suggestionsContainer.addEventListener('click', (e) => {
        const item = e.target.closest('.suggestion-item');
        if (item) {
            const lat = parseFloat(item.dataset.lat);
            const lng = parseFloat(item.dataset.lng);
            map.setView([lat, lng], 15);
            suggestionsContainer.style.display = 'none';
            searchInput.value = item.querySelector('strong').textContent;
        }
    });

    // Custom marker icon with ripple
    const createMarkerIcon = () => {
        return L.divIcon({
            className: 'custom-marker',
            html: `
                <div class="marker-container">
                    <div class="marker-pin"></div>
                    <div class="marker-ripple"></div>
                </div>
            `,
            iconSize: [32, 32],
            iconAnchor: [16, 16],
            popupAnchor: [0, -16]
        });
    };
                // Add markers with custom icon, tooltip, and popup
        const markers = plantationData.map(plantation => {
            if (!plantation.latitude || !plantation.longitude) {
                console.warn(`Missing coordinates for plantation: ${plantation.name}`);
                return null;
            }

            try {
                const marker = L.marker([plantation.latitude, plantation.longitude], {
                    icon: createMarkerIcon()
                }).addTo(map);

                // Add hover tooltip (brief info)
                marker.bindTooltip(`
                    <div class="marker-tooltip">
                        <strong>${plantation.name}</strong><br>
                        ${plantation.state}
                    </div>
                `, {
                    direction: 'top',
                    offset: [0, -20],
                    permanent: false
                });

                // Add clickable popup (detailed info)
                marker.bindPopup(`
                    <div class="marker-popup">
                        <h4>${plantation.name}</h4>
                        <p><strong>ID:</strong> ${plantation.plantation_id}</p>
                        <p><strong>Location:</strong> ${plantation.latitude}, ${plantation.longitude}</p>
                        <p><strong>State:</strong> ${plantation.state}</p>
                        <p><strong>Owner:</strong> ${plantation.owner}</p>
                        ${plantation.company ? `<p><strong>Company:</strong> ${plantation.company}</p>` : ''}
                        <a href="/plantation-details/${plantation.id}/" class="popup-link">
                            View Plantation Details →
                        </a>
                    </div>
                `, {
                    maxWidth: 320,
                    className: 'custom-popup',
                    closeButton: true
                });

                // Handle marker click
                marker.on('click', function(e) {
                    // Close any other open popups
                    map.closeTooltip();
                });

                return marker;
            } catch (error) {
                console.error(`Error creating marker for plantation: ${plantation.name}`, error);
                return null;
            }
        }).filter(Boolean);

    // Map style toggle
    const mapStyleToggle = document.getElementById('mapStyleToggle');
    const focusStyle = 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png';
    const detailedStyle = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
    let currentLayer = null;

    function updateMapStyle(isFocusMode) {
        if (currentLayer) {
            map.removeLayer(currentLayer);
        }

        currentLayer = L.tileLayer(isFocusMode ? focusStyle : detailedStyle, {
            attribution: isFocusMode ? '© CartoDB' : '© OpenStreetMap contributors'
        }).addTo(map);
    }

    mapStyleToggle.addEventListener('change', (e) => {
        updateMapStyle(e.target.checked);
    });

    // Initialize with detailed map
    updateMapStyle(false);

    // Reset functionality
    document.getElementById('resetButton').addEventListener('click', () => {
        // Reset search
        searchInput.value = '';
        suggestionsContainer.style.display = 'none';
        
        // Reset map view
        map.fitBounds(indiaBounds);
        
        // Reset map style
        mapStyleToggle.checked = false;
        updateMapStyle(false);
    });

});
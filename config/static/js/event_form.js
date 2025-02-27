let timeoutId;

function updateAddressSuggestions() {
    const city = document.getElementById('city').value;
    const address = document.getElementById('location').value;
    const suggestions = document.getElementById('suggestions');

    clearTimeout(timeoutId);

    if (address.length < 3) {
        suggestions.style.display = 'none';
        return;
    }

    let query = city ? `${city}, ${address}` : address;

    suggestions.innerHTML = '<li class="loading">Searching addresses...</li>';
    suggestions.style.display = 'block';

    timeoutId = setTimeout(() => {
        fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&countrycodes=gb&addressdetails=1`)
            .then(response => response.json())
            .then(data => {
                suggestions.innerHTML = '';
                if (data.length > 0) {
                    data.forEach(place => {
                        const li = document.createElement('li');
                        li.textContent = place.display_name;
                        li.onclick = () => {
                            document.getElementById('location').value = place.display_name;
                            document.getElementById('latitude').value = place.lat;
                            document.getElementById('longitude').value = place.lon;
                            suggestions.style.display = 'none';
                        };
                        suggestions.appendChild(li);
                    });
                } else {
                    suggestions.innerHTML = '<li class="no-results">No addresses found. Try a different search.</li>';
                }
            })
            .catch(() => {
                suggestions.innerHTML = '<li class="error">Error loading suggestions</li>';
            });
    }, 300);
}

function validateForm() {
    const lat = document.getElementById('latitude').value;
    const lng = document.getElementById('longitude').value;

    if (!lat || !lng) {
        alert('Please select a valid address from the suggestions');
        return false;
    }
    return true;
}

document.addEventListener('click', (e) => {
    if (!e.target.closest('.form-group')) {
        document.getElementById('suggestions').style.display = 'none';
    }
});

let mapInitialized = false;

function initializeMap() {
    if (!mapInitialized) {
        var mapContainer = document.getElementById("map");

        window.map = L.map('map').setView([51.505, -0.09], 13);

        L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            minZoom: 5,
            zoom: 10,
            attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        }).addTo(map);

        var marker = L.marker([51.5, -0.09]).addTo(map);
        marker.bindPopup("<b>Hello world!</b><br>I am a popup.").openPopup();

        mapInitialized = true;
    }
}
    
window.resizeMap = function() {
    setTimeout(() => {
        if (typeof window.map !== "undefined") {
            window.map.invalidateSize();
        }
    }, 300);
}
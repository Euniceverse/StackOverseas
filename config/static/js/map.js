let mapInitialized = false;
let map;
let marker; // Used for searched location
let markers = [];

// Clear all markers from the map
function clearMarkers() {
  markers.forEach(m => map.removeLayer(m));
  markers = [];
}

// Open the event detail modal and update its content
function openEventModal(event) {
  document.getElementById("event-name").textContent = event.name || "No name provided";
  document.getElementById("event-type").textContent = event.event_type || "Event Type";

  if (event.start_datetime) {
    let startDate = new Date(event.start_datetime);
    document.getElementById("event-date").textContent = "📅 Date: " + startDate.toISOString().split("T")[0];
    document.getElementById("event-time").textContent = "⏰ Time: " + startDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  } else {
    document.getElementById("event-date").textContent = "📅 Date: Not specified";
    document.getElementById("event-time").textContent = "⏰ Time: Not specified";
  }

  document.getElementById("event-location").textContent = "📍 Location: " + (event.address || "Not specified");
  document.getElementById("event-fee").textContent = (event.fee && event.fee !== "Free") ? "💰 Fee: " + event.fee + " USD" : "💰 Fee: Free";
  document.getElementById("event-description").textContent = event.description || "No description available.";

  // Show the modal (assumes a modal element with id "event-detail-modal")
  document.getElementById("event-detail-modal").classList.remove("hidden");
}

// Load events from the given URL and add markers to the map
function loadEvents(url) {
  clearMarkers();
  fetch(url)
    .then(response => response.json())
    .then(events => {
      events.forEach(event => {
        if (event.latitude && event.longitude) {
          let m = L.marker([event.latitude, event.longitude]).addTo(map);
          markers.push(m);
          m.on("click", () => openEventModal(event));
          m.bindPopup(`<b>${event.name}</b><br>${event.address}`);
        }
      });
    })
    .catch(error => console.error("Error loading events:", error));
}

// Initialize the map (runs only once)
function initializeMap() {
  if (mapInitialized) return;

  // Create the map in the container with id "map"
  map = L.map("map").setView([51.5074, -0.1278], 10);

  // Add OpenStreetMap tiles
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap contributors"
  }).addTo(map);

  // Load the initial set of event markers
  loadEvents("/api/events/");
  mapInitialized = true;
}

// Update the map using filters (e.g. from a filter component)
function updateMapWithFilters(filters) {
  if (!mapInitialized) {
    initializeMap();
  }
  // Update markers based on the filtered events from your API
  loadEvents(`/events/api/${filters}`);
}

// Update the map based on a searched location stored in localStorage
function updateMap() {
  if (!mapInitialized) {
    initializeMap();
  }
  clearMarkers();
  const savedLocation = localStorage.getItem("searchedLocation");
  if (savedLocation) {
    const { lat, lon, name } = JSON.parse(savedLocation);
    map.setView([lat, lon], 15);
    if (marker) {
      marker.setLatLng([lat, lon]);
    } else {
      marker = L.marker([lat, lon]).addTo(map);
    }
    marker.bindPopup(`<b>${name}</b>`).openPopup();
  }
  // Optionally reload the events after updating the map view
  loadEvents("/api/events/");
  setTimeout(() => map.invalidateSize(), 300);
}

// Event listeners for initializing and updating the map
document.addEventListener("DOMContentLoaded", initializeMap);
document.addEventListener("filtersUpdated", function (e) {
  updateMapWithFilters(e.detail);
});
window.addEventListener("updateMap", updateMap);

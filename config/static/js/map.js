let mapInitialized = false;
let map;
let marker; // Used for searched location
let markers = [];

// Clear all markers from the map
function clearMarkers() {
  markers.forEach(m => map.removeLayer(m));
  markers = [];
}

function openEventModal(event) {
  // Set visible modal content
  document.getElementById("event-name").textContent = event.name || "No name provided";
  document.getElementById("event-type").textContent = event.event_type || "Event Type";

  if (event.start_datetime) {
      const startDate = new Date(event.start_datetime);
      document.getElementById("event-date").textContent = "📅 Date: " + startDate.toISOString().split("T")[0];
      document.getElementById("event-time").textContent = "⏰ Time: " + startDate.toLocaleTimeString([], {
          hour: "2-digit", minute: "2-digit"
      });
  } else {
      document.getElementById("event-date").textContent = "📅 Date: Not specified";
      document.getElementById("event-time").textContent = "⏰ Time: Not specified";
  }

  // Ensure fee is treated as a number. If fee is "Free" or 0, use 0. Otherwise parse it.
  let feeValue;
  if (event.fee === undefined || event.fee === null || event.fee === "Free" || event.fee === "0" || Number(event.fee) === 0) {
      feeValue = 0.0;
  } else {
      feeValue = parseFloat(event.fee);
  }
  const feeText = feeValue === 0.0 ? "💰 Fee: Free" : `💰 Fee: £${feeValue.toFixed(2)}`;
  document.getElementById("event-fee").textContent = feeText;

  document.getElementById("event-location").textContent = "📍 Location: " + (event.address || "Not specified");
  document.getElementById("event-description").textContent = event.description || "No description available.";

  // Display Host (Society)
  document.getElementById("event-hosts").textContent = event.hosts || "TBA";  // Make sure to use the hosts data

  // Display Capacity
  document.getElementById("event-capacity").textContent = "👥 Capacity: " + (event.capacity || "Unlimited");

  // Set the hidden form fields for the Register Now button
  document.getElementById("event-id-input").value = event.id;
  document.getElementById("event-name-input").value = event.name || "Unnamed Event";
  document.getElementById("event-price-input").value = feeValue;  // numeric value: 0.0 or the actual fee
  document.getElementById("event-description-input").value = event.description || "No description available.";

  // Show the modal
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

  // const myEventsFilter = new URLSearchParams(window.location.search).get("my_events");
  // let initialURL = "/api/events/";
  // if (myEventsFilter === "true") {
  //   initialURL = "/events/api/?my_events=true";
  // }
  
  // loadEvents(initialURL);

  mapInitialized = true;

  updateMapWithFilters("");
  updateMap();
}

// Update the map using filters (e.g. from a filter component)
function updateMapWithFilters(filters) {
  if (!mapInitialized) {
    initializeMap();
  }
  // Update markers based on the filtered events from your API
  let queryString = localStorage.getItem("filterQueryString") || "";

  const myEventsFilterUrl = new URLSearchParams(window.location.search).get('my_events'); 
  const myEventsFilterStorage = localStorage.getItem("my_events"); 
  if (myEventsFilterUrl === "true" || myEventsFilterStorage === "true") { 
      queryString += (queryString ? '&' : '?') + 'my_events=true';
  }

  console.log("🗺️ Map - Query String:", queryString);

  fetch(`/events/api/${queryString}`)
    .then(response => response.json())
    .then(data => {
      console.log("🗺️ Map - Raw Events Data:", data);
      loadEvents(`/events/api/${queryString}`);
    })
    .catch(error => console.error("Error loading events:", error));
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

  let queryString = localStorage.getItem("filterQueryString") || "";
  const myEventsFilterUrl = new URLSearchParams(window.location.search).get('my_events');
  const myEventsFilterStorage = localStorage.getItem("my_events");
  if (myEventsFilterUrl === "true" || myEventsFilterStorage === "true") {
    queryString += (queryString ? '&' : '?') + 'my_events=true';
  }
  
  loadEvents(`/events/api/${queryString}`);
  setTimeout(() => map.invalidateSize(), 300);
}

// Event listeners for initializing and updating the map
document.addEventListener("DOMContentLoaded", initializeMap);
document.addEventListener("filtersUpdated", function (e) {
  updateMapWithFilters(e.detail);
});
window.addEventListener("updateMap", updateMap);
window.list.refetchEvents();
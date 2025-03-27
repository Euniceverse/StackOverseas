let mapInitialized = false;
let map;
let marker; 
let markers = [];

function clearMarkers() {
  markers.forEach(m => map.removeLayer(m));
  markers = [];
}

function openEventModal(event) {
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

  document.getElementById("event-hosts").textContent = event.hosts || "TBA";  // Make sure to use the hosts data

  document.getElementById("event-capacity").textContent = "👥 Capacity: " + (event.capacity || "Unlimited");

  document.getElementById("event-id-input").value = event.id;
  document.getElementById("event-name-input").value = event.name || "Unnamed Event";
  document.getElementById("event-price-input").value = feeValue;  // numeric value: 0.0 or the actual fee
  document.getElementById("event-description-input").value = event.description || "No description available.";

  document.getElementById("event-detail-modal").classList.remove("hidden");
}

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

function initializeMap() {
  if (mapInitialized) return;

  map = L.map("map").setView([51.5074, -0.1278], 10);

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

function updateMapWithFilters(filters) {
  if (!mapInitialized) {
    initializeMap();
  }
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

document.addEventListener("DOMContentLoaded", initializeMap);
document.addEventListener("filtersUpdated", function (e) {
  updateMapWithFilters(e.detail);
});

window.addEventListener("updateMap", updateMap);
window.list.refetchEvents();
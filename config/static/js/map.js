let mapInitialized = false;
let map, marker;
let markers = [];
const eventDetailModal = document.getElementById("event-detail-modal");

function initializeMap() {
    if (mapInitialized) return;

    const map = L.map('map').setView([51.5074, -0.1278], 10);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    function loadEvents(url) {
        fetch(url)
            .then(response => response.json())
            .then(events => {
                events.forEach(event => {
                    if (event.latitude && event.longitude) {
                        const marker = L.marker([event.latitude, event.longitude]).addTo(map);
                        marker.bindPopup(`<b>${event.name}</b><br>${event.address}`);
                    }
                });
            })
            .catch(error => console.error('Error loading events:', error));
    }

    loadEvents('/api/events/');

    document.addEventListener("filtersUpdated", function(event) {
        map.eachLayer((layer) => {
            if (layer instanceof L.Marker) {
                map.removeLayer(layer);
            }
        });
        loadEvents(`/events/api/${event.detail}`);
    });

    mapInitialized = true;
}

function fetchEventLocations() {
  fetch('/api/events/')
      .then(response => {
          if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
          return response.json();
      })
      .then(events => {
          console.log("📍 Events Data:", events);
          // Check if events is wrapped in a results object
          const eventsList = events.results || events;
          eventsList.forEach(event => addEventMarker(event));
      })
      .catch(error => console.error("❌ Fetch Error:", error));
}
function addEventMarker(event) {
    if (!map || !event.latitude || !event.longitude) {
        console.warn("⚠️ Invalid map state or coordinates for event:", event);
        return;
    }

    const newMarker = L.marker([event.latitude, event.longitude])
        .addTo(map)
        .bindPopup(`<b>${event.name}</b><br>${event.address}`)


    markers.push(newMarker);

    newMarker.on("click", () => {
        console.log("🖱️ Marker Interaction:", event);
        updateEventModal(event);
        eventDetailModal.classList.remove("hidden");
    });
}

function updateEventModal(event) {
    const formatDate = (dateStr) =>
        dateStr ? new Date(dateStr).toLocaleDateString() : "No date";

    const formatTime = (dateStr) =>
        dateStr ? new Date(dateStr).toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit'
        }) : "No time";

    document.getElementById("event-name").textContent = event.name;
    document.getElementById("event-type").textContent = event.event_type || "N/A";
    document.getElementById("event-date").textContent = formatDate(event.date);
    document.getElementById("event-time").textContent = formatTime(event.date);
    document.getElementById("event-location").textContent = event.address;  // ✅ Fixed to 'address'
    document.getElementById("event-fee").textContent =
        event.fee > 0 ? `£${event.fee}` : "Free";
    document.getElementById("event-description").textContent =
        event.description || "No description available";
}

function updateMapWithFilters(filters) {
    if (!mapInitialized) {
        console.warn("⚠️ Map is not initialized yet. Trying again...");
        initializeMap();
    }

    console.log("🔄 Updating map with filters:", filters);

    clearMarkers(); // ✅ 기존 마커 삭제

    fetch(`/events/api/${filters}`)  // ✅ 필터가 적용된 데이터 가져오기
        .then(response => response.json())
        .then(events => {
            console.log("📍 Filtered Events Loaded:", events);
            events.forEach(event => addEventMarker(event));
        })
        .catch(error => console.error("❌ Error fetching filtered events:", error));
}

// 🔹 검색 후 지도 업데이트 함수
function updateMap() {
    if (!mapInitialized) {
        console.warn("⚠️ Map is not initialized yet. Trying again...");
        initializeMap();
    }

    clearMarkers();

    const savedLocation = localStorage.getItem("searchedLocation");
    if (savedLocation) {
        const { lat, lon, name } = JSON.parse(savedLocation);

        if (map) {
            map.setView([lat, lon], 15);

            if (marker) {
                marker.setLatLng([lat, lon]);
            } else {
                marker = L.marker([lat, lon]).addTo(map);
            }

            marker.bindPopup(`<b>${name}</b>`).openPopup();
        } else {
            console.error("❌ Map is undefined when trying to update.");
        }
    }

    resizeMap();
}

function clearMarkers() {
    markers.forEach(marker => {
        map.removeLayer(marker); // 기존 마커 제거
    });
    markers = []; // 배열 초기화
}

// 🔹 지도 크기 조정
window.resizeMap = function() {
    setTimeout(() => {
        if (typeof window.map !== "undefined") {
            window.map.invalidateSize();
        }
    }, 300);
};

// 🔹 이벤트 리스너 등록
window.addEventListener("updateMap", updateMap);

document.addEventListener("filtersUpdated", function (event) {
    console.log("🗺 Map updating with filters:", event.detail);
    updateMapWithFilters(event.detail); // 필터 적용 후 지도 새로고침
    resizeMap();
});

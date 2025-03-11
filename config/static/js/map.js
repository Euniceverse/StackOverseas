let mapInitialized = false;
let map, marker;
let markers = [];
const eventDetailModal = document.getElementById("event-detail-modal");


function initializeMap() {
    if (!mapInitialized) {
        var mapContainer = document.getElementById("map");

        if (!mapContainer) {
            console.error("❌ Error: `#map` container is missing in HTML.");
            return;
        }

        // 🔹 Prevent duplicate map initialization
        if (mapContainer._leaflet_id !== undefined) {
            console.warn("⚠️ Map is already initialized. Skipping...");
            return;
        }

        map = L.map('map').setView([51.505, -0.09], 13);

        L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            minZoom: 5,
            zoom: 10,
            attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        }).addTo(map);

        mapInitialized = true;
        fetchEventLocations();  // 🔹 이벤트 데이터 가져오기
    }
}

// 🔹 서버에서 이벤트 위치 데이터를 가져와 지도에 추가
function fetchEventLocations() {
    fetch("/events/api/")
        .then(response => response.json())
        .then(events => {
            console.log("📍 Event Locations Loaded:", events);
            events.forEach(event => addEventMarker(event));
        })
        .catch(error => console.error("❌ Error fetching events:", error));
}

// 🔹 이벤트 위치 마커 추가 함수 (오타 수정 및 기능 추가)
function addEventMarker(event) {
    if (!map) {
        console.warn("⚠️ Map not initialized yet.");
        return;
    }

    // 오타 수정: latitue → latitude, longtitude → longitude
    if (!event.latitude || !event.longitude) {
        console.warn("⚠️ Missing latitude or longitude for event:", event);
        return;
    }

    const marker = L.marker([event.latitude, event.longitude]).addTo(map);
    markers.push(marker); // ✅ 새 마커를 markers 배열에 추가

    marker.addEventListener("click", function () {
        console.log("🖱️ Marker clicked:", event); // 🛠 데이터 구조 확인을 위한 로그 추가

        document.getElementById("event-name").textContent = event.name;
        document.getElementById("event-type").textContent = event.type || "No type available";
        document.getElementById("event-date").textContent = event.date
            ? new Date(event.date).toISOString().split("T")[0]
            : "No date available";
        document.getElementById("event-time").textContent = event.date
            ? new Date(event.date).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
            : "Time not specified";
        document.getElementById("event-location").textContent = event.location || "No location";
        document.getElementById("event-fee").textContent =
            event.fee && event.fee !== "Free" ? `${event.fee} USD` : "Free";
        document.getElementById("event-description").textContent =
            event.description || "No description available";

        // ✅ 모달 표시
        eventDetailModal.classList.remove("hidden");
    });
}

document.getElementById("event-detail-modal").addEventListener("click", function (event) {
    if (event.target === this) {
        this.classList.add("hidden");
    }
    event.stopPropagation();
});

const closeButton = document.getElementById("close-modal");
if (closeButton) {
    closeButton.addEventListener("click", function () {
        console.log("🔄 Close button clicked");
        eventDetailModal.classList.add("hidden");
    });
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
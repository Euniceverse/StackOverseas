let mapInitialized = false;
let map, marker;

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

        // document.getElementById('geoForm').addEventListener('submit', function(event) {
        //     event.preventDefault();
        //     var address = document.getElementById('address').value;

        //     fetch(`https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(address)}&format=json`)
        //         .then(response => response.json())
        //         .then(data => {
        //             if (data.length > 0) {
        //                 var lat = parseFloat(data[0].lat);
        //                 var lon = parseFloat(data[0].lon);

        //                 map.setView([lat, lon], 15);  // 지도 이동

        //                 if (marker) {
        //                     marker.setLatLng([lat, lon]);  // 기존 마커 이동
        //                 } else {
        //                     marker = L.marker([lat, lon]).addTo(map);  // 새로운 마커 추가
        //                 }

        //                 marker.bindPopup(`<b>${data[0].display_name}</b>`).openPopup();
        //             } else {
        //                 alert("주소를 찾을 수 없습니다.");
        //             }
        //         })
        //         .catch(error => console.log("지오코딩 요청 실패: ", error));
        // });

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

    marker.bindPopup(`
        <b>${event.name}</b><br>
        📍 ${event.location || "Unknown Location"}<br>
        📅 ${new Date(event.date).toLocaleDateString()}
    `);
}

// 🔹 검색 후 지도 업데이트 함수
function updateMap() {
    if (!mapInitialized) {
        console.warn("⚠️ Map is not initialized yet. Trying again...");
        initializeMap();
    }

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

// HTML 요소가 완전히 로드된 후 실행되도록 보장
document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ 문서가 로드되었습니다."); // 디버깅 로그 추가

    // HTML에서 id="mapContainer"가 존재하는지 확인
    var mapContainer = document.getElementById("mapContainer");
    if (!mapContainer) {
        console.error("❌ 'mapContainer' 요소를 찾을 수 없습니다. HTML을 확인하세요.");
        return;
    }

    // Leaflet 지도 초기화
    var map = L.map('mapContainer').setView([51.509865, -0.118092], 6); // 영국 중심 (런던)
    console.log("✅ 지도가 초기화되었습니다.");

    // OpenStreetMap 타일 레이어 추가
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 18
    }).addTo(map);
    console.log("✅ 타일 레이어가 추가되었습니다.");
});

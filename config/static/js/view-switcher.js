document.addEventListener("DOMContentLoaded", function () {
    const listButton = document.getElementById("list-button");
    const calendarButton = document.getElementById("calendar-button");
    const mapButton = document.getElementById("map-button");

    const listView = document.querySelector(".event-view-list");
    const calendarView = document.querySelector(".event-view-calendar");
    const mapView = document.querySelector(".event-view-map");

    if (!listButton || !calendarButton || !mapButton) {
        console.error("❌ ERROR: One or more buttons are missing!");
        return;
    }

    if (!listView || !calendarView || !mapView) {
        console.error("❌ ERROR: One or more views are missing!");
        return;
    }

    // ✅ Function to switch active view
    function switchView(activeButton, activeView) {
        console.log(`🔄 Switching to: ${activeButton.id}`);

        // 🔥 Remove "active" class from all buttons
        listButton.classList.remove("active");
        calendarButton.classList.remove("active");
        mapButton.classList.remove("active");

        // 🔥 Hide all views
        listView.style.display = "none";
        calendarView.style.display = "none";
        mapView.style.display = "none";

        // 🔥 Show selected view and highlight button
        activeButton.classList.add("active");
        activeView.style.display = "block";

        if (activeView === mapView) {
            initializeMap(); // 🌍 지도 최초 로드
            resizeMap();     // 🌍 지도 크기 재조정
        }
        if (activeView === calendarView) {
            initializeCalendar(); // 🌍 지도 최초 로드
            resizeCalendar();     // 🌍 지도 크기 재조정
        }
        if (activeView === listView) {
            initializeList(); // 🌍 지도 최초 로드
            resizeList();     // 🌍 지도 크기 재조정
        }
    }

    // ✅ Default view: CALENDAR
    switchView(calendarButton, calendarView);

    // ✅ Event listeners for each button
    listButton.addEventListener("click", function () {
        switchView(listButton, listView);
    });

    calendarButton.addEventListener("click", function () {
        switchView(calendarButton, calendarView);
    });

    mapButton.addEventListener("click", function () {
        switchView(mapButton, mapView);
    });
});


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

    function switchView(activeButton, activeView) {
        console.log(`🔄 Switching to: ${activeButton.id}`);

        listButton.classList.remove("active");
        calendarButton.classList.remove("active");
        mapButton.classList.remove("active");

        listView.style.display = "none";
        calendarView.style.display = "none";
        mapView.style.display = "none";

        activeButton.classList.add("active");
        activeView.style.display = "block";

        if (activeView === calendarView) {
            initializeCalendar();
            resizeCalendar();
        }
        if (activeView === listView) {
            initializeList();
            resizeList();
        }
        if (activeView === mapView) {
            initializeMap();
        }
    }

    switchView(calendarButton, calendarView);

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

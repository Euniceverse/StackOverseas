document.addEventListener("DOMContentLoaded", function () {
    const listButton = document.getElementById("list-button");
    const calendarButton = document.getElementById("calendar-button");
    const mapButton = document.getElementById("map-button");

    const listView = document.querySelector(".event-view-list");
    const calendarView = document.querySelector(".event-view-calendar");

    if (!listButton || !calendarButton || !mapButton) {
        console.error("❌ ERROR: One or more buttons are missing!");
        return;
    }

    if (!listView || !calendarView) {
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
    }

    switchView(calendarButton, calendarView);

    listButton.addEventListener("click", function () {
        switchView(listButton, listView);
    });

    calendarButton.addEventListener("click", function () {
        switchView(calendarButton, calendarView);
    });

    // Use the global variable that holds the URL for event_map
    mapButton.addEventListener("click", function () {
        window.location.href = window.eventMapUrl;
    });
});

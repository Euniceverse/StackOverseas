document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ FullCalendar is initializing...");

    // ✅ Ensure FullCalendar is available
    if (typeof FullCalendar === "undefined") {
        console.error("❌ FullCalendar is NOT loaded! Check script order.");
        return;
    }

    let calendarEl = document.getElementById("calendar");

    if (!calendarEl) {
        console.error("❌ ERROR: Calendar container is missing!");
        return;
    }

    let calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: "dayGridMonth",
        headerToolbar: {
            left: "prev,next today",
            center: "title",
            right: "dayGridMonth,timeGridWeek,timeGridDay",
        },
        events: "/api/events/", // ✅ Fetch events from API
    });

    calendar.render(); // ✅ Render the calendar
});

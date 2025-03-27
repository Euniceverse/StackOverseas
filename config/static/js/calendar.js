let calendarInitialized = false;

function initializeCalendar() {
    if (calendarInitialized) return;

    console.log("JS loaded! initializeCalendar() called.");

    const calendarEl = document.getElementById("calendarContainer");
    const eventCalendar = document.querySelector(".event-calendar");
    const closeButton = document.getElementById("event-detail-close");

    if (!calendarEl) {
        console.error("ERROR: Calendar container is missing!");
        return;
    }

    calendarInitialized = true;
    localStorage.removeItem("filterQueryString");

function fetchFilteredEvents(fetchInfo, successCallback, failureCallback) {
    let queryString = localStorage.getItem("filterQueryString") || "";

    const myEventsFilter = new URLSearchParams(window.location.search).get('my_events');
    if (myEventsFilter === "true") {
        queryString += (queryString ? '&' : '?') + 'my_events=true';
    }

    fetch(`/events/api/${queryString}`)
        .then(response => response.json())
        .then(data => {
            let eventsArray = Array.isArray(data) ? data : data.results;

            if (!eventsArray || !Array.isArray(eventsArray)) {
                console.error("API response error: `results` field missing", data);
                return;
            }

            let events = eventsArray.map(event => ({
                id: event.id,
                title: event.name,
                start: event.start_datetime,
                end: event.end_datetime,
                extendedProps: {
                    event_type: event.event_type.split(",")[0].trim().replace("(", "").replace("'", ""),
                    location: event.location || "Not specified",
                    fee: event.fee || "Free",
                    description: event.description || "No description available.",
                    capacity: event.capacity || "Unlimited",
                    member_only: event.member_only,
                    hosts: event.society.join(", "),
                    society_names: event.society_names                }
            }));

            successCallback(events);
        })
        .catch(error => {
            console.error("Error fetching events:", error);
            failureCallback(error);
        });
}


    window.calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: "dayGridMonth",
        headerToolbar: {
            left: "prev,next today",
            center: "title",
            right: "dayGridMonth,timeGridWeek,timeGridDay",
        },
        events: fetchFilteredEvents,
        eventClick: function (info) {
            console.log("🖱️ Event clicked:", info.event);

            document.getElementById("event-id-input").value = info.event.id;
            document.getElementById("event-name").textContent = info.event.title;
            document.getElementById("event-type").textContent = info.event.extendedProps.event_type;
            document.getElementById("event-date").textContent = info.event.start.toISOString().split("T")[0];
            document.getElementById("event-time").textContent = info.event.start
                ? info.event.start.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
                : "Time not specified";
            document.getElementById("event-location").textContent = info.event.extendedProps.location;

            const fee = info.event.extendedProps.fee;
            const feeText =
                fee === "Free" || fee === 0 || fee === "0"
                    ? "💰 Fee: Free"
                    : `💰 Fee: £${parseFloat(fee).toFixed(2)}`;
            document.getElementById("event-fee").textContent = feeText;

            document.getElementById("event-price-input").value =
                fee !== "Free" && fee !== "" ? parseFloat(fee) : 0.0;

            document.getElementById("event-description").textContent = info.event.extendedProps.description;
            document.getElementById("event-hosts").textContent =
            info.event.extendedProps.society_names?.join(", ") || "TBA";
            document.getElementById("event-capacity").textContent =
            "👥 Capacity: " + (info.event.extendedProps.capacity || "Unlimited");
            
            const modal = document.getElementById("event-detail-modal");
            if (modal) modal.classList.remove("hidden");
        }
    });

    window.calendar.render();

    if (closeButton) {
        closeButton.addEventListener("click", function () {
            console.log("🔄 Close button clicked (hiding modal)");

            if (eventCalendar) {
                eventCalendar.classList.remove("active");
            }

            const modal = document.getElementById("event-detail-modal");
            if (modal) modal.classList.add("hidden");
        });
    }

    const modalEl = document.getElementById("event-detail-modal");
    if (modalEl) {
        modalEl.addEventListener("click", function (evt) {
            if (evt.target === this) {
                this.classList.add("hidden");
            }
            evt.stopPropagation();
        });
    }

    document.addEventListener("filtersUpdated", function (evt) {
        console.log("🔄 Calendar updating with filters:", evt.detail);
        localStorage.setItem("filterQueryString", evt.detail);

        if (window.calendar) {
            console.log("📌 Removing old events & refetching new data");
            window.calendar.removeAllEvents();
            window.calendar.refetchEvents();
            window.calendar.updateSize();
        }
    });

    window.resizeCalendar = function () {
        setTimeout(() => {
            console.log("FullCalendar resizing");
            window.calendar.updateSize();
        }, 100);
    };
}

window.initializeCalendar = initializeCalendar;

document.addEventListener("DOMContentLoaded", function () {
    console.log("DOM fully loaded. Initializing calendar...");
    initializeCalendar();
});

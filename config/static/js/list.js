let listInitialized = false;

function initializeList() {
    if (listInitialized) return;

    let listEl = document.getElementById("listContainer");
    let eventList = document.querySelector(".event-list");
    let eventPanel = document.getElementById("event-detail");
    let closeButton = document.getElementById("event-detail-close");

    if (!listEl) {
        console.error("ERROR: List container is missing!");
        return;
    }

    listInitialized = true;

    localStorage.removeItem("filterQueryString");

    function fetchFilteredEvents(fetchInfo, successCallback, failureCallback) {
        let queryString = localStorage.getItem("filterQueryString") || "";
        console.log("📋 List - Query String:", queryString);

        fetch(`/events/api/${queryString}`)
            .then(response => response.json())
            .then(data => {
                console.log("📋 List - Raw Events Data:", data);

                let eventsArray = Array.isArray(data) ? data : data.results;

                if (!eventsArray || !Array.isArray(eventsArray)) {
                    console.error("API Not Responding: No field name `results`", data);
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
                        society_names: event.society_names
                    }
                }));

                console.log("Filtered Event (FullCalendar):", events);

                successCallback(events);
            })
            .catch(error => console.error("Error fetching events:", error));
    }


    window.list = new FullCalendar.Calendar(listEl, {
        initialView: "listWeek",
        headerToolbar: {
            left: "prev,next today",
            center: "title",
            right: "listWeek",
        },
        events: fetchFilteredEvents, 
        eventClick: function (info) {
            console.log("🖱️ Event clicked:", info.event);

            document.getElementById("event-name").textContent = info.event.title;
            document.getElementById("event-type").textContent = info.event.type;
            document.getElementById("event-date").textContent = info.event.start.toISOString().split("T")[0];
            document.getElementById("event-time").textContent =
                info.event.start
                    ? info.event.start.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                    : "Time not specified";
            document.getElementById("event-location").textContent = info.event.extendedProps.location;
            document.getElementById("event-fee").textContent =
                info.event.extendedProps.fee !== "Free" ? info.event.extendedProps.fee + " USD" : "Free";
            document.getElementById("event-description").textContent = info.event.extendedProps.description;
            document.getElementById("event-hosts").textContent =
            info.event.extendedProps.society_names?.join(", ") || "TBA";
            document.getElementById("event-capacity").textContent =
            "👥 Capacity: " + (info.event.extendedProps.capacity || "Unlimited");

            document.getElementById("event-detail-modal").classList.remove("hidden");
        }


    });


    window.list.render();

    if (closeButton) {
        closeButton.addEventListener("click", function () {
            console.log("🔄 Close button clicked");
            eventlist.classList.remove("active");
        });
    }

    if (closeButton) {
        closeButton.addEventListener("click", function () {
            console.log("🔄 Close button clicked");
            document.getElementById("event-detail-modal").classList.add("hidden");
        });
    }

    document.getElementById("event-detail-modal").addEventListener("click", function (event) {
        if (event.target === this) { 
            this.classList.add("hidden");
        }
        event.stopPropagation(); 
    });

    document.addEventListener("filtersUpdated", function (event) {
        console.log("🔄 Calendar updating with filters:", event.detail);
        localStorage.setItem("filterQueryString", event.detail);

        if (window.list) {
            console.log("FullCalendar Reload!");
            window.list.removeAllEvents(); 
            window.list.refetchEvents();  
            window.list.updateSize();  
        }
    });

    window.resizeList = function () {
        setTimeout(() => {
            console.log("FullCalendar resizing...");
            window.list.updateSize();
        }, 100);
    };


}

window.initializeList = initializeList;

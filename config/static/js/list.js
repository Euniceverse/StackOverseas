document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ FullCalendar List View is initializing...");

    let listEl = document.getElementById("listContainer");
    let eventCalendar = document.querySelector(".event-calendar");
    let eventPanel = document.getElementById("event-detail");
    let closeButton = document.getElementById("event-detail-close");

    if (!listEl) {
        console.error("❌ ERROR: List container is missing!");
        return;
    }

    // ✅ 🟢 페이지 로드 시 필터 초기화 (새로고침하면 초기 상태)
    localStorage.removeItem("filterQueryString");  // 🛑 기존 필터 제거

    // Function to fetch events dynamically
    function fetchFilteredEvents(fetchInfo, successCallback, failureCallback) {
        let queryString = localStorage.getItem("filterQueryString") || "";

        fetch(`/events/api/${queryString}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log("✅ Events API Response:", data);

                let events = data.results.map(event => {
                    let datePart = event.date.split("T")[0]; // Extract YYYY-MM-DD
                    let startDate = datePart + "T" + (event.start_time || "00:00:00");
                    let endDate = datePart + "T" + (event.end_time || event.start_time || "23:59:59");

                    return {
                        id: event.id,
                        title: event.name,
                        start: startDate,
                        end: endDate,
                        extendedProps: {
                            location: event.location || "Not specified",
                            fee: event.fee || "Free",
                            description: event.description || "No description available."
                        }
                    };
                });

                successCallback(events);
            })
            .catch(error => {
                console.error("❌ Error fetching events:", error);
                failureCallback(error);
            });
    }

    // Initialize FullCalendar for List View
    window.listView = new FullCalendar.Calendar(listEl, {
        initialView: "listWeek",
        headerToolbar: {
            left: "prev,next today",
            center: "title",
        },
        events: fetchFilteredEvents, // Use function to dynamically fetch events
        eventClick: function (info) {
            console.log("🖱️ Event clicked:", info.event);

            // ✅ Update Event Panel with Clicked Event Details
            document.getElementById("event-name").textContent = info.event.title;
            document.getElementById("event-date").textContent = info.event.start.toISOString().split("T")[0];
            document.getElementById("event-time").textContent =
                info.event.start
                    ? info.event.start.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                    : "Time not specified";
            document.getElementById("event-location").textContent = info.event.extendedProps.location;
            document.getElementById("event-fee").textContent =
                info.event.extendedProps.fee !== "Free" ? info.event.extendedProps.fee + " USD" : "Free";
            document.getElementById("event-description").textContent = info.event.extendedProps.description;

            // ✅ Show Event Panel
            eventCalendar.classList.add("active");
        }
    });

    window.listView.render();

    // ✅ Close Button Click: Hide Event Panel
    if (closeButton) {
        closeButton.addEventListener("click", function () {
            console.log("🔄 Close button clicked");
            eventCalendar.classList.remove("active");
        });
    }

    // ✅ Close event panel when clicking outside
    document.addEventListener("click", function (event) {
        if (!eventPanel.contains(event.target) && !event.target.closest(".fc-event")) {
            eventCalendar.classList.remove("active");
        }
    });

    // 🟢 Listen for filter updates & apply filters dynamically
    document.addEventListener("filtersUpdated", function (event) {
        console.log("🔄 List View updating with filters:", event.detail);
        localStorage.setItem("filterQueryString", event.detail);
        window.listView.refetchEvents();
    });

    // ✅ 🟢 필터를 초기화했으므로, 새로고침 후에도 `filtersUpdated` 이벤트를 트리거하지 않음
});

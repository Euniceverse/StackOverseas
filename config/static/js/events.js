document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ FullCalendar is initializing...");

    let calendarEl = document.getElementById("calendar");
    let eventCalendar = document.querySelector(".event-calendar");
    let eventPanel = document.getElementById("event-detail");
    let closeButton = document.getElementById("event-detail-close");

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
        events: function (fetchInfo, successCallback, failureCallback) {
            fetch("/events/api/")
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! Status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    console.log("✅ Events API Response:", data);

                    let events = data.results.map(event => {
                        // 1. Separate the date (e.g., "2025-02-17") from the time portion
                        //    (which we ignore) in event.date (e.g., "2025-02-17T07:32:06.961900Z")
                        let datePart = event.date.split("T")[0]; // "YYYY-MM-DD"

                        // 2. Construct valid ISO8601 date/time strings for FullCalendar:
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
        },
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

            // ✅ Show Event Panel & Shrink Calendar
            eventCalendar.classList.add("active");
        }
    });

    calendar.render();

    // ✅ Close Button Click: Reset Calendar & Hide Event Panel
    closeButton.addEventListener("click", function () {
        console.log("🔄 Close button clicked");
        eventCalendar.classList.remove("active");
    });
});


document.addEventListener("DOMContentLoaded", function () {
  var map = L.map("map").setView([51.5074, -0.1278], 10);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "&copy; OpenStreetMap contributors",
  }).addTo(map);

  fetch("/api/events/")
      .then((response) => response.json())
      .then((events) => {
          events.forEach((event) => {
              L.marker([event.latitude, event.longitude])
                  .addTo(map)
                  .bindPopup(`<b>${event.name}</b><br>${event.address}`);
          });
      })
      .catch((error) => console.error("Error loading events:", error));
});


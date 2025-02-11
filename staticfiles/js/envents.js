document.addEventListener('DOMContentLoaded', function () {
    console.log("✅ FullCalendar is initializing...");

    let calendarEl = document.getElementById('calendar');
    let slidePanel = document.getElementById("event-slide-panel");
    let calendarContainer = document.getElementById("calendar-container");

    if (!calendarEl) {
        console.error("❌ ERROR: Cannot find calendar.");
        return;
    }

    let calendar = new window.FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        eventClick: function(info) {
            // ✅ Load event details into the right panel
            document.getElementById("event-name").textContent = info.event.title;
            document.getElementById("event-date").textContent = info.event.start.toISOString().split("T")[0];
            document.getElementById("event-time").textContent = info.event.start.toISOString().split("T")[1] || "Time TBD";
            document.getElementById("event-location").textContent = info.event.extendedProps.location || "Location TBD";
            document.getElementById("event-fee").textContent = info.event.extendedProps.fee ? info.event.extendedProps.fee + " USD" : "Free";
            document.getElementById("event-description").textContent = info.event.extendedProps.description || "No description available.";

            // ✅ Open the panel (Sliding from right)
            slidePanel.style.right = "0";
            document.body.classList.add("panel-open");

            // ✅ Set event ID for join button
            let joinButton = document.getElementById("join-event");
            joinButton.onclick = function() {
                joinEvent(info.event.id);
            };
        },
        events: function(fetchInfo, successCallback, failureCallback) {
            fetch("/api/events/")  // ✅ Ensure your Django API URL is correct!
                .then(response => response.json())
                .then(data => {
                    console.log("✅ Events API Response:", data);

                    let events = data.results.map(event => ({
                        id: event.id,
                        title: event.name,
                        start: event.date + "T" + (event.start_time || "00:00:00"),
                        end: event.date + "T" + (event.end_time || "23:59:59"),
                        description: event.description,
                        location: event.location,
                        fee: event.fee
                    }));

                    successCallback(events);
                })
                .catch(error => {
                    console.error("❌ Error fetching events:", error);
                    failureCallback(error);
                });
        }
    });

    calendar.render();
});

function closePanel() {
    document.getElementById("event-slide-panel").style.right = "-350px";  // ✅ Hide the panel
    document.body.classList.remove("panel-open");
}

function joinEvent(eventId) {
    fetch(`/api/events/${eventId}/register/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify({ user_id: 1 })  // ✅ Change user ID dynamically
    })
    .then(response => response.json())
    .then(data => {
        alert("✅ Successfully joined the event!");  // Success message
    })
    .catch(error => {
        console.error("❌ Error joining event:", error);
        alert("❌ Failed to join the event.");
    });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        let cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            let cookie = cookies[i].trim();
            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

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
                .then(response => response.json())
                .then(data => {
                    console.log("✅ Events API Response:", data);

                    let events = data.results.map(event => ({
                        id: event.id,
                        title: event.name,
                        start: event.date + "T" + (event.start_time || "00:00:00"),
                        end: event.date + "T" + (event.end_time || "23:59:59"),
                        location: event.location,
                        fee: event.fee,
                        description: event.description
                    }));

                    successCallback(events);
                })
                .catch(error => {
                    console.error("❌ Error fetching events:", error);
                    failureCallback(error);
                });
        },
        eventClick: function (info) {
            console.log("🖱️ Event clicked:", info.event);

            // ✅ Event 정보 업데이트
            document.getElementById("event-name").textContent = info.event.title;
            document.getElementById("event-date").textContent = info.event.start.toISOString().split("T")[0];
            document.getElementById("event-time").textContent =
                info.event.start ? info.event.start.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : "Time not specified";
            document.getElementById("event-location").textContent = info.event.extendedProps.location || "Location not specified";
            document.getElementById("event-fee").textContent = info.event.extendedProps.fee ? info.event.extendedProps.fee + " USD" : "Free";
            document.getElementById("event-description").textContent = info.event.extendedProps.description || "No description available.";

            // ✅ 달력 크기를 줄이고 이벤트 패널 표시
            eventCalendar.classList.add("active");
        }
    });

    calendar.render();

    // ✅ 닫기 버튼 클릭 시 달력을 원래 크기로 되돌림
    closeButton.addEventListener("click", function () {
        console.log("🔄 Close button clicked");

        // ✅ 달력을 원래 크기로 복귀 & 이벤트 패널 숨기기
        eventCalendar.classList.remove("active");
    });
});


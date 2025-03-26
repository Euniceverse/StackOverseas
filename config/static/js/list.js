let listInitialized = false;

function initializeList() {
    if (listInitialized) return;

    let listEl = document.getElementById("listContainer");
    let eventList = document.querySelector(".event-list");
    let eventPanel = document.getElementById("event-detail");
    let closeButton = document.getElementById("event-detail-close");

    if (!listEl) {
        console.error("❌ ERROR: List container is missing!");
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

                // ✅ API 응답이 배열인지 확인
                let eventsArray = Array.isArray(data) ? data : data.results;

                if (!eventsArray || !Array.isArray(eventsArray)) {
                    console.error("❌ API 응답 오류: `results` 필드가 없음", data);
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
                        hosts: event.society.join(", ")
                    }
                }));

                console.log("🎯 필터링된 이벤트 (FullCalendar에 전달될 데이터):", events);

                // ✅ FullCalendar가 데이터를 정상적으로 수신하는지 확인
                successCallback(events);
            })
            .catch(error => console.error("❌ Error fetching events:", error));
    }


    window.list = new FullCalendar.Calendar(listEl, {
        initialView: "listWeek",
        headerToolbar: {
            left: "prev,next today",
            center: "title",
            right: "listWeek",
        },
        events: fetchFilteredEvents, // Use function to dynamically fetch events
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

            // ✅ 모달 보이기
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
        if (event.target === this) { // 모달 바깥 영역 클릭 시 닫기
            this.classList.add("hidden");
        }
        event.stopPropagation(); // 🌟 이벤트 전파 차단하여 다른 버튼 클릭 방해 방지
    });

    document.addEventListener("filtersUpdated", function (event) {
        console.log("🔄 Calendar updating with filters:", event.detail);
        localStorage.setItem("filterQueryString", event.detail);

        if (window.list) {
            console.log("📌 FullCalendar 기존 이벤트 삭제 및 새 데이터 로드!");
            window.list.removeAllEvents(); // ✅ 기존 데이터 삭제
            window.list.refetchEvents();   // ✅ 새로운 데이터 요청
            window.list.updateSize();      // ✅ 캘린더 강제 리렌더링
        }
    });

    window.resizeList = function () {
        setTimeout(() => {
            console.log("✅ FullCalendar resizing...");
            window.list.updateSize();
        }, 100);
    };


}

// 🚀 `window` 객체에 함수 등록하여 `viewSwitcher.js`에서 호출 가능하도록 설정
window.initializeList = initializeList;

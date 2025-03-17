let calendarInitialized = false;

function initializeCalendar() {
  if (calendarInitialized) return;

  console.log("✅ JS loaded! initializeCalendar() called.");

  let calendarEl = document.getElementById("calendarContainer");
  let eventCalendar = document.querySelector(".event-calendar");
  let eventPanel = document.getElementById("event-detail");
  let closeButton = document.getElementById("event-detail-close");

  if (!calendarEl) {
    console.error("❌ ERROR: Calendar container is missing!");
    return;
  }

  calendarInitialized = true;

  localStorage.removeItem("filterQueryString");

  function fetchFilteredEvents(fetchInfo, successCallback, failureCallback) {
    let queryString = localStorage.getItem("filterQueryString") || "";

    fetch(`/events/api/${queryString}`)
      .then((response) => response.json())
      .then((data) => {
        console.log("🔍 API 응답 확인:", data);

        // ✅ API 응답이 배열인지 확인
        let eventsArray = Array.isArray(data) ? data : data.results;

        if (!eventsArray || !Array.isArray(eventsArray)) {
          console.error("❌ API 응답 오류: `results` 필드가 없음", data);
          return;
        }

        let events = eventsArray.map((event) => ({
          id: event.id,
          title: event.name,
          start: event.start_datetime,
          end: event.end_datetime,
          extendedProps: {
            event_type: event.event_type
              .split(",")[0]
              .trim()
              .replace("(", "")
              .replace("'", ""),
            location: event.location || "Not specified",
            fee: event.fee || "Free",
            description: event.description || "No description available.",
            capacity: event.capacity || "Unlimited",
            member_only: event.member_only,
            hosts: event.society.join(", "),
          },
        }));

        console.log(
          "🎯 필터링된 이벤트 (FullCalendar에 전달될 데이터):",
          events
        );

        // ✅ FullCalendar가 데이터를 정상적으로 수신하는지 확인
        successCallback(events);
      })
      .catch((error) => console.error("❌ Error fetching events:", error));
  }

  window.calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: "dayGridMonth",
    headerToolbar: {
      left: "prev,next today",
      center: "title",
      right: "dayGridMonth,timeGridWeek,timeGridDay",
    },
    events: fetchFilteredEvents, // Use function to dynamically fetch events

    eventClick: function (info) {
      console.log("🖱️ Event clicked:", info.event);

      document.getElementById("event-name").textContent = info.event.title;
      document.getElementById("event-type").textContent = info.event.type;
      document.getElementById("event-date").textContent = info.event.start
        .toISOString()
        .split("T")[0];
      document.getElementById("event-time").textContent = info.event.start
        ? info.event.start.toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })
        : "Time not specified";
      document.getElementById("event-location").textContent =
        info.event.extendedProps.location;
      document.getElementById("event-fee").textContent =
        info.event.extendedProps.fee !== "Free"
          ? info.event.extendedProps.fee + " USD"
          : "Free";
      document.getElementById("event-description").textContent =
        info.event.extendedProps.description;
      // ✅ Update the Register Button with the correct event ID
      let registerButton = document.querySelector(".register-button");
      if (registerButton) {
        registerButton.href = `/payments/checkout/?type=event&id=${info.event.id}`;
        registerButton.dataset.eventId = info.event.id;
        console.log(`🔗 Register Button URL Updated: ${registerButton.href}`);
      } else {
        console.error("❌ ERROR: Register button not found!");
      }

      // ✅ Show the modal
      let eventModal = document.getElementById("event-detail-modal");
      if (eventModal) {
        eventModal.classList.remove("hidden");
      } else {
        console.error("❌ ERROR: Event modal not found in DOM!");
      }
    },
  });

  window.calendar.render();

  if (closeButton) {
    closeButton.addEventListener("click", function () {
      console.log("🔄 Close button clicked");
      //   eventCalendar.classList.remove("active");

      if (eventCalendar) {
        eventCalendar.classList.remove("active");
      } else {
        console.error(
          "❌ ERROR: `eventCalendar` is null or not found in the DOM!"
        );
      }
    });
  }

  if (closeButton) {
    closeButton.addEventListener("click", function () {
      //   console.log("🔄 Close button clicked");
      //   document.getElementById("event-detail-modal").classList.add("hidden");
      console.log("🔄 Close button clicked (hiding modal)");
      let modal = document.getElementById("event-detail-modal");
      if (modal) modal.classList.add("hidden");
    });
  }

  // Close modal if user clicks outside the modal content
  let modalEl = document.getElementById("event-detail-modal");
  if (modalEl) {
    modalEl.addEventListener("click", function (evt) {
      if (evt.target === this) {
        this.classList.add("hidden");
      }
      evt.stopPropagation();
    });
  }

  // Listen for custom "filtersUpdated" event
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

  // Optional: a function to manually resize the calendar
  window.resizeCalendar = function () {
    setTimeout(() => {
      console.log("✅ FullCalendar resizing...");
      window.calendar.updateSize();
    }, 100);
  };
}

// Expose our init function for other scripts
window.initializeCalendar = initializeCalendar;

document.addEventListener("DOMContentLoaded", function () {
  console.log("✅ DOM fully loaded. Initializing calendar...");
  initializeCalendar();
});

//   document
//     .getElementById("event-detail-modal")
//     .addEventListener("click", function (event) {
//       if (event.target === this) {
//         // 모달 바깥 영역 클릭 시 닫기
//         this.classList.add("hidden");
//       }
//       event.stopPropagation(); // 🌟 이벤트 전파 차단하여 다른 버튼 클릭 방해 방지
//     });

//   document.addEventListener("filtersUpdated", function (event) {
//     console.log("🔄 Calendar updating with filters:", event.detail);
//     localStorage.setItem("filterQueryString", event.detail);

//     if (window.calendar) {
//       console.log("📌 FullCalendar 기존 이벤트 삭제 및 새 데이터 로드!");
//       window.calendar.removeAllEvents(); // ✅ 기존 데이터 삭제
//       window.calendar.refetchEvents(); // ✅ 새로운 데이터 요청
//       window.calendar.updateSize(); // ✅ 캘린더 강제 리렌더링
//     }
//   });

//   window.resizeCalendar = function () {
//     setTimeout(() => {
//       console.log("✅ FullCalendar resizing...");
//       window.calendar.updateSize();
//     }, 100);
//   };
// }

// // 🚀 `window` 객체에 함수 등록하여 `viewSwitcher.js`에서 호출 가능하도록 설정
// window.initializeCalendar = initializeCalendar;

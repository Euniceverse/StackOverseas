document.addEventListener("DOMContentLoaded", function() {
    // Grab all Create-Event links that have data-create-event-url
    const allCreateEventLinks = document.querySelectorAll(".create-event-link");

    allCreateEventLinks.forEach(link => {
      link.addEventListener("click", function(e) {
        e.preventDefault(); // stop normal '#' navigation
        if (confirm("Are you sure you want to create an event?")) {
          const url = link.getAttribute("data-create-event-url");
          window.location.href = url; // Navigate to /events/create/<society_id>/
        }
      });
    });
  });

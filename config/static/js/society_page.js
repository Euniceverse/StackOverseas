document.addEventListener("DOMContentLoaded", function() {
    const createEventLink = document.getElementById("createEventLink");
    if (createEventLink) {
      createEventLink.addEventListener("click", function(event) {
        event.preventDefault(); // stop normal <a> navigation
        const isSure = confirm("Are you sure you want to create an event for this society?");
        if (isSure) {
          // If confirmed, redirect to the real URL stored in data-create-event-url
          const createUrl = createEventLink.getAttribute("data-create-event-url");
          window.location.href = createUrl;
        }
      });
    }
  });
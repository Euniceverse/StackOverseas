document.addEventListener("DOMContentLoaded", function() {
    const createBtn = document.getElementById("createEventSubmitBtn");
    const cancelBtn = document.getElementById("cancelCreateEventBtn");

    if (createBtn) {
      createBtn.addEventListener("click", function(e) {
        const sure = confirm("Are you sure you want to create this event?");
        if (!sure) {
          e.preventDefault(); // stop form submission
        }
      });
    }

    if (cancelBtn) {
      cancelBtn.addEventListener("click", function(e) {
        if (confirm("Are you sure you want to cancel?")) {
          // e.g. go back or redirect
          window.history.back();
        }
      });
    }
  });

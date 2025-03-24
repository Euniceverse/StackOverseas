document.addEventListener("DOMContentLoaded", function() {
  const createBtn = document.getElementById("createEventSubmitBtn");
  const cancelBtn = document.getElementById("cancelCreateSocietyBtn");

  if (createBtn) {
    createBtn.addEventListener("click", function(e) {
      const sure = confirm("Are you sure you want to create this society?");
      if (!sure) {
        e.preventDefault(); // stop form submission
      }
    });
  }

  if (cancelBtn) {
    cancelBtn.addEventListener("click", function(e) {
      if (confirm("Are you sure you want to cancel?")) {
        window.history.back();
      }
    });
  }
});

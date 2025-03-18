
document.addEventListener("DOMContentLoaded", function() {
    const publishBtn = document.getElementById("publishNewsBtn");
    const cancelBtn = document.getElementById("cancelNewsBtn");
  
    // Confirm "Publish / Save"
    if (publishBtn) {
      publishBtn.addEventListener("click", function(e) {
        const isSure = confirm("Are you sure you want to publish/save these news items?");
        if (!isSure) {
          e.preventDefault(); // stop the form submission
        }
      });
    }
  
    // Confirm "Cancel"
    if (cancelBtn) {
      cancelBtn.addEventListener("click", function() {
        const isSure = confirm("Are you sure you want to cancel?  Nothing will be published.");
        if (isSure) {
          window.location.href = "/events/";
        }
      });
    }
  });
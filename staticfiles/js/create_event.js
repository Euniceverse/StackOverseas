

document.addEventListener("DOMContentLoaded", function() {
    const submitBtn = document.getElementById("createEventSubmitBtn");
    const cancelBtn = document.getElementById("cancelCreateEventBtn");
  
    // Confirm "Create Event"
    if (submitBtn) {
      submitBtn.addEventListener("click", function(e) {
        const answer = confirm("Are you sure you want to create this event?");
        if (!answer) {
          e.preventDefault(); 
        }
      });
    }
  
    // Confirm "Cancel"
    if (cancelBtn) {
      cancelBtn.addEventListener("click", function() {
        const isSure = confirm("Are you sure you want to cancel?  You will lose any data you entered.");
        if (isSure) {
          window.history.back(); 
          // or: window.location.href = "{% url 'society_page' society.id %}";
        }
      });
    }
  });
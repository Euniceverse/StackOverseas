function populateEventModal(event) {
  // 🎯 Fallbacks for field differences (calendar uses `extendedProps`, map uses raw event)
  const id = event.id;
  const name = event.name || event.title || "No name provided";
  const eventType = event.event_type || event.extendedProps?.event_type || "Event Type";
  const start = event.start_datetime || event.start;
  const location = event.address || event.location || "Not specified";
  const fee = event.fee || event.extendedProps?.fee || "Free";
  const description = event.description || event.extendedProps?.description || "No description available.";
  const hosts = event.society?.join(", ") || event.extendedProps?.hosts || "TBA";

  // 🧾 Set visible modal content
  document.getElementById("event-name").textContent = name;
  document.getElementById("event-type").textContent = eventType;

  if (start) {
      const dateObj = new Date(start);
      document.getElementById("event-date").textContent = "📅 Date: " + dateObj.toISOString().split("T")[0];
      document.getElementById("event-time").textContent = "⏰ Time: " + dateObj.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  } else {
      document.getElementById("event-date").textContent = "📅 Date: Not specified";
      document.getElementById("event-time").textContent = "⏰ Time: Not specified";
  }

  document.getElementById("event-location").textContent = "📍 Location: " + location;

  const feeText = fee === "Free" || fee === 0 || fee === "0"
      ? "💰 Fee: Free"
      : `💰 Fee: £${parseFloat(fee).toFixed(2)}`;
  document.getElementById("event-fee").textContent = feeText;

  document.getElementById("event-description").textContent = description;
  document.getElementById("event-hosts").textContent = hosts;

  // 🕹️ Set hidden fields for Register button
  document.getElementById("event-id-input").value = id;
  document.getElementById("event-name-input").value = name;
  document.getElementById("event-price-input").value = fee !== "Free" && fee !== "" ? parseFloat(fee) : 0.0;
  document.getElementById("event-description-input").value = description;

  // 🎯 Show the modal
  document.getElementById("event-detail-modal").classList.remove("hidden");
}

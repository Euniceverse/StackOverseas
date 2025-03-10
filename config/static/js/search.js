document.addEventListener("DOMContentLoaded", function () {
    const searchContainer = document.getElementById("searchContainer");

    if (!searchContainer) {
        console.error("❌ Error: 'searchContainer' is missing in HTML.");
        return;
    }

    // 🔹 Create Search Input Field
    const searchInput = document.createElement("input");
    searchInput.setAttribute("type", "text");
    searchInput.setAttribute("placeholder", "Search for events!");
    searchInput.classList.add("search-input");

    // 🔹 Listen for "Enter" Key
    searchInput.addEventListener("keydown", function (event) {
        console.log(`🔍 Key Pressed: ${event.key}`);
        if (event.key === "Enter") {
            event.preventDefault();
            console.log("✅ Enter Key Detected - Triggering Search...");
            triggerSearch(searchInput.value.trim());
        }
    });

    function triggerSearch(query) {
        if (query === "") return;
        console.log(`🔍 Searching for: ${query}`);

        fetch(`https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(query)}&format=json`)
            .then(response => response.json())
            .then(data => {
                console.log("🔍 API Response:", data);
                if (data.length > 0) {
                    const lat = parseFloat(data[0].lat);
                    const lon = parseFloat(data[0].lon);

                    // 🔹 Store in localStorage and trigger update event
                    localStorage.setItem("searchedLocation", JSON.stringify({ lat, lon, name: data[0].display_name }));
                    window.dispatchEvent(new Event("updateMap"));  // Notify map.js
                } else {
                    alert("❌ Location not found.");
                }
            })
            .catch(error => console.error("❌ Geocoding API Error: ", error));
    }

    // 🔹 Append Search Input to Search Container
    searchContainer.appendChild(searchInput);
});
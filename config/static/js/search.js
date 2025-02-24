document.addEventListener("DOMContentLoaded", function () {
    const searchContainer = document.getElementById("searchContainer");

    if (!searchContainer) {
        console.error("❌ Error: `searchContainer` is missing in HTML.");
        return;
    }

    // Search terms for autocomplete
    const searchTerms = ["Art", "Academic", "Sports", "Culture", "Others", "Music", "Technology", "Education", "Health", "Science"];
    let selectedIndex = -1; // Tracks currently selected autocomplete option

    // 🔹 Create Search Input
    const searchInput = document.createElement("input");
    searchInput.setAttribute("type", "text");
    searchInput.setAttribute("placeholder", "Find your perfect one");
    searchInput.classList.add("search-input");

    // 🔹 Create Autocomplete List
    const autocompleteList = document.createElement("ul");
    autocompleteList.classList.add("autocomplete-list");

    // 🔹 Search Input Event Listener
    searchInput.addEventListener("input", function () {
        const query = searchInput.value.toLowerCase();
        autocompleteList.innerHTML = ""; // Clear previous results
        selectedIndex = -1; // Reset selection

        if (query.length === 0) {
            autocompleteList.style.display = "none";
            return;
        }

        // 🔹 Filter search terms based on input
        const filteredResults = searchTerms.filter(term => term.toLowerCase().includes(query));

        // 🔹 Populate the autocomplete list
        filteredResults.forEach((result, index) => {
            const listItem = document.createElement("li");
            listItem.textContent = result;
            listItem.setAttribute("data-index", index);

            // Click event: select item
            listItem.addEventListener("click", function () {
                searchInput.value = result;
                autocompleteList.innerHTML = "";
                autocompleteList.style.display = "none";
            });

            autocompleteList.appendChild(listItem);
        });

        // Show or hide autocomplete list
        autocompleteList.style.display = filteredResults.length > 0 ? "block" : "none";
    });

    // 🔹 Keyboard Navigation for Autocomplete List
    searchInput.addEventListener("keydown", function (event) {
        const items = autocompleteList.querySelectorAll("li");

        if (items.length === 0) return;

        if (event.key === "ArrowDown") {
            // Move down the list
            selectedIndex = (selectedIndex + 1) % items.length;
            updateActiveItem(items);
            event.preventDefault();
        } else if (event.key === "ArrowUp") {
            // Move up the list
            selectedIndex = (selectedIndex - 1 + items.length) % items.length;
            updateActiveItem(items);
            event.preventDefault();
        } else if (event.key === "Enter") {
            // Select the highlighted option
            if (selectedIndex >= 0 && selectedIndex < items.length) {
                searchInput.value = items[selectedIndex].textContent;
            }
            autocompleteList.innerHTML = "";
            autocompleteList.style.display = "none";
            searchInput.blur();


            triggerSearch(searchInput.value); // Execute search
            event.preventDefault();
        }
    });

    // 🔹 Highlight active item in dropdown
    function updateActiveItem(items) {
        items.forEach((item, index) => {
            if (index === selectedIndex) {
                item.classList.add("active");
                item.scrollIntoView({ block: "nearest" });
            } else {
                item.classList.remove("active");
            }
        });
    }

    // 🔹 Hide autocomplete when clicking outside
    document.addEventListener("click", function (event) {
        if (!searchContainer.contains(event.target)) {
            autocompleteList.style.display = "none";
        }
    });

    function triggerSearch(query) {
        if (query.trim() === "") return;
        console.log("🔍 Searching for:", query);
        // TODO: Redirect to search results page, call API, or filter results
    }

    // 🔹 Append elements to search container
    searchContainer.appendChild(searchInput);
    searchContainer.appendChild(autocompleteList);
});
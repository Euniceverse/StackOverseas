document.addEventListener("DOMContentLoaded", function () {
    const dropdownContainer = document.getElementById("dropdownContainer");

    if (!dropdownContainer) {
        console.error("❌ ERROR: `dropdownContainer` is missing in HTML.");
        return;
    }

    const dropdownData = [
        { label: "Category", options: ["Sports", "Academic", "Arts", "Cultural", "Social", "Other"] },
        { label: "Audience", options: ["General", "Members only"] },
        { label: "Location", options: ["London", "Manchester", "Birmingham", "Liverpool", "Online"] },
        { label: "Availability", options: ["Available", "Full", "Waiting List"] },
        { label: "Fee", options: ["Free", "Under £10", "£10 - £50", "£50 - £100", "£100+"] }
    ];

    const filterValueMapping = {
        "Sports": "event_type=('sports', 'Sports')",
        "Academic": "event_type=('academic', 'Academic')",
        "Arts": "event_type=('arts', 'Arts')",
        "Cultural": "event_type=('cultural', 'Cultural')",
        "Social": "event_type=('social', 'Social')",
        "Other": "event_type=('other', 'Other')",
    
        "General": "member_only=false",  // 아무 파라미터도 보내지 않는다면 ""로
        "Members only": "member_only=true",
    
        "London": "location=london",
        "Manchester": "location=manchester",
        "Birmingham": "location=birmingham",
        "Liverpool": "location=liverpool",
        "Online": "location=online",
    
        "Available": "availability=available",
        "Full": "availability=full",
        "Waiting List": "availability=waiting",
    
        // Fee 관련
        // fee=0 → free, fee_min=10&fee_max=50 → 10 ~ 50
        "Free": "fee_max=0",
        "Under £10": "fee_max=10",
        "£10 - £50": "fee_min=10&fee_max=50",
        "£50 - £100": "fee_min=50&fee_max=100",
        "£100+": "fee_min=100"
    };
    

    function createDropdown(label, options) {
        const container = document.createElement("div");
        container.classList.add("custom-dropdown");

        const selectedDiv = document.createElement("div");
        selectedDiv.classList.add("custom-selected");
        selectedDiv.setAttribute("tabindex", "0"); // Enable keyboard focus

        const selectedText = document.createElement("span");
        selectedText.classList.add("selected-text");
        selectedText.textContent = label;
        selectedDiv.appendChild(selectedText);

        const dropdownIcon = document.createElement("span");
        dropdownIcon.classList.add("dropdown-icon");
        dropdownIcon.textContent = "▼";
        selectedDiv.appendChild(dropdownIcon);

        const clearButton = document.createElement("span");
        clearButton.classList.add("clear-selection");
        clearButton.textContent = "✖";
        clearButton.style.display = "none";
        selectedDiv.appendChild(clearButton);

        const optionsList = document.createElement("ul");
        optionsList.classList.add("custom-options");

        options.forEach(optionText => {
            const option = document.createElement("li");
            option.textContent = optionText;
            option.setAttribute("tabindex", "0"); // Enable keyboard focus

            // 🟢 Apply filter on option click
            option.addEventListener("click", function () {
                applySelection(optionText, selectedText, selectedDiv, optionsList, dropdownIcon, clearButton);
            });

            // 🟢 Apply filter on Enter key
            option.addEventListener("keydown", function (event) {
                if (event.key === "Enter") {
                    event.preventDefault();
                    option.click(); // Simulate click on Enter
                }
            });

            optionsList.appendChild(option);
        });

        // Toggle dropdown on selectedDiv click
        selectedDiv.addEventListener("click", function () {
            optionsList.style.display = optionsList.style.display === "block" ? "none" : "block";
        });

        // 🟢 Apply filter when pressing Enter on selectedDiv
        selectedDiv.addEventListener("keydown", function (event) {
            if (event.key === "Enter") {
                event.preventDefault();
                const firstOption = optionsList.querySelector("li");
                if (firstOption) {
                    firstOption.click();
                }
            }
        });

        // 🟢 Clear selection (reset filter)
        clearButton.addEventListener("click", function (event) {
            event.stopPropagation();
            resetSelection(selectedText, selectedDiv, dropdownIcon, clearButton, label);
        });

        // Close dropdown when clicking outside
        document.addEventListener("click", function (event) {
            if (!container.contains(event.target)) {
                optionsList.style.display = "none";
            }
        });

        container.appendChild(selectedDiv);
        container.appendChild(optionsList);
        dropdownContainer.appendChild(container);
    }

    function applySelection(optionText, selectedText, selectedDiv, optionsList, dropdownIcon, clearButton) {
        selectedText.textContent = optionText;
        selectedDiv.classList.add("selected");
        optionsList.style.display = "none";

        dropdownIcon.style.display = "none";
        clearButton.style.display = "inline-block";

        // 🟢 Apply filters immediately
        applyFilters();
    }

    function resetSelection(selectedText, selectedDiv, dropdownIcon, clearButton, label) {
        selectedText.textContent = label;
        selectedDiv.classList.remove("selected");

        dropdownIcon.style.display = "inline-block";
        clearButton.style.display = "none";

        // 🟢 Apply filters immediately after clearing
        applyFilters();
    }

    function getFilterQueryString() {
        let queryParams = [];

        document.querySelectorAll(".custom-selected").forEach(selectedDiv => {
            const selectedText = selectedDiv.querySelector(".selected-text").textContent.trim();
            if (selectedText && filterValueMapping[selectedText]) {
                queryParams.push(filterValueMapping[selectedText]);
            }
        });

        return queryParams.length > 0 ? "?" + queryParams.join("&") : "";
    }

    function applyFilters() {
        let queryString = getFilterQueryString();
        console.log("🎯 Applying filters:", queryString);

        // 🔥 Send an event so `calendar.js` and `list.js` can update
        document.dispatchEvent(new CustomEvent("filtersUpdated", { detail: queryString }));
    }

    // Create dropdowns
    dropdownData.forEach(data => {
        createDropdown(data.label, data.options);
    });
});

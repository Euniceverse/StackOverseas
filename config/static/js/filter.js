// document.addEventListener("DOMContentLoaded", function () {
//     const dropdownContainer = document.getElementById("dropdownContainer");

//     if (!dropdownContainer) {
//         console.error("❌ ERROR: `dropdownContainer` is missing in HTML.");
//         return;
//     }

//     // 필터 드롭다운 데이터
//     const dropdownData = [
//         { label: "Category", options: ["Sports", "Academic", "Arts", "Cultural", "Social", "Other"] },
//         { label: "Audience", options: ["General", "Members only"] },
//         { label: "Location", options: ["London", "Manchester", "Birmingham", "Liverpool", "Online"] },
//         { label: "Availability", options: ["Available", "Full", "Waiting List"] }
//     ];

//     // 필터 값 매핑 (쿼리스트링 변환)
//     const filterValueMapping = {
//         "Sports": "event_type=sports",
//         "Academic": "event_type=academic",
//         "Arts": "event_type=arts",
//         "Cultural": "event_type=cultural",
//         "Social": "event_type=social",
//         "Other": "event_type=other",
    
//         "General": "member_only=false",
//         "Members only": "member_only=true",
    
//         "London": "location=london",
//         "Manchester": "location=manchester",
//         "Birmingham": "location=birmingham",
//         "Liverpool": "location=liverpool",
//         "Online": "location=online",
    
//         "Available": "availability=available",
//         "Full": "availability=full",
//         "Waiting List": "availability=waiting"
//     };

//     // ✅ 하나의 슬라이더에서 최소/최대 값 조절 가능
//     function createRangeSlider() {
//         const container = document.createElement("div");
//         container.classList.add("range-slider");
    
//         // ✅ 트랙 (슬라이더 배경)
//         const sliderTrack = document.createElement("div");
//         sliderTrack.classList.add("slider-track");
    
//         // ✅ 최소값 핸들
//         const minInput = document.createElement("input");
//         minInput.type = "range";
//         minInput.min = "0";
//         minInput.max = "100";
//         minInput.step = "5";
//         minInput.value = "0";
    
//         // ✅ 최대값 핸들
//         const maxInput = document.createElement("input");
//         maxInput.type = "range";
//         maxInput.min = "0";
//         maxInput.max = "100";
//         maxInput.step = "5";
//         maxInput.value = "100";
    
//         // ✅ 값 표시
//         const valueDisplay = document.createElement("span");
//         valueDisplay.textContent = "£0 - £100+";
//         valueDisplay.classList.add("slider-value");
    
//         // ✅ 슬라이더 트랙 및 핸들 위치 업데이트 함수
//         function updateSlider() {
//             let minVal = parseInt(minInput.value, 10);
//             let maxVal = parseInt(maxInput.value, 10);
    
//             // ⚠️ 최소값이 최대값을 넘지 않도록 조정
//             if (minVal > maxVal - 5) {
//                 minInput.value = maxVal - 5; 
//                 minVal = maxVal - 5;
//             }
    
//             // ✅ 트랙 위치 및 크기 조정
//             const minPercent = (minVal / 100) * 100;
//             const maxPercent = (maxVal / 100) * 100;
//             sliderTrack.style.left = minPercent + "%";
//             sliderTrack.style.width = (maxPercent - minPercent) + "%";
    
//             // ✅ 값 업데이트
//             valueDisplay.textContent = maxVal === 100 ? `£${minVal} - £100+` : `£${minVal} - £${maxVal}`;
    
//             // ✅ 필터 적용
//             applyFilters();
//         }
    
//         // ✅ 값 변경 시 필터 적용
//         minInput.addEventListener("input", updateSlider);
//         maxInput.addEventListener("input", updateSlider);
    
//         // ✅ 구성 요소 추가
//         container.appendChild(valueDisplay);
//         container.appendChild(sliderTrack);
//         container.appendChild(minInput);
//         container.appendChild(maxInput);
        
//         dropdownContainer.appendChild(container);
    
//         // ✅ 초기 슬라이더 트랙 위치 설정
//         updateSlider();
//     }    
    

// //     function createDropdown(label, options) {
// //         const container = document.createElement("div");
// //         container.classList.add("custom-dropdown");

// //         const selectedDiv = document.createElement("div");
// //         selectedDiv.classList.add("custom-selected");
// //         selectedDiv.setAttribute("tabindex", "0");

// //         const selectedText = document.createElement("span");
// //         selectedText.classList.add("selected-text");
// //         selectedText.textContent = label;
// //         selectedDiv.appendChild(selectedText);

// //         const dropdownIcon = document.createElement("span");
// //         dropdownIcon.classList.add("dropdown-icon");
// //         dropdownIcon.textContent = "▼";
// //         selectedDiv.appendChild(dropdownIcon);

// //         const clearButton = document.createElement("span");
// //         clearButton.classList.add("clear-selection");
// //         clearButton.textContent = "✖";
// //         clearButton.style.display = "none";
// //         selectedDiv.appendChild(clearButton);

// //         const optionsList = document.createElement("ul");
// //         optionsList.classList.add("custom-options");

// //         options.forEach(optionText => {
// //             const option = document.createElement("li");
// //             option.textContent = optionText;
// //             option.setAttribute("tabindex", "0");

// //             option.addEventListener("click", function () {
// //                 applySelection(optionText, selectedText, selectedDiv, optionsList, dropdownIcon, clearButton);
// //             });

// //             option.addEventListener("keydown", function (event) {
// //                 if (event.key === "Enter") {
// //                     event.preventDefault();
// //                     option.click();
// //                 }
// //             });

// //             optionsList.appendChild(option);
// //         });

// //         selectedDiv.addEventListener("click", function () {
// //             optionsList.style.display = optionsList.style.display === "block" ? "none" : "block";
// //         });

// //         clearButton.addEventListener("click", function (event) {
// //             event.stopPropagation();
// //             resetSelection(selectedText, selectedDiv, dropdownIcon, clearButton, label);
// //         });

// //         document.addEventListener("click", function (event) {
// //             if (!container.contains(event.target)) {
// //                 optionsList.style.display = "none";
// //             }
// //         });

// //         container.appendChild(selectedDiv);
// //         container.appendChild(optionsList);
// //         dropdownContainer.appendChild(container);
// //     }

//     // ✅ 드롭다운 생성 함수
//     function createDropdown(label, options) {
//         const container = document.createElement("div");
//         container.classList.add("custom-dropdown");

//         const selectedDiv = document.createElement("div");
//         selectedDiv.classList.add("custom-selected");
//         selectedDiv.setAttribute("tabindex", "0");

//         const selectedText = document.createElement("span");
//         selectedText.classList.add("selected-text");
//         selectedText.textContent = label;
//         selectedDiv.appendChild(selectedText);

//         const dropdownIcon = document.createElement("span");
//         dropdownIcon.classList.add("dropdown-icon");
//         dropdownIcon.textContent = "▼";
//         selectedDiv.appendChild(dropdownIcon);

//         const clearButton = document.createElement("span");
//         clearButton.classList.add("clear-selection");
//         clearButton.textContent = "✖";
//         clearButton.style.display = "none";
//         selectedDiv.appendChild(clearButton);

//         const optionsList = document.createElement("ul");
//         optionsList.classList.add("custom-options");

//         options.forEach(optionText => {
//             const option = document.createElement("li");
//             option.textContent = optionText;
//             option.setAttribute("tabindex", "0");

//             option.addEventListener("click", function () {
//                 applySelection(optionText, selectedText, selectedDiv, optionsList, dropdownIcon, clearButton);
//             });

//             option.addEventListener("keydown", function (event) {
//                 if (event.key === "Enter") {
//                     event.preventDefault();
//                     option.click();
//                 }
//             });

//             optionsList.appendChild(option);
//         });

//         selectedDiv.addEventListener("click", function () {
//             optionsList.style.display = optionsList.style.display === "block" ? "none" : "block";
//         });

//         clearButton.addEventListener("click", function (event) {
//             event.stopPropagation();
//             resetSelection(selectedText, selectedDiv, dropdownIcon, clearButton, label);
//         });

//         document.addEventListener("click", function (event) {
//             if (!container.contains(event.target)) {
//                 optionsList.style.display = "none";
//             }
//         });

//         container.appendChild(selectedDiv);
//         container.appendChild(optionsList);
//         dropdownContainer.appendChild(container);
//     }

//     function applySelection(optionText, selectedText, selectedDiv, optionsList, dropdownIcon, clearButton) {
//         selectedText.textContent = optionText;
//         selectedDiv.classList.add("selected");
//         optionsList.style.display = "none";

//         dropdownIcon.style.display = "none";
//         clearButton.style.display = "inline-block";

//         // ✅ 필터 적용 즉시 실행
//         applyFilters();
//     }


//     // ✅ 필터 적용 함수
//     function applyFilters() {
//         let queryString = getFilterQueryString();
//         console.log("🎯 Applying filters:", queryString);

//         document.dispatchEvent(new CustomEvent("filtersUpdated", { detail: queryString }));
//     }

//     // ✅ 필터 쿼리 생성
//     function getFilterQueryString() {
//         let queryParams = [];

//         document.querySelectorAll(".custom-selected").forEach(selectedDiv => {
//             const selectedText = selectedDiv.querySelector(".selected-text").textContent.trim();
//             if (selectedText && filterValueMapping[selectedText]) {
//                 queryParams.push(filterValueMapping[selectedText]);
//             }
//         });

//         // ✅ Fee 슬라이더 값 추가
//         const minInput = document.querySelector(".range-slider input:nth-of-type(1)");
//         const maxInput = document.querySelector(".range-slider input:nth-of-type(2)");
        
//         if (minInput && maxInput) {
//             const minFee = parseInt(minInput.value, 10);
//             const maxFee = parseInt(maxInput.value, 10);
//             queryParams.push(`fee_min=${minFee}&fee_max=${maxFee === 100 ? "" : maxFee}`);
//         }

//         return queryParams.length > 0 ? "?" + queryParams.join("&") : "";
//     }

//     // ✅ 페이지 로드 시 필터 UI 생성
//     dropdownData.forEach(data => {
//         createDropdown(data.label, data.options);
//     });

//     // ✅ 하나의 슬라이더에서 최소/최대값 조정 가능하게 추가!
//     createRangeSlider();
// });


document.addEventListener("DOMContentLoaded", function () {
    const dropdownContainer = document.getElementById("dropdownContainer");

    if (!dropdownContainer) {
        console.error("❌ ERROR: `dropdownContainer` is missing in HTML.");
        return;
    }

    // 필터 드롭다운 데이터
    const dropdownData = [
        { label: "Category", options: ["Sports", "Academic", "Arts", "Cultural", "Social", "Other"] },
        { label: "Audience", options: ["General", "Members only"] },
        { label: "Location", options: ["London", "Manchester", "Birmingham", "Liverpool", "Online"] },
        { label: "Availability", options: ["Available", "Full", "Waiting List"] }
    ];

    // 필터 값 매핑 (쿼리스트링 변환)
    const filterValueMapping = {
        "Sports": "event_type=sports",
        "Academic": "event_type=academic",
        "Arts": "event_type=arts",
        "Cultural": "event_type=cultural",
        "Social": "event_type=social",
        "Other": "event_type=other",
    
        "General": "member_only=false",
        "Members only": "member_only=true",
    
        "London": "location=london",
        "Manchester": "location=manchester",
        "Birmingham": "location=birmingham",
        "Liverpool": "location=liverpool",
        "Online": "location=online",
    
        "Available": "availability=available",
        "Full": "availability=full",
        "Waiting List": "availability=waiting"
    };

    // ✅ 최소/최대 Fee 슬라이더 추가
    function createFeeSlider() {
        const container = document.createElement("div");
        container.classList.add("custom-slider-container");

        // ✅ 최소값 슬라이더
        const minLabel = document.createElement("label");
        minLabel.textContent = "Min (£)";
        minLabel.classList.add("slider-label");

        const minSlider = document.createElement("input");
        minSlider.type = "range";
        minSlider.min = "0";
        minSlider.max = "100";
        minSlider.step = "5";
        minSlider.value = "0"; 

        const minValueDisplay = document.createElement("span");
        minValueDisplay.textContent = "£0";
        minValueDisplay.classList.add("slider-value");

        // ✅ 최대값 슬라이더
        const maxLabel = document.createElement("label");
        maxLabel.textContent = "Max (£)";
        maxLabel.classList.add("slider-label");

        const maxSlider = document.createElement("input");
        maxSlider.type = "range";
        maxSlider.min = "0";
        maxSlider.max = "100";
        maxSlider.step = "5";
        maxSlider.value = "100"; 

        const maxValueDisplay = document.createElement("span");
        maxValueDisplay.textContent = "£100+";
        maxValueDisplay.classList.add("slider-value");

        // ✅ 슬라이더 동작 설정
        function updateSliderValues() {
            let minVal = parseInt(minSlider.value, 10);
            let maxVal = parseInt(maxSlider.value, 10);

            if (minVal > maxVal) {
                minVal = maxVal;
                minSlider.value = minVal;
            }

            minValueDisplay.textContent = `£${minVal}`;
            maxValueDisplay.textContent = maxVal === 100 ? "£100+" : `£${maxVal}`;

            applyFilters();
        }

        // ✅ 슬라이더 값 변경 시 필터 적용
        minSlider.addEventListener("input", updateSliderValues);
        maxSlider.addEventListener("input", updateSliderValues);

        // ✅ 슬라이더 UI 추가
        container.appendChild(minLabel);
        container.appendChild(minSlider);
        container.appendChild(minValueDisplay);
        container.appendChild(maxLabel);
        container.appendChild(maxSlider);
        container.appendChild(maxValueDisplay);
        
        dropdownContainer.appendChild(container);
    }

    // ✅ 드롭다운 생성 함수
    function createDropdown(label, options) {
        const container = document.createElement("div");
        container.classList.add("custom-dropdown");

        const selectedDiv = document.createElement("div");
        selectedDiv.classList.add("custom-selected");
        selectedDiv.setAttribute("tabindex", "0");

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
            option.setAttribute("tabindex", "0");

            option.addEventListener("click", function () {
                applySelection(optionText, selectedText, selectedDiv, optionsList, dropdownIcon, clearButton);
            });

            option.addEventListener("keydown", function (event) {
                if (event.key === "Enter") {
                    event.preventDefault();
                    option.click();
                }
            });

            optionsList.appendChild(option);
        });

        selectedDiv.addEventListener("click", function () {
            optionsList.style.display = optionsList.style.display === "block" ? "none" : "block";
        });

        clearButton.addEventListener("click", function (event) {
            event.stopPropagation();
            resetSelection(selectedText, selectedDiv, dropdownIcon, clearButton, label);
        });

        document.addEventListener("click", function (event) {
            if (!container.contains(event.target)) {
                optionsList.style.display = "none";
            }
        });

        container.appendChild(selectedDiv);
        container.appendChild(optionsList);
        dropdownContainer.appendChild(container);
    }

    // ✅ 필터 선택
    function applySelection(optionText, selectedText, selectedDiv, optionsList, dropdownIcon, clearButton) {
        selectedText.textContent = optionText;
        selectedDiv.classList.add("selected");
        optionsList.style.display = "none";

        dropdownIcon.style.display = "none";
        clearButton.style.display = "inline-block";

        applyFilters();
    }

    // ✅ 필터 초기화
    function resetSelection(selectedText, selectedDiv, dropdownIcon, clearButton, label) {
        selectedText.textContent = label;
        selectedDiv.classList.remove("selected");

        dropdownIcon.style.display = "inline-block";
        clearButton.style.display = "none";

        applyFilters();
    }

    // ✅ 필터 쿼리 생성
    function getFilterQueryString() {
        let queryParams = [];

        document.querySelectorAll(".custom-selected").forEach(selectedDiv => {
            const selectedText = selectedDiv.querySelector(".selected-text").textContent.trim();
            if (selectedText && filterValueMapping[selectedText]) {
                queryParams.push(filterValueMapping[selectedText]);
            }
        });

        const minSlider = document.querySelector(".custom-slider-container input:nth-of-type(1)");
        const maxSlider = document.querySelector(".custom-slider-container input:nth-of-type(2)");
        
        if (minSlider && maxSlider) {
            const minFee = parseInt(minSlider.value, 10);
            const maxFee = parseInt(maxSlider.value, 10);
            queryParams.push(`fee_min=${minFee}&fee_max=${maxFee === 100 ? "" : maxFee}`);
        }

        return queryParams.length > 0 ? "?" + queryParams.join("&") : "";
    }

    // ✅ 필터 적용 (캘린더, 리스트, 지도 업데이트)
    function applyFilters() {
        let queryString = getFilterQueryString();
        console.log("🎯 Applying filters:", queryString);

        document.dispatchEvent(new CustomEvent("filtersUpdated", { detail: queryString }));
    }

    dropdownData.forEach(data => {
        createDropdown(data.label, data.options);
    });

    createFeeSlider();
});



document.addEventListener("DOMContentLoaded", function () {
    let joinLink = document.getElementById("join-society-link");
    if (joinLink) {
        joinLink.addEventListener("click", function (evt) {
            if (!confirm("Are you sure you want to join this society?")) {
                evt.preventDefault();
            }
        });
    }
});
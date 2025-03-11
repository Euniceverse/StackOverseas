document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    const searchSuggestions = document.getElementById('searchSuggestions');
    const searchType = document.getElementById('searchType');
    const searchTermSpans = document.querySelectorAll('.search-term');
    const searchForm = searchInput.closest('form');

    searchInput.addEventListener('input', function() {
        const query = this.value.trim();

        // Update search terms in suggestions
        searchTermSpans.forEach(span => {
            span.textContent = query;
        });

        // Show/hide suggestions based on input
        if (query.length > 0) {
            searchSuggestions.classList.remove('d-none');
        } else {
            searchSuggestions.classList.add('d-none');
        }
    });

    // Handle category selection
    document.querySelectorAll('.search-category').forEach(category => {
        category.addEventListener('click', function() {
            searchType.value = this.dataset.type;
            searchForm.submit();
        });
    });

    // Hide suggestions when clicking outside
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !searchSuggestions.contains(e.target)) {
            searchSuggestions.classList.add('d-none');
        }
    });

    // Show suggestions when focusing on input
    searchInput.addEventListener('focus', function() {
        if (this.value.trim().length > 0) {
            searchSuggestions.classList.remove('d-none');
        }
    });
});

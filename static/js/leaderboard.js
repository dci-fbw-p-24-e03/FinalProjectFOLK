document.body.addEventListener('htmx:afterSwap', function (e) {
    // Check if the swap happened in the content area
    if (e.target.id === 'content-area') {
        // Re-run the function that sets up click events, sorting, etc.
        initializeLeaderboard();
    }
});

function initializeLeaderboard() {
    let starsHeader = document.getElementById("stars-header");
    if (!starsHeader) return;  // partial not present, do nothing

    let isAverageMode = false;

    starsHeader.addEventListener("click", function () {
        let tbody = document.querySelector("table tbody");
        let rows = Array.from(tbody.querySelectorAll("tr"));

        // Toggle between "Stars" and "Average Stars per Game"
        isAverageMode = !isAverageMode;
        starsHeader.textContent = isAverageMode ? "Average Stars per Game" : "Stars";

        // Update displayed star values
        rows.forEach(row => {
            let starsCell = row.cells[3];
            let originalStars = parseFloat(starsCell.dataset.originalStars);
            let averageStars = parseFloat(starsCell.dataset.averageStars);
            starsCell.textContent = isAverageMode ? averageStars.toFixed(2) : originalStars;
        });

        // Sort rows
        let sortedRows = rows.slice().sort((a, b) => {
            let aValue = parseFloat(a.cells[3].textContent);
            let bValue = parseFloat(b.cells[3].textContent);
            return bValue - aValue; // descending
        });

        // Update ranks and re-append rows
        sortedRows.forEach((row, index) => {
            row.cells[0].textContent = index + 1;
        });
        sortedRows.forEach(row => tbody.appendChild(row));
    });
}
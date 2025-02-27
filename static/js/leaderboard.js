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
        if (isAverageMode) {
            starsHeader.innerHTML = "Average Stars per Game / <span class='inactive'>Stars</span>";
        } else {
            starsHeader.innerHTML = "Stars / <span class='inactive'>Avg. Stars</span>";
        }

        // Update displayed star values
        // Stars column is now the 5th column (index 4) because we inserted "Total Games"
        rows.forEach(row => {
            let starsCell = row.cells[4];
            let originalStars = parseFloat(starsCell.dataset.originalStars);
            let averageStars = parseFloat(starsCell.dataset.averageStars);
            starsCell.textContent = isAverageMode ? averageStars.toFixed(2) : originalStars;
        });

        // Sort rows based on the updated star values (descending)
        let sortedRows = rows.slice().sort((a, b) => {
            let aValue = parseFloat(a.cells[4].textContent);
            let bValue = parseFloat(b.cells[4].textContent);
            return bValue - aValue; // descending
        });

        // Update ranks and re-append rows
        sortedRows.forEach((row, index) => {
            row.cells[0].textContent = index + 1;
        });
        sortedRows.forEach(row => tbody.appendChild(row));
    });
}

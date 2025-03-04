function toggleExplanations() {
    var explanations = document.getElementById("explanations");
    var button = document.getElementById("toggleButton");

    if (explanations.style.display === "none" || explanations.style.display === "") {
        explanations.style.display = "block";
        button.classList.add("toggled"); // Keep hover style after clicking
    } else {
        explanations.style.display = "none";
        button.classList.remove("toggled"); // Remove hover style when toggled off
    }
}

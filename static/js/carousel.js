document.addEventListener("DOMContentLoaded", function () {
    const slides = document.querySelectorAll(".carousel-item");
    const prevButton = document.getElementById("prevButton");
    const nextButton = document.getElementById("nextButton");

    let currentIndex = 0;

    function showSlide(index) {
        if (index < 0) {
            currentIndex = slides.length - 1; // Wrap to last slide
        } else if (index >= slides.length) {
            currentIndex = 0; // Wrap to first slide
        } else {
            currentIndex = index; // Set current index
        }

        slides.forEach((slide, i) => {
            slide.style.display = i === currentIndex ? "block" : "none"; // Show current slide
        });
    }

    // Ensure only the first slide is visible initially
    if (slides.length > 0) {
        showSlide(currentIndex); // Show the first slide
    }

    prevButton.addEventListener("click", function () {
        showSlide(currentIndex - 1); // Show previous slide
    });

    nextButton.addEventListener("click", function () {
        showSlide(currentIndex + 1); // Show next slide
    });
});
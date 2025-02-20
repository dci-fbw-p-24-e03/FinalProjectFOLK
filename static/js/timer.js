// Global variable to alternate between 10 and 3 seconds.
let currentDuration = 10;

function runTimer(timerElement, duration) {
  let timeLeft = duration; // Use the given duration.
  const timerCircle = timerElement.querySelector('svg > circle + circle');
  timerElement.classList.add('animatable');
  timerCircle.style.strokeDashoffset = 1;

  // Get the display element for the countdown.
  const timerDisplay = timerElement.querySelector('#timeLeft');

  let countdownTimer = setInterval(function() {
    if (timeLeft >= 0) {
      timerDisplay.innerHTML = timeLeft;
      // Normalize using the dynamic duration.
      const normalizedTime = (duration - timeLeft) / duration;
      timerCircle.style.strokeDashoffset = normalizedTime;
      timeLeft--;
    } else {
      clearInterval(countdownTimer);
      timerElement.classList.remove('animatable');
    }
  }, 1000);
}

function initializeTimer() {
  const timerElement = document.querySelector('.timer');
  if (timerElement) {
    runTimer(timerElement, currentDuration);
    // Toggle the duration for the next run.
    currentDuration = currentDuration === 10 ? 3 : 10;
  }
}

// Run immediately if the document is already loaded; otherwise, wait for the load event.
if (document.readyState === "complete") {
  initializeTimer();
} else {
  window.addEventListener('load', initializeTimer);
}

// Re-run the timer after each HTMX swap, toggling the duration each time.
document.addEventListener('htmx:afterSwap', function(event) {
  const timerElement = document.querySelector('.timer');
  if (timerElement) {
    runTimer(timerElement, currentDuration);
    currentDuration = currentDuration === 10 ? 3 : 10;
  }
});
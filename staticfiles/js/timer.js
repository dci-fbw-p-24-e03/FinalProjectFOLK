// Global variable to alternate between 10 and 3 seconds.
let currentDuration = 15;
// Global bonus variable, starts at 12 when a new question appears
let bonusPoints = 12;

function runTimer(timerElement, duration) {
  let timeLeft = duration; // Use the given duration.
  bonusPoints = 12; // Reset bonus when a new question starts

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
      bonusPoints = Math.max(0, bonusPoints - 1); // Decrease bonus, min 0
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
    currentDuration = currentDuration === 15 ? 3 : 15;
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
    currentDuration = currentDuration === 15 ? 3 : 15;
  }
});

document.querySelectorAll('.answer-button').forEach(button => {
  button.addEventListener('click', function() {
    console.log("Answer clicked!"); // ✅ Check if event fires

    const resultElement = document.getElementById('result');
    if (resultElement.classList.contains('score-positive')) {
      console.log("Correct answer!"); // ✅ Check if it's correct

      const timeLeftElement = document.getElementById('timeLeft');
      if (timeLeftElement) {
        const timeLeft = parseInt(timeLeftElement.textContent, 15);
        console.log("Time left:", timeLeft); // ✅ Check time value

        let baseScore = parseInt(resultElement.getAttribute('data-base'), 15);
        console.log("Base score:", baseScore); // ✅ Check base score

        let newScore = baseScore + timeLeft;
        console.log("New score:", newScore); // ✅ Check calculation

        resultElement.setAttribute('data-base', newScore);
        resultElement.textContent = "Score: +" + newScore;
      } else {
        console.log("⚠️ timeLeftElement not found!");
      }
    }
  });
});
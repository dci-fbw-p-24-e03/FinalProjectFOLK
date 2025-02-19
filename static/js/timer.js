function runTimer(timerElement) {
    let timeLeft = 10; // Reset timer duration each time
    const timerCircle = timerElement.querySelector('svg > circle + circle');
    timerElement.classList.add('animatable');
    timerCircle.style.strokeDashoffset = 1;
    
    // Get the display element for the countdown.
    // Using timerElement.querySelector ensures we search within the timer.
    const timerDisplay = timerElement.querySelector('#timeLeft');
    
    let countdownTimer = setInterval(function() {
      if (timeLeft >= 0) {
        timerDisplay.innerHTML = timeLeft;
        const normalizedTime = (10 - timeLeft) / 10;
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
      runTimer(timerElement);
    }
  }
  
  // If the document is already loaded, run immediately; otherwise, wait for the load event.
  if (document.readyState === "complete") {
    initializeTimer();
  } else {
    window.addEventListener('load', initializeTimer);
  }
  
  // Re-run timer after HTMX swaps new content.
  document.addEventListener('htmx:afterSwap', function(event) {
    const timerElement = document.querySelector('.timer');
    if (timerElement) {
      runTimer(timerElement);
    }
  });
document.addEventListener('DOMContentLoaded', () => {
  // Function to generate a random colour in hexadecimal notation
  const randomColor = () =>
    '#' + Math.floor(Math.random() * 16777215).toString(16).padStart(6, '0');

  // Assign random colours to each nav item by setting CSS custom properties on the inner <span>
  document.querySelectorAll('nav a').forEach(anchor => {
    const span = anchor.querySelector('span');
    if (span) {
      const color1 = randomColor();
      const color2 = randomColor();
      span.style.setProperty('--color1', color1);
      span.style.setProperty('--color2', color2);
    }
  });

  // Select all nav links, the indicator element, and the nav container
  const navLinks = document.querySelectorAll('nav a');
  const indicator = document.getElementById('indicator');
  const nav = document.querySelector('nav');

  // For each nav link, update the indicator's position, width, and background on mouseenter
  navLinks.forEach(link => {
    link.addEventListener('mouseenter', () => {
      const span = link.querySelector('span');
      if (!span) return;

      // Get the bounding rectangle of the span and the nav container
      const spanRect = span.getBoundingClientRect();
      const navRect = nav.getBoundingClientRect();

      // Calculate the left offset and width of the span relative to the nav container
      const left = spanRect.left - navRect.left;
      const width = spanRect.width;

      // Update the indicator's position and size
      indicator.style.left = `${left}px`;
      indicator.style.width = `${width}px`;

      // Retrieve the custom properties (colors) from the computed style of the span
      const computedStyle = getComputedStyle(span);
      const color1 = computedStyle.getPropertyValue('--color1').trim() || 'yellow';
      const color2 = computedStyle.getPropertyValue('--color2').trim() || 'red';

      // Set the indicator's background to a gradient using the retrieved colours
      indicator.style.background = `linear-gradient(130deg, ${color1}, ${color2})`;
    });
  });
});

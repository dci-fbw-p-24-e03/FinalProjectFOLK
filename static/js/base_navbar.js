document.addEventListener('DOMContentLoaded', () => {
  // Define an array of neon colours to choose from
  const randomNeonColor = () => {
    // Generate a random hue between 0 and 360.
    const hue = Math.floor(Math.random() * 360);
    // Saturation between 80% and 100% to ensure vivid colour.
    const saturation = Math.floor(Math.random() * 21) + 80;
    // Lightness between 60% and 80% to keep the colour bright.
    const lightness = Math.floor(Math.random() * 21) + 60;
    return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
  };
  // Function to generate a random colour in hexadecimal notation (for the pseudo-elements)
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

      // Assign a random neon colour for the text
      const neonText = randomNeonColor();
      span.style.setProperty('--neon-text', neonText);
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

      // Get computed styles for the nav container
      const navStyles = getComputedStyle(nav);
      const borderLeft = parseFloat(navStyles.borderLeftWidth) || 0;

      // Calculate the left offset relative to the nav's content (excluding border)
      const left = spanRect.left - navRect.left - borderLeft;
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

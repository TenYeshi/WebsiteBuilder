document.addEventListener("DOMContentLoaded", function () {
  // Random starting slide
  const items = document.querySelectorAll("#imageCarousel .carousel-item");
  const indicators = document.querySelectorAll("#imageCarousel .carousel-indicators button");
  const randomIndex = Math.floor(Math.random() * items.length);

  items[randomIndex].classList.add("active");
  indicators[randomIndex]?.classList.add("active");

  // Initialize AOS (Animate On Scroll)
  AOS.init({
      duration: 1200,
      once: true
  });

  // Dark Mode Toggle
  const darkToggle = document.querySelector('.dark-toggle');
  const html = document.documentElement;

  darkToggle.addEventListener('click', () => {
      const currentTheme = html.getAttribute("data-bs-theme");
      const newTheme = currentTheme === "light" ? "dark" : "light";
      html.setAttribute("data-bs-theme", newTheme);

      // Update button icon
      darkToggle.textContent = newTheme === "dark" ? '🌙' : '🌞';
  });
});
document.addEventListener("DOMContentLoaded", function () {
  const navbar = document.querySelector(".navbar-custom");
  if (!navbar) return;

  function updateNavbar() {
    if (window.scrollY > 40) {
      navbar.classList.add("navbar-scrolled");
    } else {
      navbar.classList.remove("navbar-scrolled");
    }
  }

  updateNavbar();
  window.addEventListener("scroll", updateNavbar);
});

document.addEventListener("DOMContentLoaded", function () {
  // Auto-hide after 4 seconds
  const flashes = document.querySelectorAll(".df-flash");
  flashes.forEach((el) => {
    setTimeout(() => {
      el.classList.add("df-flash-hide");
      setTimeout(() => el.remove(), 400);
    }, 4000);
  });

  // Close button behavior
  document.querySelectorAll(".df-flash-close").forEach((btn) => {
    btn.addEventListener("click", function () {
      const alertBox = this.parentElement;
      alertBox.classList.add("df-flash-hide");
      setTimeout(() => alertBox.remove(), 400);
    });
  });
});

(() => {
  const slides = [...document.querySelectorAll(".slide")];
  const dots = [...document.querySelectorAll(".dot")];
  const heroArt = [...document.querySelectorAll(".hero-art-image")];
  const count = document.getElementById("currentSlide");
  const menu = document.getElementById("navDrawer");
  const toggle = document.getElementById("menuToggle");
  const close = document.getElementById("drawerClose");
  const scrim = document.getElementById("navScrim");
  let current = 0;
  let timer;

  function showSlide(index) {
    current = (index + slides.length) % slides.length;
    slides.forEach((slide, i) => slide.classList.toggle("active", i === current));
    heroArt.forEach((image, i) => image.classList.toggle("active", i === current));
    dots.forEach((dot, i) => {
      dot.classList.toggle("active", i === current);
      dot.setAttribute("aria-current", i === current ? "true" : "false");
    });
    if (count) count.textContent = String(current + 1).padStart(2, "0");
  }
  function restartTimer() {
    clearInterval(timer);
    timer = setInterval(() => showSlide(current + 1), 6500);
  }
  dots.forEach(dot => dot.addEventListener("click", () => {
    showSlide(Number(dot.dataset.go));
    restartTimer();
  }));
  if (slides.length) { showSlide(0); restartTimer(); }
  // Do not advance slides while the tab is hidden; resume cleanly when it comes back.
  document.addEventListener("visibilitychange", () => {
    if (!slides.length) return;
    if (document.hidden) clearInterval(timer); else restartTimer();
  });

  function setMenu(open) {
    if (!menu || !scrim || !toggle) return;
    menu.classList.toggle("open", open);
    scrim.classList.toggle("show", open);
    toggle.setAttribute("aria-expanded", String(open));
    document.body.classList.toggle("menu-open", open);
  }
  toggle?.addEventListener("click", () => setMenu(!menu?.classList.contains("open")));
  close?.addEventListener("click", () => setMenu(false));
  scrim?.addEventListener("click", () => setMenu(false));
  menu?.querySelectorAll("a").forEach(link => link.addEventListener("click", () => setMenu(false)));
  document.addEventListener("keydown", event => { if (event.key === "Escape") setMenu(false); });
})();
// reveal the 4 career pillars as they enter the viewport.
(() => {
  const section = document.getElementById('job-ready-pillars');
  if (!section) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    section.classList.add('is-visible');
    return;
  }
  const observer = new IntersectionObserver((entries, obs) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        section.classList.add('is-visible');
        obs.unobserve(section);
      }
    });
  }, { threshold: 0.16 });
  observer.observe(section);
})();

// Internship section reveal sequence.
(() => {
  const section = document.getElementById('internship');
  if (!section) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    section.classList.add('is-visible');
    return;
  }
  const observer = new IntersectionObserver((entries, obs) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        section.classList.add('is-visible');
        obs.unobserve(section);
      }
    });
  }, { threshold: 0.14 });
  observer.observe(section);
})();

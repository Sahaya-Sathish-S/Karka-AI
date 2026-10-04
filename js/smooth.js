/* Karka AI — smoothness helpers
   - scroll reveals (transform/opacity only, GPU friendly)
   - plays preview videos only while they are on screen
   - pauses decorative animations in sections that are off screen
   Everything degrades gracefully: without JS or IntersectionObserver the page simply shows all content. */
(() => {
  const root = document.documentElement;
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const hasIO = 'IntersectionObserver' in window;

  /* 1. Scroll reveal ------------------------------------------------------ */
  const revealSelectors = [
    '.partners-heading', '.courses-heading', '.why-karka-shell', '.voices-heading', '.voices-player',
    '.pay-after-heading', '.pay-after-layout', '.feedback-heading', '.career-track-heading',
    '.faq-heading', '.faq-footer-card', '.career-call-shell', '.location-heading', '.location-grid',
    '.future-cta-shell'
  ];
  const revealTargets = revealSelectors.flatMap(sel => [...document.querySelectorAll(sel)]);
  if (revealTargets.length) {
    if (!hasIO || reduceMotion) {
      revealTargets.forEach(el => el.classList.add('reveal', 'is-in'));
    } else {
      const io = new IntersectionObserver((entries, obs) => {
        entries.forEach(entry => {
          if (!entry.isIntersecting) return;
          entry.target.classList.add('is-in');
          obs.unobserve(entry.target);
        });
      }, { threshold: 0.08, rootMargin: '0px 0px -6% 0px' });
      revealTargets.forEach(el => { el.classList.add('reveal'); io.observe(el); });

      // Safety net: if the reader jumps/flicks past a block (fast scroll, anchor jump, back button),
      // reveal everything that is now on screen or already above the fold so nothing stays hidden.
      let pending = revealTargets.slice(), ticking = false;
      const sweep = () => {
        ticking = false;
        const limit = window.innerHeight * 0.94;
        pending = pending.filter(el => {
          if (el.classList.contains('is-in')) return false;
          if (el.getBoundingClientRect().top < limit) { el.classList.add('is-in'); io.unobserve(el); return false; }
          return true;
        });
        if (!pending.length) window.removeEventListener('scroll', onScroll);
      };
      const onScroll = () => { if (!ticking) { ticking = true; requestAnimationFrame(sweep); } };
      window.addEventListener('scroll', onScroll, { passive: true });
      window.addEventListener('load', sweep);
    }
  }

  /* 2. Videos play only while visible ------------------------------------ */
  const videos = [...document.querySelectorAll('video[data-lazy-play], video.hero-video')];
  if (videos.length) {
    const tryPlay = v => { const p = v.play(); if (p && p.catch) p.catch(() => {}); };
    if (!hasIO || reduceMotion) {
      if (!reduceMotion) videos.forEach(tryPlay);
    } else {
      const vio = new IntersectionObserver(entries => {
        entries.forEach(entry => {
          const v = entry.target;
          if (entry.isIntersecting) tryPlay(v); else v.pause();
        });
      }, { threshold: 0.15 });
      videos.forEach(v => vio.observe(v));
    }
  }

  /* 3. Pause off-screen decorative animations ----------------------------- */
  if (hasIO && !reduceMotion) {
    const aio = new IntersectionObserver(entries => {
      entries.forEach(entry => entry.target.classList.toggle('anim-paused', !entry.isIntersecting));
    }, { rootMargin: '200px 0px' });
    document.querySelectorAll('section, footer').forEach(el => aio.observe(el));
  }

  /* 4. Smooth in-page anchor scrolling that respects the fixed hash --------- */
  document.addEventListener('click', event => {
    const link = event.target.closest && event.target.closest('a[href*="#"]');
    if (!link || reduceMotion) return;
    const url = new URL(link.href, location.href);
    if (url.pathname !== location.pathname || !url.hash || url.hash === '#') return;
    const target = document.getElementById(decodeURIComponent(url.hash.slice(1)));
    if (!target) return;
    event.preventDefault();
    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    history.pushState(null, '', url.hash);
  });

  /* 5. Make sure nothing stays hidden if the page was restored from cache --- */
  window.addEventListener('pageshow', e => { if (e.persisted) root.classList.add('js'); });
})();

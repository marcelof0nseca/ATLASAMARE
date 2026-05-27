/* ============================================================
   ATLAS LANDING — JS
   Lenis + GSAP ScrollTrigger + interactions
   ============================================================ */

document.addEventListener('DOMContentLoaded', function () {

  /* ── Lenis smooth scroll ────────────────────────────────── */
  const lenis = new Lenis({
    duration: 1.2,
    easing: t => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
    smooth: true,
    smoothTouch: false,
  });

  lenis.on('scroll', ScrollTrigger.update);
  gsap.ticker.add(t => lenis.raf(t * 1000));
  gsap.ticker.lagSmoothing(0);

  /* ── Smooth anchor links ────────────────────────────────── */
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
      const target = document.querySelector(a.getAttribute('href'));
      if (target) {
        e.preventDefault();
        lenis.scrollTo(target, { offset: -72 });
      }
    });
  });

  /* ── 1. NAV fade in + scroll shadow ────────────────────── */
  const nav = document.getElementById('main-nav');
  gsap.to(nav, { opacity: 1, duration: 0.4, ease: 'power2.out', delay: 0.1 });

  lenis.on('scroll', ({ scroll }) => {
    if (scroll > 32) {
      nav.style.boxShadow = '0 2px 16px rgba(75,61,86,0.08)';
    } else {
      nav.style.boxShadow = 'none';
    }
  });

  /* ── 2. HERO entrance stagger ───────────────────────────── */
  const heroEls = [
    '.hero-eyebrow',
    '.hero-h1',
    '.hero-subtitle',
    '.hero-ctas',
    '.hero-trust',
    '.hero-badges',
    '.hero-mockup-wrap',
  ];
  heroEls.forEach((sel, i) => {
    const el = document.querySelector(sel);
    if (!el) return;
    gsap.to(el, {
      y: 0,
      opacity: 1,
      duration: 0.7,
      ease: 'power2.out',
      delay: 0.1 + i * 0.12,
    });
  });

  /* helper: reveal elements on scroll */
  function revealOnScroll(selector, options = {}) {
    const els = document.querySelectorAll(selector);
    if (!els.length) return;
    els.forEach((el, i) => {
      gsap.fromTo(el,
        { y: 28, opacity: 0 },
        {
          y: 0,
          opacity: 1,
          duration: options.duration || 0.7,
          ease: 'power2.out',
          delay: (options.stagger || 0) * i,
          scrollTrigger: {
            trigger: el,
            start: options.start || 'top 82%',
            once: true,
          },
        }
      );
    });
  }

  /* ── 3. Trust bar ───────────────────────────────────────── */
  revealOnScroll('#trust-bar .trust-label');
  revealOnScroll('#trust-bar .trust-item', { stagger: 0.06 });

  /* ── 4. Profile cards ───────────────────────────────────── */
  revealOnScroll('.profiles-header', {});
  revealOnScroll('.profile-card', { stagger: 0.12, start: 'top 80%' });

  /* ── 5. Stats counters ──────────────────────────────────── */
  const counters = document.querySelectorAll('[data-count]');
  counters.forEach(el => {
    const target = el.getAttribute('data-count');
    const isPercent = target.includes('%');
    const num = parseFloat(target);

    const ob = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        ob.unobserve(el);
        const start = performance.now();
        const duration = 1800;

        function easeOutQuart(t) { return 1 - Math.pow(1 - t, 4); }

        function tick(now) {
          const elapsed = now - start;
          const progress = Math.min(elapsed / duration, 1);
          const value = easeOutQuart(progress) * num;
          el.textContent = isPercent
            ? Math.round(value) + '%'
            : (num % 1 === 0 ? Math.round(value) : value.toFixed(1));
          if (progress < 1) requestAnimationFrame(tick);
          else el.textContent = target;
        }
        requestAnimationFrame(tick);
      });
    }, { threshold: 0.5 });

    ob.observe(el);
  });

  revealOnScroll('.stat-cell', { stagger: 0.08 });

  /* ── 6. Bento grid ──────────────────────────────────────── */
  revealOnScroll('.features-header');
  revealOnScroll('.bento-cell', { stagger: 0.08 });

  /* spotlight mouse tracking on bento cells */
  document.querySelectorAll('.bento-cell').forEach(cell => {
    cell.addEventListener('mousemove', e => {
      const rect = cell.getBoundingClientRect();
      const x = ((e.clientX - rect.left) / rect.width) * 100;
      const y = ((e.clientY - rect.top) / rect.height) * 100;
      cell.style.setProperty('--mx', x + '%');
      cell.style.setProperty('--my', y + '%');
    });
  });

  /* ── 7. How it works ────────────────────────────────────── */
  revealOnScroll('.how-header');
  revealOnScroll('.step', { stagger: 0.14 });

  document.querySelectorAll('.connector-line').forEach(line => {
    gsap.fromTo(line,
      { scaleX: 0 },
      {
        scaleX: 1,
        ease: 'none',
        scrollTrigger: {
          trigger: line,
          start: 'top 80%',
          end: 'top 40%',
          scrub: 1,
        },
      }
    );
  });

  /* ── 8. Testimonials ────────────────────────────────────── */
  revealOnScroll('.testimonials-header');

  const carouselWrap = document.querySelector('.carousel-wrap');
  if (carouselWrap) {
    gsap.fromTo(carouselWrap,
      { filter: 'blur(8px)', opacity: 0 },
      {
        filter: 'blur(0px)',
        opacity: 1,
        duration: 0.8,
        ease: 'power2.out',
        scrollTrigger: { trigger: carouselWrap, start: 'top 82%', once: true },
      }
    );
  }

  /* touch swipe for carousel on mobile */
  const track = document.querySelector('.carousel-track');
  if (track) {
    let startX = 0;
    track.addEventListener('touchstart', e => {
      startX = e.touches[0].clientX;
      track.style.animationPlayState = 'paused';
    }, { passive: true });

    track.addEventListener('touchend', e => {
      const diff = startX - e.changedTouches[0].clientX;
      if (Math.abs(diff) > 50) {
        const dir = diff > 0 ? 1 : -1;
        const current = parseFloat(getComputedStyle(track).transform.split(',')[4] || '0');
        track.style.transform = `translateX(${current - dir * 340}px)`;
        setTimeout(() => { track.style.transform = ''; }, 600);
      }
      track.style.animationPlayState = 'running';
    }, { passive: true });
  }

  /* ── 9. Pricing toggle ──────────────────────────────────── */
  const toggleSwitch = document.getElementById('billing-toggle');
  const monthlyLabel = document.getElementById('label-monthly');
  const annualLabel  = document.getElementById('label-annual');
  const priceEls = document.querySelectorAll('[data-monthly][data-annual]');
  let isAnnual = false;

  function activateToggle() {
    isAnnual = !isAnnual;
    toggleSwitch.classList.toggle('on', isAnnual);
    toggleSwitch.setAttribute('aria-checked', isAnnual);
    monthlyLabel.classList.toggle('active', !isAnnual);
    annualLabel.classList.toggle('active', isAnnual);
    priceEls.forEach(el => {
      el.textContent = isAnnual ? el.dataset.annual : el.dataset.monthly;
    });
  }

  if (toggleSwitch) {
    toggleSwitch.addEventListener('click', activateToggle);
    toggleSwitch.addEventListener('keydown', e => {
      if (e.key === ' ' || e.key === 'Enter') { e.preventDefault(); activateToggle(); }
    });
  }

  revealOnScroll('.pricing-header');
  revealOnScroll('.plan-card', { stagger: 0.10 });
  revealOnScroll('.trust-badges-row');

  /* plan select toast */
  document.querySelectorAll('.plan-select-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      showToast('Plano selecionado! Redirecionando...');
    });
  });

  /* ── 10. FAQ accordion ──────────────────────────────────── */
  document.querySelectorAll('.faq-item').forEach(item => {
    const btn = item.querySelector('.faq-question');
    const answer = item.querySelector('.faq-answer');
    btn.addEventListener('click', () => {
      const isOpen = item.classList.contains('open');
      document.querySelectorAll('.faq-item.open').forEach(open => {
        open.classList.remove('open');
        open.querySelector('.faq-answer').style.maxHeight = '0';
        open.querySelector('.faq-question').setAttribute('aria-expanded', 'false');
      });
      if (!isOpen) {
        item.classList.add('open');
        answer.style.maxHeight = answer.scrollHeight + 'px';
        btn.setAttribute('aria-expanded', 'true');
      }
    });
  });

  revealOnScroll('.faq-header');
  revealOnScroll('.faq-item', { stagger: 0.06 });

  /* ── 11. CTA word reveal ────────────────────────────────── */
  const ctaH2 = document.querySelector('.cta-h2');
  if (ctaH2) {
    const words = ctaH2.querySelectorAll('.cta-word');
    gsap.fromTo(words,
      { y: 20, opacity: 0 },
      {
        y: 0,
        opacity: 1,
        duration: 0.5,
        ease: 'power2.out',
        stagger: 0.04,
        scrollTrigger: { trigger: ctaH2, start: 'top 80%', once: true },
      }
    );
  }
  revealOnScroll('.cta-subtitle');
  revealOnScroll('.cta-actions');
  revealOnScroll('.cta-micro');

  /* ── Section titles: letter-spacing tighten on reveal ───── */
  document.querySelectorAll('.profiles-h2, .features-h2, .how-h2, .testimonials-h2, .pricing-h2, .faq-h2').forEach(el => {
    gsap.fromTo(el,
      { letterSpacing: '-0.005em' },
      {
        letterSpacing: '-0.025em',
        duration: 0.7,
        ease: 'power2.out',
        scrollTrigger: { trigger: el, start: 'top 82%', once: true },
      }
    );
  });

  /* ── Mobile drawer ──────────────────────────────────────── */
  const hamburger = document.getElementById('hamburger-btn');
  const drawerOverlay = document.getElementById('drawer-overlay');
  const drawer = document.getElementById('nav-drawer');
  const drawerClose = document.getElementById('drawer-close');

  function openDrawer() {
    drawerOverlay.classList.add('open');
    drawer.classList.add('open');
    document.body.style.overflow = 'hidden';
  }
  function closeDrawer() {
    drawerOverlay.classList.remove('open');
    drawer.classList.remove('open');
    document.body.style.overflow = '';
  }

  if (hamburger) hamburger.addEventListener('click', openDrawer);
  if (drawerOverlay) drawerOverlay.addEventListener('click', closeDrawer);
  if (drawerClose) drawerClose.addEventListener('click', closeDrawer);
  document.querySelectorAll('.drawer-link').forEach(a => a.addEventListener('click', closeDrawer));

  /* ── Toast helper ───────────────────────────────────────── */
  function showToast(msg) {
    const container = document.querySelector('.toast-container') || (() => {
      const c = document.createElement('div');
      c.className = 'toast-container';
      document.body.appendChild(c);
      return c;
    })();

    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.innerHTML = `<span class="toast-dot"></span>${msg}`;
    container.appendChild(toast);

    setTimeout(() => {
      toast.classList.add('out');
      toast.addEventListener('animationend', () => toast.remove());
    }, 3200);
  }

  /* ── Newsletter form ────────────────────────────────────── */
  const newsForm = document.querySelector('.footer-newsletter-form');
  if (newsForm) {
    newsForm.addEventListener('submit', e => {
      e.preventDefault();
      const input = newsForm.querySelector('input');
      if (input.value.trim()) {
        showToast('Inscrição realizada com sucesso!');
        input.value = '';
      }
    });
  }

});

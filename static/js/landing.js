/* ============================================================
   ATLAS LANDING — JS
   IntersectionObserver + CSS animations (sem Lenis, sem GSAP)

   Removidos:
   - Lenis smooth scroll: interceptava o scroll nativo com JS
     (duration:1.2 = travamento intencional de 1.2s por scroll)
   - GSAP + ScrollTrigger: scrub:1 executava JS em todo frame
     de scroll; filter:blur() animado = repaint constante

   Substituídos por:
   - CSS scroll-behavior: smooth (nativo, compositor thread)
   - IntersectionObserver + classes CSS (zero JS no scroll path)
   - Passive scroll listener apenas para shadow da nav
   ============================================================ */

document.addEventListener('DOMContentLoaded', function () {

  /* ── 1. Smooth anchor scroll ──────────────────────────────────────────────
     CSS já tem scroll-behavior:smooth no html.
     Este listener apenas aplica o offset da nav fixa (72px).
  -------------------------------------------------------------------------- */
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
      const target = document.querySelector(a.getAttribute('href'));
      if (!target) return;
      e.preventDefault();
      const top = target.getBoundingClientRect().top + window.scrollY - 72;
      window.scrollTo({ top, behavior: 'smooth' });
    });
  });

  /* ── 2. Nav shadow no scroll ──────────────────────────────────────────────
     Listener passivo: nunca bloqueia o scroll, não anima nada,
     só altera uma propriedade CSS não-layout.
  -------------------------------------------------------------------------- */
  const nav = document.getElementById('main-nav');
  if (nav) {
    /* O CSS inicia a nav com opacity:0 (era o GSAP que revelava).
       Fazemos o fade-in via transição CSS, sem biblioteca. */
    nav.style.transition = 'opacity 0.4s ease, transform 0.35s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.2s ease';
    setTimeout(() => { nav.style.opacity = '1'; }, 50);

    /* ── Hide on scroll down / show on scroll up ──────────────
       Usa transform (GPU) para esconder/mostrar sem layout shift.
       Só oculta após passar da altura da própria nav (72px).
    ────────────────────────────────────────────────────────── */
    let lastScrollY = 0;
    let ticking = false;

    window.addEventListener('scroll', () => {
      if (ticking) return;
      ticking = true;

      requestAnimationFrame(() => {
        const currentY = window.scrollY;

        /* Shadow */
        nav.style.boxShadow = currentY > 32
          ? '0 2px 16px rgba(75,61,86,0.08)'
          : 'none';

        /* Hide / show */
        if (currentY > lastScrollY && currentY > 72) {
          /* scrollando para baixo → esconde */
          nav.style.transform = 'translateY(-100%)';
        } else {
          /* scrollando para cima → mostra */
          nav.style.transform = 'translateY(0)';
        }

        lastScrollY = currentY;
        ticking = false;
      });
    }, { passive: true });
  }

  /* ── 3. Reveal via IntersectionObserver ───────────────────────────────────
     Substitui todas as animações GSAP fromTo/ScrollTrigger.
     Quando o elemento entra na viewport → adiciona .is-revealed.
     O CSS cuida da transição (opacity + translateY) na GPU.
  -------------------------------------------------------------------------- */
  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add('is-revealed');
      revealObserver.unobserve(entry.target);
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -32px 0px' });

  /* Todos os seletores que recebem animação de reveal por scroll */
  const scrollRevealSelectors = [
    '.profiles-header',  '.profile-card',
    '.features-header',  '.bento-cell',
    '.how-header',       '.step',
    '.testimonials-header',
    '.faq-header',       '.faq-item',
    '.cta-subtitle',     '.cta-actions', '.cta-micro',
  ];

  scrollRevealSelectors.forEach(selector => {
    document.querySelectorAll(selector).forEach((el, i) => {
      el.classList.add('reveal');
      /* stagger: delay acumulado por posição dentro do grupo */
      el.style.setProperty('--reveal-delay', `${i * 0.07}s`);
      revealObserver.observe(el);
    });
  });

  /* ── 4. Hero: visível no carregamento inicial, revela com stagger ─────────
     Elementos do hero já estão na viewport. Adicionamos .reveal (estado
     inicial invisível) e depois .is-revealed com setTimeout sequencial.
  -------------------------------------------------------------------------- */
  const heroSelectors = [
    '.hero-eyebrow', '.hero-h1', '.hero-subtitle',
    '.hero-ctas', '.hero-trust', '.hero-badges', '.hero-mockup-wrap',
  ];
  heroSelectors.forEach((sel, i) => {
    const el = document.querySelector(sel);
    if (!el) return;
    el.classList.add('reveal');
    el.style.setProperty('--reveal-delay', '0s'); /* delay via setTimeout abaixo */
    setTimeout(() => el.classList.add('is-revealed'), 100 + i * 120);
  });

  /* ── 5. CTA words reveal ──────────────────────────────────────────────────
     Cada palavra do título do CTA revela em sequência.
  -------------------------------------------------------------------------- */
  const ctaH2 = document.querySelector('.cta-h2');
  if (ctaH2) {
    const ctaObserver = new IntersectionObserver((entries) => {
      if (!entries[0].isIntersecting) return;
      ctaH2.querySelectorAll('.cta-word').forEach((w, i) => {
        w.classList.add('reveal');
        setTimeout(() => w.classList.add('is-revealed'), i * 50);
      });
      ctaObserver.disconnect();
    }, { threshold: 0.3 });
    ctaObserver.observe(ctaH2);
  }

  /* ── 6. Connector lines ───────────────────────────────────────────────────
     Substitui o GSAP scrub (que rodava JS em todo frame de scroll).
     Agora usa CSS scaleX transition acionada por IntersectionObserver.
  -------------------------------------------------------------------------- */
  document.querySelectorAll('.connector-line').forEach(line => {
    line.classList.add('reveal-line');
    const lineObserver = new IntersectionObserver((entries) => {
      if (!entries[0].isIntersecting) return;
      line.classList.add('is-revealed');
      lineObserver.disconnect();
    }, { threshold: 0.5 });
    lineObserver.observe(line);
  });

  /* ── 7. Spotlight mouse tracking nos bento cells ─────────────────────────
     Só dispara em mousemove (hover), nunca no scroll — sem impacto.
  -------------------------------------------------------------------------- */
  document.querySelectorAll('.bento-cell').forEach(cell => {
    cell.addEventListener('mousemove', e => {
      const r = cell.getBoundingClientRect();
      cell.style.setProperty('--mx', ((e.clientX - r.left) / r.width * 100) + '%');
      cell.style.setProperty('--my', ((e.clientY - r.top)  / r.height * 100) + '%');
    });
  });

  /* ── 9. FAQ accordion ─────────────────────────────────────────────────── */
  document.querySelectorAll('.faq-item').forEach(item => {
    const btn    = item.querySelector('.faq-question');
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

  /* ── 10. Mobile drawer ───────────────────────────────────────────────── */
  const hamburger     = document.getElementById('hamburger-btn');
  const drawerOverlay = document.getElementById('drawer-overlay');
  const drawer        = document.getElementById('nav-drawer');
  const drawerClose   = document.getElementById('drawer-close');

  function openDrawer()  {
    drawerOverlay.classList.add('open');
    drawer.classList.add('open');
    document.body.style.overflow = 'hidden';
  }
  function closeDrawer() {
    drawerOverlay.classList.remove('open');
    drawer.classList.remove('open');
    document.body.style.overflow = '';
  }
  if (hamburger)     hamburger.addEventListener('click', openDrawer);
  if (drawerOverlay) drawerOverlay.addEventListener('click', closeDrawer);
  if (drawerClose)   drawerClose.addEventListener('click', closeDrawer);
  document.querySelectorAll('.drawer-link').forEach(a => a.addEventListener('click', closeDrawer));

  /* ── 12. Carousel touch swipe ─────────────────────────────────────────── */
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

  /* ── 13. Toast helper ─────────────────────────────────────────────────── */
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

  /* ── 13. Newsletter form ─────────────────────────────────────────────── */
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

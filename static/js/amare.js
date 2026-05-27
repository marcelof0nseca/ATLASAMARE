document.addEventListener("DOMContentLoaded", () => {
  const modalRoot = document.getElementById("modal-root");
  const toastRoot = document.getElementById("toast-root");

  // ── Toast ──────────────────────────────────────────────────────────────────
  document.body.addEventListener("showToast", (event) => {
    if (!toastRoot) return;
    const detail = event.detail || {};
    const tone = detail.tone === "success" ? "bg-success/90" : "bg-text-strong";
    toastRoot.innerHTML = `
      <div class="rounded-2xl ${tone} px-4 py-3 text-sm font-medium text-white shadow-serene">
        ${detail.message || "Tudo certo."}
      </div>
    `;
    window.clearTimeout(window.amareToastTimeout);
    window.amareToastTimeout = window.setTimeout(() => {
      toastRoot.innerHTML = "";
    }, 3500);
  });

  // ── Modal ──────────────────────────────────────────────────────────────────
  document.body.addEventListener("closeModal", () => {
    if (modalRoot) modalRoot.innerHTML = "";
  });

  // ── Barra de progresso de navegação ───────────────────────────────────────
  const progress = document.getElementById("amare-progress");

  function progressStart() {
    if (!progress) return;
    progress.className = "";
    // força reflow para reiniciar a transição do zero
    void progress.offsetWidth;
    progress.className = "is-loading";
  }

  function progressDone() {
    if (!progress) return;
    progress.className = "is-done";
  }

  // ── Animação de entrada da página ─────────────────────────────────────────
  function animatePageIn() {
    const shell = document.querySelector(".amare-shell");
    if (!shell) return;
    shell.classList.remove("amare-page-in");
    void shell.offsetWidth; // força reflow para reiniciar animação
    shell.classList.add("amare-page-in");
  }

  // ── Eventos HTMX ──────────────────────────────────────────────────────────

  // Inicia a barra quando um request HTMX começa
  document.body.addEventListener("htmx:beforeRequest", progressStart);

  // Conclui a barra e anima o conteúdo novo após o swap
  document.body.addEventListener("htmx:afterSwap", (evt) => {
    progressDone();
    animatePageIn();

    // Reinicializa o Alpine.js apenas no elemento trocado pelo HTMX,
    // não em todo o document.body — evita percorrer o DOM inteiro a cada troca.
    if (window.Alpine && evt.detail && evt.detail.target) {
      window.Alpine.initTree(evt.detail.target);
    }
  });

  // Fallback: se o request falhar, encerra a barra igualmente
  document.body.addEventListener("htmx:responseError", progressDone);
  document.body.addEventListener("htmx:sendError", progressDone);

  // Roda a animação também no carregamento inicial (primeira página)
  animatePageIn();
});

document.addEventListener("DOMContentLoaded", () => {
  const modalRoot = document.getElementById("modal-root");
  const toastRoot = document.getElementById("toast-root");

  document.body.addEventListener("closeModal", () => {
    if (modalRoot) {
      modalRoot.innerHTML = "";
    }
  });

  document.body.addEventListener("showToast", (event) => {
    if (!toastRoot) {
      return;
    }
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
});

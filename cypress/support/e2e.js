Cypress.on("window:before:load", (win) => {
  win.__AMARE_E2E__ = true;
});

Cypress.Commands.add("loginAs", (email) => {
  cy.visit("/login/");
  cy.get('input[name="email"]').type(email);
  cy.get('input[name="password"]').type("amare123!", { log: false });
  cy.get('button[type="submit"]').click();
  cy.get("body[data-user-id]", { timeout: 20000 }).then(($body) => {
    const userId = $body.attr("data-user-id");
    if (userId) {
      cy.window().then((win) => {
        win.localStorage.setItem(`amare_notif_asked_${userId}`, "1");
      });
    }
  });
});

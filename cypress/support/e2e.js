Cypress.on("window:before:load", (win) => {
  win.__AMARE_E2E__ = true;
});

Cypress.Commands.add("loginAs", (email) => {
  cy.visit("/login/");
  cy.get('input[name="email"]').type(email);
  cy.get('input[name="password"]').type("amare123!", { log: false });
  cy.get('button[type="submit"]').click();
});

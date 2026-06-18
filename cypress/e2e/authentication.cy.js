describe("Autenticacao e perfis", () => {
  it("redireciona visitante de pagina privada para o login", () => {
    cy.visit("/dashboard/");
    cy.location("pathname", { timeout: 20000 }).should("eq", "/login/");
    cy.location("search").should("eq", "?next=/dashboard/");
  });

  it("autentica paciente e abre sua jornada", () => {
    cy.loginAs("ana@amare.local");
    cy.location("pathname", { timeout: 20000 }).should("eq", "/dashboard/");
    cy.contains("h1", "Olá, Ana Beatriz").should("exist");

    cy.visit("/treatment/");
    cy.contains("h1", "Sua Jornada").should("exist");
  });

  it("autentica medica e abre pacientes sob seu cuidado", () => {
    cy.loginAs("dra.helen@amare.local");
    cy.location("pathname", { timeout: 20000 }).should("eq", "/doctor/patients/");
    cy.contains("h1", "Pacientes sob seu cuidado").should("exist");
  });

  it("autentica acompanhante e abre a jornada vinculada", () => {
    cy.loginAs("joao@amare.local");
    cy.location("pathname", { timeout: 20000 }).should("eq", "/partner/dashboard/");
    cy.contains("h1", "Olá, João Santos").should("exist");

    cy.visit("/partner/treatment/");
    cy.contains("h1", "Jornada de Ana").should("exist");
  });
});

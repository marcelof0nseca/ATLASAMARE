describe("Autenticacao e perfis", () => {
  it("redireciona visitante de pagina privada para o login", () => {
    cy.visit("/dashboard/");
    cy.location("pathname").should("eq", "/login/");
    cy.location("search").should("eq", "?next=/dashboard/");
  });

  it("autentica paciente e abre sua jornada", () => {
    cy.loginAs("ana@amare.local");
    cy.location("pathname").should("eq", "/dashboard/");
    cy.contains("h1", "Oi, Ana Beatriz").should("be.visible");

    cy.visit("/treatment/");
    cy.contains("h1", "Sua jornada de tratamento").should("be.visible");
  });

  it("autentica medica e abre pacientes sob seu cuidado", () => {
    cy.loginAs("dra.helen@amare.local");
    cy.location("pathname").should("eq", "/doctor/patients/");
    cy.contains("h1", "Pacientes sob seu cuidado").should("be.visible");
  });

  it("autentica acompanhante e abre a jornada vinculada", () => {
    cy.loginAs("joao@amare.local");
    cy.location("pathname").should("eq", "/partner/dashboard/");
    cy.contains("h1", "Oi, João Santos").should("be.visible");

    cy.visit("/partner/treatment/");
    cy.contains("h1", "Jornada de Ana").should("be.visible");
  });
});

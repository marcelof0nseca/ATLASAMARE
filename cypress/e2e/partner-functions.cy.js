describe("Funcionalidades do acompanhante", () => {
  beforeEach(() => {
    cy.loginAs("joao@amare.local");
    cy.location("pathname", { timeout: 20000 }).should("eq", "/partner/dashboard/");
  });

  it("acompanha a jornada compartilhada da paciente", () => {
    cy.visit("/partner/treatment/");
    cy.contains("h1", "Jornada de Ana").should("exist");
    cy.contains("Preparação hormonal").should("exist");
    cy.contains("Coleta de óvulos").should("exist");
    cy.contains("Onde ela está?").should("exist");
  });

  it("consulta medicamentos e compromissos na rotina", () => {
    cy.visit("/partner/routine/");
    cy.contains("h1", "Rotina de Ana").should("exist");
    cy.contains("Medicamentos de Ana").should("exist");

    cy.contains("button", "Consultas").should("exist");
    cy.contains("Lembre Ana 24h antes da consulta").should("exist");
  });

  it("respeita as permissões específicas do acompanhante", () => {
    cy.visit("/partner/routine/");
    cy.contains("button", "Diário de Sintomas").should("exist");
    cy.contains("Acesso restrito a este diário.").should("exist");

    cy.contains("button", "Recordações").should("exist");
    cy.contains("Você não tem acesso a esta aba como acompanhante.").should("exist");
  });

  it("acessa a Maya com orientações para oferecer apoio", () => {
    cy.visit("/partner/maya/");
    cy.contains("Assistente Maya").should("exist");
    cy.contains("como apoiar Ana").should("exist");
    cy.get('textarea[name="question"]').should("exist");
  });

  it("consulta perfil, vínculo e documentos compartilhados", () => {
    cy.visit("/partner/profile/");
    cy.contains("h1", "Seu perfil").should("exist");
    cy.contains("João Santos").should("exist");
    cy.contains("Ana Beatriz").should("exist");

    cy.visit("/partner/jornada/documentos/");
    cy.contains("h1", "Documentos").should("exist");
  });
});

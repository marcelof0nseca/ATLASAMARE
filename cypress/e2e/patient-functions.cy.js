describe("Funcionalidades da paciente", () => {
  beforeEach(() => {
    cy.loginAs("ana@amare.local");
    cy.location("pathname", { timeout: 20000 }).should("eq", "/dashboard/");
  });

  it("acompanha a timeline e o progresso do tratamento", () => {
    cy.visit("/treatment/");
    cy.contains("h1", "Sua Jornada").should("exist");
    cy.contains("Preparação hormonal").should("exist");
    cy.contains("Coleta de óvulos").should("exist");
    cy.contains("Acompanhamento embrionário").should("exist");
  });

  it("consulta agenda e medicações", () => {
    cy.visit("/routine/appointments/");
    cy.contains("h1", "Sua agenda com leitura simples").should("exist");
    cy.contains("Compromissos").should("exist");

    cy.contains("a", "Medicações").click();
    cy.location("pathname", { timeout: 20000 }).should("eq", "/routine/medications/");
    cy.contains("h1", "Sua rotina de medicações").should("exist");
    cy.contains("Agora").should("exist");
    cy.contains("Hoje").should("exist");
  });

  it("acessa documentos e vídeos liberados pela clínica", () => {
    cy.visit("/jornada/documentos/");
    cy.contains("h1", "Documentos").should("exist");
    cy.contains("Semana 1").should("exist");

    cy.visit("/jornada/videos/");
    cy.contains("h1", "Vídeos auxiliares").should("exist");
    cy.contains("Todas").should("exist");
  });

  it("acessa a assistente Maya e o contato da clínica", () => {
    cy.visit("/maya/");
    cy.contains("Assistente Maya").should("exist");
    cy.get('textarea[name="question"]').should("exist");
    cy.contains("a", "Contato da clínica")
      .should("have.attr", "href")
      .and("include", "wa.me/5581998003535");
  });

  it("explora comunidades e parceiros de apoio", () => {
    cy.visit("/comunidades/");
    cy.contains("h1", "Você não está sozinha").should("exist");

    cy.visit("/explore/partners/");
    cy.contains("h1", "Parceiros multidisciplinares").should("exist");
  });
});

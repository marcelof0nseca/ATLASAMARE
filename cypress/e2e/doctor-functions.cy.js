describe("Funcionalidades da médica", () => {
  beforeEach(() => {
    cy.loginAs("dra.helen@amare.local");
    cy.location("pathname", { timeout: 20000 }).should("eq", "/doctor/patients/");
  });

  it("busca uma paciente e abre seus detalhes clínicos", () => {
    cy.get('input[name="q"]').type("Ana");
    cy.contains("button", "Buscar").click();
    cy.contains("Ana Beatriz").click();

    cy.contains("h1", "Ana Beatriz").should("exist");
    cy.contains("Dados essenciais").should("exist");
    cy.contains("Etapa atual").should("exist");
    cy.contains("Próximos compromissos").should("exist");
  });

  it("acessa o cadastro de nova paciente", () => {
    cy.visit("/doctor/patients/new/");
    cy.contains("h1", "Nova paciente").should("exist");
    cy.get('input[name="full_name"]').should("exist");
    cy.get('input[name="email"]').should("exist");
    cy.get('input[name="initial_password"]').should("exist");
    cy.contains("button", "Cadastrar paciente").should("exist");
  });

  it("acessa a criação de acompanhante a partir da paciente", () => {
    cy.visit("/doctor/patients/");
    cy.contains("Ana Beatriz").click();
    cy.contains("Acesso dos acompanhantes").should("exist");
    cy.contains("a", "Criar acesso").click();

    cy.contains("h1", "Criar acesso de acompanhante").should("exist");
    cy.contains("Paciente acompanhada").should("exist");
    cy.get('input[name="full_name"]').should("exist");
    cy.get('input[name="email"]').should("exist");
    cy.get('input[name="phone"]').should("exist");
    cy.get('input[name="initial_password"]').should("exist");
    cy.contains("button", "Criar acesso").should("exist");
  });

  it("gerencia a biblioteca de vídeos da jornada", () => {
    cy.visit("/doctor/jornada/videos/");
    cy.contains("h1", "Gerenciar vídeos da Jornada").should("exist");
    cy.contains("Vídeos cadastrados").should("exist");
    cy.contains("a", "+ Novo vídeo").should("have.attr", "href", "/doctor/jornada/videos/new/");
  });

  it("gerencia documentos disponibilizados às pacientes", () => {
    cy.visit("/doctor/jornada/documentos/");
    cy.contains("h1", "Gerenciar Documentos da Jornada").should("exist");
    cy.contains("Arquivos cadastrados").should("exist");
    cy.contains("a", "+ Novo Documento").should("have.attr", "href", "/doctor/jornada/documentos/new/");
  });
});

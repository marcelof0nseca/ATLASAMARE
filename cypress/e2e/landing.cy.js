describe("Landing publica", () => {
  beforeEach(() => {
    cy.visit("/landing/");
  });

  it("apresenta os principais conteudos e acesso ao login", () => {
    cy.contains("h1", "Uma jornada.").should("be.visible");
    cy.contains("a", "Entrar").first().should("have.attr", "href", "/login/");
    cy.contains("a", "Conhecer a plataforma").should("have.attr", "href", "#features");
    cy.contains("a", "Ver como funciona").should("have.attr", "href", "#how-it-works");
  });

  it("direciona contatos comerciais ao WhatsApp", () => {
    cy.contains("a", "Falar com a AMARE")
      .should("have.attr", "href")
      .and("include", "wa.me/5581998003535");

    cy.contains("a", "Agendar demonstração")
      .should("have.attr", "href")
      .and("include", "wa.me/5581998003535");

    cy.contains("a", "Falar com nossa equipe")
      .should("have.attr", "href")
      .and("include", "wa.me/5581998003535");
  });

  it("exibe o Instagram oficial no rodape", () => {
    cy.contains("a", "@clinicaamare")
      .should("be.visible")
      .and("have.attr", "href", "https://www.instagram.com/clinicaamare/");
  });

  it("apresenta perguntas frequentes alinhadas às funcionalidades reais", () => {
    cy.contains(".faq-question-text", "Para quem é a plataforma AMARE?").should("exist");
    cy.contains(".faq-question-text", "O que a paciente consegue acompanhar?").should("exist");
    cy.contains(".faq-question-text", "O que o acompanhante pode acessar?").should("exist");
    cy.contains(".faq-question-text", "Como é feita a cobrança").should("not.exist");
    cy.contains(".faq-question-text", "Há treinamento incluído").should("not.exist");
  });
});

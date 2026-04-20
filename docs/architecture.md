# Arquitetura do MVP

## Dominios

- `users`: autenticacao, perfil, vinculo medico-paciente e area medica
- `treatments`: tratamento ativo, etapas ordenadas e transicoes validas
- `appointments`: consultas e exames organizados por data
- `medications`: doses agendadas e confirmacao unica
- `assistant`: conversas guiadas da Maya, triagem de intencao e risco, guardrails e integracao opcional com LLM
- `core`: dashboard, mixins, seed e layout compartilhado

## Camadas

- Modelos: regras estruturais do dominio
- Servicos: transicoes de etapa, conclusao de dose, dashboard e Maya
- Views web: paginas server-rendered com HTMX para interacoes leves
- API DRF: rotas em `/api/v1` para os mesmos dominios

## Maya

- Cria tres conversas guiadas por paciente:
  - `treatment`
  - `routine`
  - `feelings`
- Classifica cada pergunta em `treatment`, `routine`, `feelings`, `symptom` ou `general`
- Marca risco como `low`, `medium` ou `high`
- Usa contexto seguro da jornada, sem acessar detalhes clinicos sensiveis no prompt do MVP
- Mantem historico separado por conversa para reduzir confusao e carga cognitiva
- Em sintomas ou sinais de risco, faz handoff para a equipe medica em vez de improvisar conduta

## Permissoes

- Paciente acessa apenas os proprios dados
- Medico acessa apenas pacientes sob sua responsabilidade
- Atualizacao de etapas so ocorre via acoes validas do fluxo
- Conclusao de medicacao so pode acontecer uma vez por dose
- Conversas e interacoes da Maya ficam restritas a propria paciente

## Banco

- PostgreSQL quando `POSTGRES_DB` estiver configurado
- SQLite como fallback local para desenvolvimento rapido e testes simples

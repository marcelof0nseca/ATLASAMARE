# AMARE — Plataforma Clínica de Fertilidade

## Visão Geral

O **AMARE** é uma plataforma digital desenvolvida para clínicas de fertilização, com o objetivo de centralizar o tratamento, a rotina e a comunicação entre paciente, médico e clínica.

A proposta é transformar uma jornada complexa e emocionalmente difícil em uma experiência mais **clara, organizada e acolhedora**.

> “Um espaço digital que cuida da paciente enquanto ela cuida de si.”

---

## Problema

O tratamento de fertilidade é:

- Complexo  
- Emocionalmente desgastante  
- Fragmentado entre diferentes sistemas e processos  

---

## Missão

Tornar a jornada da paciente:

- Clara  
- Organizada  
- Acolhedora  

---

## Usuários

### Paciente
- Acompanha o tratamento  
- Organiza rotina (consultas, exames, medicações)  
- Tira dúvidas  

### Médico
- Acompanha pacientes  
- Atualiza tratamentos  
- Analisa exames  

### Supervisor (Admin)
- Gerencia o sistema  
- Controla acessos  
- Resolve problemas  

---

## Funcionalidades Principais

### Tratamento
- Timeline interativa  
- Status das etapas:
  - Pendente  
  - Em andamento  
  - Concluído  
- Atualização em tempo real  

---

### Rotina
- Agenda (consultas + exames)  
- Controle de medicação  
- Lembretes automáticos  

---

### Assistente Maya
- Responde dúvidas frequentes  
- Explica etapas do tratamento  
- Interface conversacional simples  

---

### Documentos
- Upload de exames  
- Organização por categoria  
- Compartilhamento com médicos  

---

### 👤 Gestão de Usuários
- Perfis:
  - Paciente  
  - Médico  
  - Supervisor  
- Controle de permissões  

---

### Notificações
- Consultas  
- Medicação  
- Alertas personalizados  
- Suporte a acessibilidade  

---

## Arquitetura Técnica

- **Backend:** Django  
- **API:** Django REST Framework  
- **Banco de Dados:** PostgreSQL  

---

## Estrutura do Projeto

```bash
users/
treatments/
appointments/
documents/
notifications/
assistant/

# Handoff: Nova tela de Login · AMARE

## Visão geral
Reformulação editorial da tela de login do portal da paciente AMARE (clínica de fertilização in vitro). A direção escolhida é **"Carta"** — tipografia serifada de grande escala como protagonista, formulário em linhas (sem caixas), atmosfera acolhedora com paleta creme + rosé antigo.

## Sobre os arquivos de design
Os arquivos deste pacote (`Login.html`, `src/*.jsx`, `assets/`) são **referências de design criadas em HTML/React** — protótipos demonstrando aparência e comportamento pretendidos. **Não são código de produção para copiar diretamente.** A tarefa é **recriar esses designs no ambiente do projeto-alvo** (React, Vue, Next.js, Vite, Angular, etc.), usando os padrões, bibliotecas e arquitetura já estabelecidos. Mantenha o protótipo aberto durante a implementação como referência visual.

## Fidelidade
**Alta fidelidade (hi-fi).** Cores, tipografia, espaçamentos, animações e estados estão definidos. O desenvolvedor deve reproduzir o resultado pixel-perfect dentro das convenções do código existente.

---

## Tela única: Login

### Propósito
Permitir que a paciente entre no portal usando e-mail + senha.

### Layout (desktop, sem scroll)
A página é dimensionada exatamente para `100vh` × `100vw` — **nunca deve haver scroll**. Estrutura vertical em três faixas:

```
┌────────────────────────────────────────────────────────────────┐
│  HEADER  (logo AMARE à esquerda)                               │  ~80px
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────────────────────┐    ┌──────────────────────────┐ │
│   │ olá de novo,             │    │   E-MAIL                 │ │
│   │                          │    │   _____________________  │ │
│   │ a vida                   │    │                          │ │  flex: 1
│   │ que floresce             │    │   SENHA           mostrar│ │  (centro
│   │ devagar.                 │    │   _____________________  │ │   vertical)
│   │                          │    │                          │ │
│   │ "o cuidado continua..."  │    │   [ entrar → ]  esqueci  │ │
│   │                          │    │                          │ │
│   └──────────────────────────┘    └──────────────────────────┘ │
│         60% largura                       40% largura          │
│                                                                 │
├────────────────────────────────────────────────────────────────┤
│  amare · cuidado em cada detalhe              privacidade · ajuda │  ~50px
└────────────────────────────────────────────────────────────────┘
```

- Container raiz: `height: 100vh; overflow: hidden; display: flex; flex-direction: column;`
- Header: `flex-shrink: 0`, padding lateral `clamp(28px, 5vw, 64px)`, padding-top `clamp(20px, 3vh, 36px)`
- Main: `flex: 1; min-height: 0; display: grid; grid-template-columns: minmax(0, 1.15fr) minmax(340px, 1fr); gap: clamp(32px, 5vw, 90px); align-items: center; padding: clamp(16px, 3vh, 40px) clamp(28px, 5vw, 64px); overflow: hidden;`
- Footer: `flex-shrink: 0`, padding `clamp(12px, 2vh, 22px) clamp(28px, 5vw, 64px)`

### Componentes

#### 1. Header — Logo
- Imagem: `assets/amare-logo.png` (PNG transparente, 895×382 px)
- Altura responsiva: `clamp(40px, 5.5vh, 56px)`, largura `auto`
- Não selecionável, não arrastável

#### 2. Hero (coluna esquerda)
**Intro italic**
- Texto: `olá de novo,`
- Fonte: Cormorant Garamond, italic, weight 400
- Tamanho: `clamp(16px, 2vh, 22px)`
- Cor: cor de destaque (rosé `#B6796F` no padrão)
- `letter-spacing: 0.01em; margin-bottom: clamp(10px, 1.6vh, 20px);`

**Headline**
- Texto em três linhas: `a vida` / `que floresce` / `devagar.`
- Fonte: Cormorant Garamond, weight 400, normal
- Tamanho: `clamp(52px, min(7.5vw, 12vh), 116px)`
- `line-height: 0.95; letter-spacing: -0.02em; margin: 0; color: #2A1F15;`
- A palavra `floresce` é envolvida em `<em>` italic, weight 500, cor de destaque
- Cada linha é um `<span class="hl-mask">` com `overflow: hidden; padding: 0.06em 0.06em 0.22em; margin-bottom: -0.18em;` (a margem negativa compensa o padding extra que dá folga para descendentes como o "g" de "devagar"). A última `.hl-mask` zera o margin-bottom.

**Blurb**
- Texto: `o cuidado continua de onde paramos. seu ciclo, suas conversas e seu time esperam por você — sem pressa.`
- Fonte: Cormorant Garamond, italic
- Tamanho: `clamp(14px, 1.8vh, 18px)`
- `line-height: 1.5; color: #5F4B3A; max-width: 420px; margin-top: clamp(16px, 3vh, 32px);`

#### 3. Formulário (coluna direita)
- `max-width: 420px`
- Dois campos com **rótulo acima + linha embaixo** (sem caixa):

**Rótulo (label)**
- Fonte: Manrope, weight 500
- `font-size: 11px; letter-spacing: 0.22em; text-transform: uppercase;`
- Cor: `#5F4B3A` em estado normal, **cor de destaque** quando o campo está focado
- Transição: `color 0.3s ease; margin-bottom: 8px;`

**Input (linha)**
- `border: 0; outline: 0; background: transparent;`
- `padding: 8px 0 10px; padding-right: 44px` (se houver botão à direita)
- Fonte: Cormorant Garamond, 22px, color `#2A1F15`, line-height 1.3
- `caret-color: <accent>`
- **Linha base estática:** `position: absolute; left: 0; right: 0; bottom: 0; height: 1px; background: rgba(42,31,21,0.18)`
- **Linha de foco animada:** `position: absolute; left: 0; bottom: 0; height: 2px; background: <accent>; width: 0%` → `100%` no foco, transição `width 0.55s cubic-bezier(.45,.02,.2,1); border-radius: 2px;`

**Botão "mostrar/ocultar" senha**
- Posicionado à direita do input
- Texto: `mostrar` / `ocultar`
- Cormorant Garamond italic 13px, cor `#5F4B3A`, opacity 0.7 → 1 no hover

**Erro inline**
- Fonte: Cormorant Garamond italic 14px
- Cor: cor de destaque
- Espaço sempre reservado (`min-height: 18px`); transição opacity + translateY
- Regras:
  - E-mail vazio/inválido: `preciso de um e-mail válido para continuar`
  - Senha < 6 chars: `sua senha tem ao menos 6 caracteres`

**Botão entrar**
- Pílula: `border-radius: 999px; padding: 14px 28px; min-width: 200px;`
- Background: cor de destaque
- Fonte: Cormorant Garamond 19px, cor branca
- `box-shadow: 0 6px 20px -8px <accent>88;`
- Estados:
  - `idle`: mostra texto "entrar" + seta SVG (→ desloca 4px à direita no hover; bg escurece para `<accent-deep>`; translateY -1px)
  - `loading`: spinner branco (rotate 0.9s linear infinite), texto "abrindo seu espaço…", botão `scale(0.98)`, disabled
  - `done`: bg muda para **sálvia `#8B9D7E`** (não acento), check mark animado, texto "bem-vinda"
- Sequência demo: idle → click → loading (1500ms) → done → idle (2700ms depois)

**Link "esqueci minha senha"**
- Cormorant Garamond italic 16px, cor `#5F4B3A`
- Hover: cor de destaque + border-bottom 1px da mesma cor

#### 4. Footer
- Esquerda: `amare · cuidado em cada detalhe` (Manrope 11px, letter-spacing 0.16em, uppercase, color `#9A876F`)
- Direita: `privacidade   ajuda` (mesmo estilo; hover → color `#5F4B3A`)

---

## Animações de entrada
Acontecem no carregamento, uma única vez. Todas usam `opacity: 0 → 1` + transform. Easing recomendado: `cubic-bezier(.2,.7,.2,1)` ou ease.

| # | Elemento        | Delay   | Duração | Transform                          |
|---|-----------------|---------|---------|------------------------------------|
| 1 | Header          | 200ms   | 900ms   | fade                               |
| 2 | Intro italic    | 350ms   | 1000ms  | translateY(8px) → 0                |
| 3 | Headline linha 1| 500ms   | 1100ms  | translateY(110%) rotate(2deg) → 0 (atrás de `overflow: hidden`) |
| 4 | Headline linha 2| 680ms   | 1100ms  | idem                               |
| 5 | Headline linha 3| 860ms   | 1100ms  | idem                               |
| 6 | Blurb           | 1200ms  | 1000ms  | translateY(8px) → 0                |
| 7 | Form            | 1400ms  | 1200ms  | translateY(20px) → 0               |

Status pulsando (badge) e ilustração botânica não estão na versão final (configuração padrão).

---

## Interações & comportamento

- **Foco do campo** revela linha sólida animada da esquerda para a direita; rótulo recolore na cor de destaque
- **Enter no e-mail** → foca campo senha
- **Enter na senha** → submete
- **Submit** valida e-mail e senha:
  - Regex e-mail: `/^[^\s@]+@[^\s@]+\.[^\s@]+$/`
  - Senha: `length >= 6`
- **Loading state:** 1500ms (apenas demo — substituir por chamada real de API)
- **Success state:** mostrado por 2700ms antes de voltar a `idle` (apenas demo — em produção, redirecionar para a área da paciente)
- **Botão de mostrar senha** alterna `type="password" ↔ "text"`

---

## State (React) ou equivalente

```ts
const [email, setEmail] = useState('');
const [password, setPassword] = useState('');
const [showPwd, setShowPwd] = useState(false);
const [focused, setFocused] = useState<null | 'email' | 'password'>(null);
const [errors, setErrors] = useState<{ email?: string; password?: string }>({});
const [state, setState] = useState<'idle' | 'loading' | 'done'>('idle');
```

Em produção, substituir o setTimeout do submit por:
```ts
await api.login({ email, password });
// redirecionar ou mostrar erro real
```

---

## Design tokens

### Cores
```
--cream:       #F3E9D7   /* fundo principal */
--cream-soft:  #FAF3E6
--cream-deep:  #E6D8BD
--paper:       #FFFCF6

--ink:         #2A1F15   /* texto principal */
--ink-2:       #5F4B3A   /* texto secundário */
--ink-3:       #9A876F   /* texto auxiliar/footer */
--ink-faint:   #C9BAA0

--line:        rgba(42,31,21,0.18)
--line-strong: rgba(42,31,21,0.4)

/* Acento — rosé é o padrão final */
--accent:      #B6796F   /* rosé */
--accent-deep: #8E5A52
--accent-soft: #D9B5AD

/* Acentos alternativos (não usados na versão final, mas no design system) */
terracota:  accent #B3633F  deep #8C4A2C  soft #E0B89F
sálvia:     accent #7C8F70  deep #5C6E54  soft #BCC8B0
dourado:    accent #A88142  deep #7E5F2D  soft #D9BE8C

--sage:      #8B9D7E       /* usado no botão "bem-vinda" */
--sage-soft: #C7D2B9
```

### Tipografia
- **Display/serifa:** `'Cormorant Garamond', 'Hoefler Text', Georgia, serif` — pesos 400, 500; ital 400, 500
- **Sans (UI/labels/footer):** `'Manrope', ui-sans-serif, system-ui, sans-serif` — pesos 300, 400, 500
- Importação Google Fonts:
  ```
  https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,300;1,400;1,500;1,600&family=Manrope:wght@300;400;500;600&display=swap
  ```

### Espaçamentos & raios
- Padding lateral do container: `clamp(28px, 5vw, 64px)`
- Padding vertical de blocos: `clamp(16px, 3vh, 40px)` (main), `clamp(20px, 3vh, 36px)` (header)
- Botão pílula: radius `999px`
- Linha de input: radius `2px` (na barra de foco animada)

### Sombras
- Botão: `0 6px 20px -8px <accent>88`
- Nada de cards/elevações além disso

### Background "filme"
Gradientes radiais sutis aplicados em `body::before` com `mix-blend-mode: multiply; opacity: 0.8;`:
```css
background:
  radial-gradient(120% 80% at 50% 30%, rgba(255,251,240,0.6) 0%, transparent 60%),
  radial-gradient(80% 60% at 20% 100%, rgba(230,216,189,0.55) 0%, transparent 60%);
```

---

## Assets
- `assets/amare-logo.png` — logo oficial AMARE com fundo já tornado transparente. **Use este arquivo no projeto** (não a versão original em fundo branco).

---

## Cópia (todos os textos)
| Local              | Texto                                                                                                                |
|--------------------|----------------------------------------------------------------------------------------------------------------------|
| Intro              | `olá de novo,`                                                                                                       |
| Headline           | `a vida` / `que floresce` / `devagar.` (com `floresce` em italic acento)                                            |
| Blurb              | `o cuidado continua de onde paramos. seu ciclo, suas conversas e seu time esperam por você — sem pressa.`           |
| Label e-mail       | `e-mail`                                                                                                             |
| Label senha        | `senha`                                                                                                              |
| Mostrar/ocultar    | `mostrar` / `ocultar`                                                                                                |
| Botão idle         | `entrar`                                                                                                             |
| Botão loading      | `abrindo seu espaço…`                                                                                                |
| Botão done         | `bem-vinda`                                                                                                          |
| Recuperar          | `esqueci minha senha`                                                                                                |
| Erro e-mail        | `preciso de um e-mail válido para continuar`                                                                         |
| Erro senha         | `sua senha tem ao menos 6 caracteres`                                                                                |
| Footer esquerda    | `amare · cuidado em cada detalhe`                                                                                    |
| Footer direita     | `privacidade   ajuda`                                                                                                |

---

## Acessibilidade (mínimo)
- `<label htmlFor>` ligado a cada `<input id>`
- `aria-label` no botão mostrar/ocultar senha
- Foco visível: a linha animada já cumpre, mas adicionar fallback `:focus-visible` se necessário
- Contraste: texto principal `#2A1F15` em fundo `#F3E9D7` passa AAA. Texto secundário `#5F4B3A` passa AA. Texto auxiliar `#9A876F` passa AA grande (footer 11px — atenção, marginal; mantém na versão final por ser informacional)
- `prefers-reduced-motion`: ao implementar, desabilitar as animações de entrada quando o usuário pedir

---

## Responsividade
Design **prioritariamente desktop** (≥ 1024px). Em telas menores, o grid deve colapsar para uma coluna; recomenda-se ocultar a regra "nunca rolar" em mobile e empilhar hero acima do formulário com padding reduzido.

---

## Arquivos neste pacote
- `Login.html` — protótipo standalone (abrir no navegador para ver a versão final)
- `src/app.jsx` — componente principal (App, AmareLogo, Headline, footer)
- `src/login-form.jsx` — formulário, validação, estados do botão
- `src/botanical.jsx` — ilustração SVG botânica (não usada por padrão; disponível como variante via tweaks)
- `src/particles.jsx` — partículas flutuantes de fundo (idem, opcional)
- `src/all.jsx` — bundle de todos os scripts acima (apenas para o protótipo)
- `tweaks-panel.jsx` — painel de tweaks (não precisa portar; é só ferramenta de design)
- `assets/amare-logo.png` — logo AMARE com fundo transparente

Para inspecionar o protótipo, abrir `Login.html` em um navegador moderno.

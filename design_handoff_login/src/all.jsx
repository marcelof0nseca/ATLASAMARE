// ── botanical.jsx ──
// Botanical illustration — a delicate branch with leaves and one bloom.
// Stroke animates in on mount; geometry tuned to look hand-drawn.

function Botanical({ accent = '#B3633F', sage = '#8B9D7E', rose = '#C99B92', animated = true, style }) {
  const ref = React.useRef(null);
  React.useEffect(() => {
    if (!animated || !ref.current) return;
    const paths = ref.current.querySelectorAll('path[data-draw], ellipse[data-draw], circle[data-draw]');
    paths.forEach((el, i) => {
      const len = el.getTotalLength ? el.getTotalLength() : 200;
      el.style.transition = 'none';
      el.style.strokeDasharray = len;
      el.style.strokeDashoffset = len;
      el.style.opacity = 0;
      // force reflow
      // eslint-disable-next-line no-unused-expressions
      el.getBoundingClientRect();
      el.style.transition = `stroke-dashoffset 1.6s cubic-bezier(.4,0,.2,1) ${1200 + i*120}ms, opacity .8s ease ${1200 + i*120}ms`;
      el.style.strokeDashoffset = 0;
      el.style.opacity = 1;
    });
  }, [animated]);

  return (
    <svg ref={ref} viewBox="0 0 380 480" fill="none"
         style={{ overflow: 'visible', ...(style || {}) }}>
      {/* main stem */}
      <path data-draw
        d="M 200 470 C 195 400, 175 320, 200 240 S 230 130, 195 40"
        stroke={accent} strokeWidth="1.4" strokeLinecap="round" />

      {/* side branches */}
      <path data-draw
        d="M 198 320 C 230 310, 270 290, 310 270"
        stroke={accent} strokeWidth="1.2" strokeLinecap="round" opacity=".85" />
      <path data-draw
        d="M 200 260 C 165 250, 125 220, 90 200"
        stroke={accent} strokeWidth="1.2" strokeLinecap="round" opacity=".85" />
      <path data-draw
        d="M 198 180 C 230 170, 275 145, 305 110"
        stroke={accent} strokeWidth="1.1" strokeLinecap="round" opacity=".8" />
      <path data-draw
        d="M 198 105 C 175 95, 145 70, 130 40"
        stroke={accent} strokeWidth="1.1" strokeLinecap="round" opacity=".8" />

      {/* leaves — paired ellipses with veins */}
      <g opacity=".88">
        <g transform="translate(310 270) rotate(-30)">
          <path data-draw d="M 0 0 Q 18 -14, 36 0 Q 18 14, 0 0 Z"
            fill={sage} stroke={sage} strokeOpacity=".4" strokeWidth=".6" />
          <path data-draw d="M 0 0 L 36 0" stroke={accent} strokeWidth=".5" opacity=".5" />
        </g>
        <g transform="translate(90 200) rotate(28)">
          <path data-draw d="M 0 0 Q -18 -14, -36 0 Q -18 14, 0 0 Z"
            fill={sage} stroke={sage} strokeOpacity=".4" strokeWidth=".6" />
          <path data-draw d="M 0 0 L -36 0" stroke={accent} strokeWidth=".5" opacity=".5" />
        </g>
        <g transform="translate(305 110) rotate(-40)">
          <path data-draw d="M 0 0 Q 16 -12, 32 0 Q 16 12, 0 0 Z"
            fill={sage} stroke={sage} strokeOpacity=".4" strokeWidth=".6" />
          <path data-draw d="M 0 0 L 32 0" stroke={accent} strokeWidth=".5" opacity=".5" />
        </g>
        <g transform="translate(130 40) rotate(40)">
          <path data-draw d="M 0 0 Q -14 -10, -28 0 Q -14 10, 0 0 Z"
            fill={sage} stroke={sage} strokeOpacity=".4" strokeWidth=".6" />
        </g>
        {/* tiny leaves on stem */}
        <g transform="translate(202 360) rotate(85)">
          <path data-draw d="M 0 0 Q 10 -7, 20 0 Q 10 7, 0 0 Z" fill={sage} opacity=".7" />
        </g>
        <g transform="translate(196 150) rotate(85)">
          <path data-draw d="M 0 0 Q 10 -7, 20 0 Q 10 7, 0 0 Z" fill={sage} opacity=".7" />
        </g>
      </g>

      {/* bloom at top — small cluster */}
      <g transform="translate(195 35)">
        <circle data-draw cx="0" cy="0" r="10" fill={accent} opacity=".9" />
        <circle data-draw cx="-9" cy="6" r="6" fill={rose} opacity=".85" />
        <circle data-draw cx="8" cy="8" r="5" fill={accent} opacity=".75" />
        <circle data-draw cx="3" cy="-9" r="4" fill={rose} opacity=".7" />
      </g>

      {/* one fallen petal */}
      <ellipse data-draw cx="240" cy="420" rx="6" ry="3" fill={rose} opacity=".7" transform="rotate(40 240 420)" />
      <ellipse data-draw cx="160" cy="440" rx="5" ry="2.5" fill={accent} opacity=".55" transform="rotate(-20 160 440)" />
    </svg>
  );
}

window.Botanical = Botanical;


// ── particles.jsx ──
// Ambient floating particles — pollen / luz / small petals drifting slowly.
// Pure CSS animation, no JS per-frame work.

function Particles({ accent = '#B3633F', sage = '#8B9D7E', rose = '#C99B92', density = 22 }) {
  const items = React.useMemo(() => {
    const arr = [];
    for (let i = 0; i < density; i++) {
      const color = [accent, sage, rose][i % 3];
      arr.push({
        x: (i * 97 + 13) % 100,
        y: (i * 53 + 7) % 100,
        size: 3 + ((i * 7) % 6),
        dur: 18 + ((i * 3) % 18),
        delay: (i * 0.6) % 12,
        color,
        kind: i % 4 === 0 ? 'leaf' : 'dot',
        drift: ((i * 17) % 40) - 20,
        opacity: 0.18 + ((i % 5) * 0.05),
      });
    }
    return arr;
  }, [accent, sage, rose, density]);

  return (
    <div style={{ position: 'fixed', inset: 0, pointerEvents: 'none', overflow: 'hidden', zIndex: 0 }}>
      <style>{`
        @keyframes drift {
          0%   { transform: translate3d(0, 0, 0) rotate(0deg); }
          50%  { transform: translate3d(var(--drift, 12px), -28px, 0) rotate(15deg); }
          100% { transform: translate3d(0, 0, 0) rotate(0deg); }
        }
        @keyframes glow {
          0%, 100% { opacity: var(--op, .2); }
          50%      { opacity: calc(var(--op, .2) * 1.8); }
        }
        .pt { position: absolute; will-change: transform, opacity;
              animation: drift var(--dur, 20s) ease-in-out infinite,
                         glow calc(var(--dur, 20s) * 0.6) ease-in-out infinite;
              animation-delay: var(--delay, 0s); }
      `}</style>
      {items.map((p, i) => (
        <span key={i} className="pt"
          style={{
            left: p.x + '%', top: p.y + '%',
            width: p.size, height: p.size,
            '--drift': p.drift + 'px',
            '--dur': p.dur + 's',
            '--delay': p.delay + 's',
            '--op': p.opacity,
            opacity: p.opacity,
          }}>
          {p.kind === 'leaf' ? (
            <svg viewBox="0 0 12 12" width={p.size} height={p.size}>
              <path d="M6 1 Q9 4, 9 7 Q6 11, 3 7 Q3 4, 6 1 Z" fill={p.color}/>
            </svg>
          ) : (
            <span style={{
              display: 'block', width: '100%', height: '100%',
              borderRadius: '50%', background: p.color,
              boxShadow: `0 0 ${p.size * 2}px ${p.color}40`,
            }}/>
          )}
        </span>
      ))}
    </div>
  );
}

window.Particles = Particles;


// ── login-form.jsx ──
// AMARE login form — editorial style: line inputs, big serif headline integration,
// graceful submit / loading / success states.

const STR = {
  intro: 'olá de novo,',
  headline: { l1: 'a vida', l2: 'que floresce', l3: 'devagar.' },
  highlight: 'floresce',
  blurb: 'o cuidado continua de onde paramos. seu ciclo, suas conversas e seu time esperam por você — sem pressa.',
  emailLabel: 'e-mail',
  passwordLabel: 'senha',
  emailPh: 'seu@email.com',
  passwordPh: 'sua senha',
  submit: 'entrar',
  submitLoading: 'abrindo seu espaço…',
  submitDone: 'bem-vinda',
  recover: 'esqueci minha senha',
  errEmail: 'preciso de um e-mail válido para continuar',
  errPassword: 'sua senha tem ao menos 6 caracteres',
};

function Field({ id, label, type = 'text', value, onChange, onFocus, onBlur, focused, autoComplete, accent, error, onEnter, rightSlot }) {
  return (
    <div style={{ marginBottom: 26 }}>
      <label htmlFor={id} style={{
        display: 'block',
        fontSize: 11, letterSpacing: '0.22em', textTransform: 'uppercase',
        color: focused ? accent : 'var(--ink-2)',
        fontWeight: 500,
        transition: 'color .3s ease',
        marginBottom: 8,
      }}>{label}</label>

      <div style={{ position: 'relative' }}>
        <input
          id={id}
          type={type}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onFocus={onFocus}
          onBlur={onBlur}
          autoComplete={autoComplete}
          onKeyDown={(e) => { if (e.key === 'Enter' && onEnter) onEnter(); }}
          style={{
            width: '100%',
            border: 0,
            outline: 0,
            background: 'transparent',
            padding: '8px 0 10px',
            paddingRight: rightSlot ? 44 : 0,
            fontFamily: 'var(--serif)',
            fontSize: 22,
            color: 'var(--ink)',
            lineHeight: 1.3,
            caretColor: accent,
          }}
        />
        {/* base line */}
        <div style={{
          position: 'absolute', left: 0, right: 0, bottom: 0, height: 1,
          background: 'var(--line)',
        }}/>
        {/* focus line — expands from left */}
        <div style={{
          position: 'absolute', left: 0, bottom: 0, height: 2,
          background: accent,
          width: focused ? '100%' : '0%',
          transition: 'width .55s cubic-bezier(.45,.02,.2,1)',
          borderRadius: 2,
        }}/>
        {rightSlot && (
          <div style={{ position: 'absolute', right: 0, bottom: 8, color: 'var(--ink-2)' }}>
            {rightSlot}
          </div>
        )}
      </div>

      <div style={{
        fontFamily: 'var(--serif)', fontStyle: 'italic',
        fontSize: 14, color: accent,
        marginTop: 8, minHeight: 18,
        opacity: error ? 1 : 0,
        transform: error ? 'translateY(0)' : 'translateY(-4px)',
        transition: 'opacity .35s ease, transform .35s ease',
      }}>
        {error || '\u00a0'}
      </div>
    </div>
  );
}

function LoginForm({ accent, accentDeep, accentSoft, animated }) {
  const [email, setEmail] = React.useState('');
  const [password, setPassword] = React.useState('');
  const [showPwd, setShowPwd] = React.useState(false);
  const [focused, setFocused] = React.useState(null);
  const [errors, setErrors] = React.useState({});
  const [state, setState] = React.useState('idle'); // idle | loading | done

  const isEmailOk = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  const isPwdOk = password.length >= 6;

  const submit = () => {
    if (state !== 'idle') return;
    const next = {};
    if (!isEmailOk) next.email = STR.errEmail;
    if (!isPwdOk) next.password = STR.errPassword;
    setErrors(next);
    if (Object.keys(next).length) return;

    setState('loading');
    setTimeout(() => setState('done'), 1500);
    setTimeout(() => setState('idle'), 4200);
  };

  const buttonLabel = state === 'loading' ? STR.submitLoading
                    : state === 'done'    ? STR.submitDone
                    : STR.submit;

  return (
    <form
      onSubmit={(e) => { e.preventDefault(); submit(); }}
      style={{
        width: '100%', maxWidth: 420,
        opacity: animated ? 0 : 1,
        transform: animated ? 'translateY(20px)' : 'none',
        animation: animated ? 'lf-rise 1.2s cubic-bezier(.2,.7,.2,1) 1.4s forwards' : 'none',
      }}
    >
      <style>{`
        @keyframes lf-rise { to { opacity: 1; transform: translateY(0); } }
        @keyframes lf-pulse { 0%,100%{opacity:.5} 50%{opacity:1} }
      `}</style>

      <Field
        id="email"
        label={STR.emailLabel}
        type="email"
        value={email}
        onChange={(v) => { setEmail(v); if (errors.email) setErrors({ ...errors, email: null }); }}
        onFocus={() => setFocused('email')}
        onBlur={() => setFocused(null)}
        focused={focused === 'email'}
        autoComplete="email"
        accent={accent}
        error={errors.email}
        onEnter={() => document.getElementById('password')?.focus()}
      />

      <Field
        id="password"
        label={STR.passwordLabel}
        type={showPwd ? 'text' : 'password'}
        value={password}
        onChange={(v) => { setPassword(v); if (errors.password) setErrors({ ...errors, password: null }); }}
        onFocus={() => setFocused('password')}
        onBlur={() => setFocused(null)}
        focused={focused === 'password'}
        autoComplete="current-password"
        accent={accent}
        error={errors.password}
        onEnter={submit}
        rightSlot={
          <button type="button" onClick={() => setShowPwd((s) => !s)}
            aria-label={showPwd ? 'esconder senha' : 'mostrar senha'}
            style={{
              border: 0, background: 'transparent', cursor: 'pointer',
              color: 'var(--ink-2)', padding: 4, fontSize: 13,
              fontFamily: 'var(--serif)', fontStyle: 'italic',
              opacity: .7, transition: 'opacity .2s',
            }}
            onMouseEnter={(e) => e.currentTarget.style.opacity = 1}
            onMouseLeave={(e) => e.currentTarget.style.opacity = .7}>
            {showPwd ? 'ocultar' : 'mostrar'}
          </button>
        }
      />

      <div style={{ display: 'flex', alignItems: 'center', gap: 24, marginTop: 16 }}>
        <button
          type="submit"
          disabled={state !== 'idle'}
          style={{
            position: 'relative',
            display: 'inline-flex', alignItems: 'center', gap: 14,
            padding: '14px 28px',
            border: 0, borderRadius: 999,
            background: state === 'done' ? 'var(--sage)' : accent,
            color: 'white',
            fontFamily: 'var(--serif)',
            fontSize: 19, letterSpacing: '.01em',
            cursor: state === 'idle' ? 'pointer' : 'default',
            boxShadow: `0 6px 20px -8px ${accent}88`,
            transition: 'background .45s ease, transform .2s ease, box-shadow .3s ease',
            transform: state === 'loading' ? 'scale(0.98)' : 'scale(1)',
            minWidth: 200,
            justifyContent: 'center',
            overflow: 'hidden',
          }}
          onMouseEnter={(e) => { if (state === 'idle') { e.currentTarget.style.background = accentDeep; e.currentTarget.style.transform = 'translateY(-1px)'; } }}
          onMouseLeave={(e) => { if (state === 'idle') { e.currentTarget.style.background = accent; e.currentTarget.style.transform = 'translateY(0)'; } }}
        >
          {state === 'loading' && (
            <span style={{
              width: 14, height: 14, borderRadius: '50%',
              border: '2px solid rgba(255,255,255,.35)', borderTopColor: 'white',
              animation: 'spin 0.9s linear infinite',
            }}/>
          )}
          {state === 'done' && (
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M3 8 L7 12 L13 4" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
                style={{ strokeDasharray: 20, strokeDashoffset: 0, animation: 'draw .5s ease-out' }}/>
            </svg>
          )}
          <span>{buttonLabel}</span>
          {state === 'idle' && (
            <svg width="22" height="12" viewBox="0 0 22 12" fill="none" style={{ transform: 'translateX(0)', transition: 'transform .3s ease' }} className="arrow">
              <path d="M1 6 H19 M14 1 L20 6 L14 11" stroke="white" strokeWidth="1.6" fill="none" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          )}
        </button>

        <a href="#" onClick={(e) => e.preventDefault()}
          style={{
            fontFamily: 'var(--serif)', fontStyle: 'italic', fontSize: 16,
            color: 'var(--ink-2)', textDecoration: 'none',
            borderBottom: '1px solid transparent',
            paddingBottom: 2,
            transition: 'color .3s, border-color .3s',
          }}
          onMouseEnter={(e) => { e.currentTarget.style.color = accent; e.currentTarget.style.borderBottomColor = accent; }}
          onMouseLeave={(e) => { e.currentTarget.style.color = 'var(--ink-2)'; e.currentTarget.style.borderBottomColor = 'transparent'; }}
        >
          {STR.recover}
        </a>
      </div>

      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
        @keyframes draw { from { stroke-dashoffset: 20; } to { stroke-dashoffset: 0; } }
        form button:hover .arrow { transform: translateX(4px) !important; }
      `}</style>
    </form>
  );
}

window.LoginForm = LoginForm;
window.STR = STR;


// ── app.jsx ──
// AMARE login — main app

function AmareLogo({ height }) {
  return (
    <img src="assets/amare-logo.png" alt="AMARE"
      style={{
        height: height || 'clamp(40px, 5.5vh, 56px)',
        width: 'auto',
        display: 'block',
        userSelect: 'none',
        WebkitUserDrag: 'none',
      }}
      draggable={false}
    />
  );
}

function Headline({ accent, animated }) {
  // Three lines, each revealed via mask. Highlight: word "floresce" italic accent.
  const lines = [STR.headline.l1, STR.headline.l2, STR.headline.l3];
  return (
    <h1 style={{
      fontFamily: 'var(--serif)',
      fontWeight: 400,
      fontSize: 'clamp(52px, min(7.5vw, 12vh), 116px)',
      lineHeight: 0.95,
      letterSpacing: '-0.02em',
      margin: 0,
      color: 'var(--ink)',
    }}>
      <style>{`
        @keyframes hl-line {
          from { transform: translateY(110%) rotate(2deg); }
          to   { transform: translateY(0) rotate(0deg); }
        }
        .hl-mask { display: block; overflow: hidden; padding: 0.06em 0.06em 0.22em; margin-bottom: -0.18em; }
        .hl-mask:last-child { margin-bottom: 0; }
        .hl-line { display: inline-block; will-change: transform; }
      `}</style>
      {lines.map((line, i) => (
        <span key={i} className="hl-mask">
          <span className="hl-line" style={{
            animation: animated ? `hl-line 1.1s cubic-bezier(.2,.7,.2,1) ${0.5 + i*0.18}s both` : 'none',
            transform: animated ? 'translateY(110%)' : 'none',
          }}>
            {line.split(STR.highlight).map((part, idx, arr) => (
              <React.Fragment key={idx}>
                {part}
                {idx < arr.length - 1 && (
                  <em style={{
                    color: accent,
                    fontStyle: 'italic',
                    fontWeight: 500,
                    position: 'relative',
                  }}>{STR.highlight}</em>
                )}
              </React.Fragment>
            ))}
          </span>
        </span>
      ))}
    </h1>
  );
}

// ─────────────────────────────────────────────────────────────────────────────

const ACCENTS = {
  terracotta: { name: 'Terracota', accent: '#B3633F', deep: '#8C4A2C', soft: '#E0B89F', tint: 'rgba(179,99,63,0.10)' },
  sage:       { name: 'Sálvia',    accent: '#7C8F70', deep: '#5C6E54', soft: '#BCC8B0', tint: 'rgba(124,143,112,0.10)' },
  rose:       { name: 'Rosé',      accent: '#B6796F', deep: '#8E5A52', soft: '#D9B5AD', tint: 'rgba(182,121,111,0.10)' },
  gold:       { name: 'Dourado',   accent: '#A88142', deep: '#7E5F2D', soft: '#D9BE8C', tint: 'rgba(168,129,66,0.10)' },
};

const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{
  "accent": "rose",
  "particles": false,
  "botanical": false,
  "animated": true
}/*EDITMODE-END*/;

function App() {
  const [t, setTweak] = useTweaks(TWEAK_DEFAULTS);
  const a = ACCENTS[t.accent] || ACCENTS.terracotta;

  // expose accent to CSS for the form's caret etc.
  React.useEffect(() => {
    document.documentElement.style.setProperty('--accent', a.accent);
    document.documentElement.style.setProperty('--accent-deep', a.deep);
    document.documentElement.style.setProperty('--accent-soft', a.soft);
    document.documentElement.style.setProperty('--accent-tint', a.tint);
  }, [a.accent, a.deep, a.soft, a.tint]);

  // remount key so animations replay when toggled
  const animKey = React.useMemo(() => Math.random(), [t.animated]);

  return (
    <div style={{
      height: '100vh',
      display: 'flex',
      flexDirection: 'column',
      position: 'relative',
      overflow: 'hidden',
    }}>
      {t.particles && <Particles accent={a.accent} sage="#8B9D7E" rose="#C99B92"/>}

      {/* botanical fixed bottom-right */}
      {t.botanical && (
        <div style={{
          position: 'fixed',
          right: 'min(4vw, 60px)',
          bottom: -40,
          width: 'min(38vh, 360px)',
          height: 'min(48vh, 460px)',
          pointerEvents: 'none',
          zIndex: 1,
          opacity: t.animated ? 0 : 1,
          animation: t.animated ? 'bot-fade 1.5s ease 1.0s forwards' : 'none',
        }}>
          <style>{`@keyframes bot-fade { to { opacity: 1; } }`}</style>
          <Botanical key={animKey + '-bot'} accent={a.accent} sage="#8B9D7E" rose="#C99B92" animated={t.animated} style={{ width: '100%', height: '100%' }}/>
        </div>
      )}

      {/* top bar */}
      <header style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: 'clamp(20px, 3vh, 36px) clamp(28px, 5vw, 64px) 0',
        position: 'relative', zIndex: 2,
        flexShrink: 0,
        opacity: t.animated ? 0 : 1,
        animation: t.animated ? 'top-fade .9s ease .2s forwards' : 'none',
      }}>
        <style>{`@keyframes top-fade { to { opacity: 1; } }`}</style>
        <AmareLogo/>
      </header>

      {/* main editorial spread */}
      <main key={animKey} style={{
        flex: 1,
        minHeight: 0,
        display: 'grid',
        gridTemplateColumns: 'minmax(0, 1.15fr) minmax(340px, 1fr)',
        gap: 'clamp(32px, 5vw, 90px)',
        padding: 'clamp(16px, 3vh, 40px) clamp(28px, 5vw, 64px)',
        alignItems: 'center',
        position: 'relative', zIndex: 2,
        overflow: 'hidden',
      }}>
        {/* left: hero */}
        <section style={{ minWidth: 0 }}>
          <div style={{
            fontFamily: 'var(--serif)', fontStyle: 'italic',
            fontSize: 'clamp(16px, 2vh, 22px)', color: a.accent,
            marginBottom: 'clamp(10px, 1.6vh, 20px)',
            opacity: t.animated ? 0 : 1,
            animation: t.animated ? 'intro-fade 1s ease .35s forwards' : 'none',
            letterSpacing: '0.01em',
          }}>
            <style>{`@keyframes intro-fade { to { opacity: 1; transform: translateY(0); } from { opacity: 0; transform: translateY(8px); } }`}</style>
            {STR.intro}
          </div>

          <Headline accent={a.accent} animated={t.animated}/>

          <p style={{
            fontFamily: 'var(--serif)',
            fontStyle: 'italic',
            fontSize: 'clamp(14px, 1.8vh, 18px)',
            lineHeight: 1.5,
            color: 'var(--ink-2)',
            maxWidth: 420,
            marginTop: 'clamp(16px, 3vh, 32px)',
            marginBottom: 0,
            opacity: t.animated ? 0 : 1,
            animation: t.animated ? 'blurb-fade 1s ease 1.2s forwards' : 'none',
          }}>
            <style>{`@keyframes blurb-fade { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }`}</style>
            {STR.blurb}
          </p>
        </section>

        {/* right: form */}
        <section style={{
          display: 'flex', justifyContent: 'flex-start', alignItems: 'flex-start',
          flexDirection: 'column',
          minWidth: 0,
        }}>
          <LoginForm
            accent={a.accent}
            accentDeep={a.deep}
            accentSoft={a.soft}
            animated={t.animated}
          />
        </section>
      </main>

      {/* footer line */}
      <footer style={{
        padding: 'clamp(12px, 2vh, 22px) clamp(28px, 5vw, 64px)',
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        fontSize: 11, letterSpacing: '0.16em', textTransform: 'uppercase',
        color: 'var(--ink-3)',
        position: 'relative', zIndex: 2,
        flexShrink: 0,
      }}>
        <span>amare · cuidado em cada detalhe</span>
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: 18 }}>
          <a href="#" onClick={(e) => e.preventDefault()} style={{ color: 'inherit', textDecoration: 'none' }}
            onMouseEnter={(e) => e.currentTarget.style.color = 'var(--ink-2)'}
            onMouseLeave={(e) => e.currentTarget.style.color = 'var(--ink-3)'}>privacidade</a>
          <a href="#" onClick={(e) => e.preventDefault()} style={{ color: 'inherit', textDecoration: 'none' }}
            onMouseEnter={(e) => e.currentTarget.style.color = 'var(--ink-2)'}
            onMouseLeave={(e) => e.currentTarget.style.color = 'var(--ink-3)'}>ajuda</a>
        </span>
      </footer>

      <TweaksPanel>
        <TweakSection label="Cor de destaque"/>
        <TweakColor
          label="Acento"
          value={a.accent}
          options={Object.values(ACCENTS).map((x) => x.accent)}
          onChange={(hex) => {
            const k = Object.keys(ACCENTS).find((key) => ACCENTS[key].accent === hex) || 'terracotta';
            setTweak('accent', k);
          }}
        />

        <TweakSection label="Atmosfera"/>
        <TweakToggle label="Partículas no fundo" value={t.particles}
          onChange={(v) => setTweak('particles', v)}/>
        <TweakToggle label="Ilustração botânica" value={t.botanical}
          onChange={(v) => setTweak('botanical', v)}/>
        <TweakToggle label="Animação de entrada" value={t.animated}
          onChange={(v) => setTweak('animated', v)}/>
      </TweaksPanel>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />);



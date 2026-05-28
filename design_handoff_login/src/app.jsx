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

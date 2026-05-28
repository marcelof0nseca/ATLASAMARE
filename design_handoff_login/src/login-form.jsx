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

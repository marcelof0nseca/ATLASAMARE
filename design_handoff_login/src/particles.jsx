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

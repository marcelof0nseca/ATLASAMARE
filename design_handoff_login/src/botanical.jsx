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

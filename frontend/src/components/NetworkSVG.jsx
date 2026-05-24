import { useEffect, useRef } from 'react'
import { STANCE_COLOR } from '../constants'
import styles from './NetworkSVG.module.css'

const W = 680, H = 390
const QX = 54, QY = H / 2, QR = 28
const CX = 626, CY = H / 2, CR = 40
const AR = 22

const AGENT_POS = [
  { x: 230, y: 70  },
  { x: 360, y: 132 },
  { x: 230, y: 195 },
  { x: 360, y: 257 },
  { x: 230, y: 320 },
  { x: 360, y: 382 },
]

function bezier(x1, y1, x2, y2) {
  const cx1 = x1 + (x2 - x1) * 0.45
  const cy1 = y1
  const cx2 = x1 + (x2 - x1) * 0.55
  const cy2 = y2
  return `M${x1},${y1} C${cx1},${cy1} ${cx2},${cy2} ${x2},${y2}`
}

export default function NetworkSVG({ verdicts, consensusStance }) {
  const svgRef = useRef(null)

  useEffect(() => {
    if (!svgRef.current) return
    const paths = svgRef.current.querySelectorAll('[data-draw]')
    const id = requestAnimationFrame(() => paths.forEach(p => p.classList.add(styles.lit)))
    return () => cancelAnimationFrame(id)
  }, [verdicts])

  const cCol = STANCE_COLOR[consensusStance] || '#7a92b4'

  return (
    <svg
      ref={svgRef}
      viewBox={`0 0 ${W} ${H}`}
      xmlns="http://www.w3.org/2000/svg"
      className={styles.svg}
    >
      <defs>
        <filter id="gq" x="-60%" y="-60%" width="220%" height="220%">
          <feGaussianBlur in="SourceGraphic" stdDeviation="5" result="b" />
          <feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
        <filter id="gc" x="-60%" y="-60%" width="220%" height="220%">
          <feGaussianBlur in="SourceGraphic" stdDeviation="9" result="b" />
          <feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
        {Object.entries(STANCE_COLOR).map(([s]) => (
          <filter key={s} id={`ga-${s}`} x="-60%" y="-60%" width="220%" height="220%">
            <feGaussianBlur in="SourceGraphic" stdDeviation="4" result="b" />
            <feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge>
          </filter>
        ))}
        <pattern id="dots" x="0" y="0" width="28" height="28" patternUnits="userSpaceOnUse">
          <circle cx="14" cy="14" r="0.9" fill="rgba(255,255,255,.04)" />
        </pattern>
      </defs>

      {/* dot grid */}
      <rect width={W} height={H} fill="url(#dots)" />

      {/* paths + particles */}
      {verdicts.map((v, i) => {
        const pos = AGENT_POS[i]
        if (!pos) return null
        const col = STANCE_COLOR[v.stance] || '#7a92b4'
        const isDis = v.stance !== consensusStance
        const d1 = bezier(QX + QR, QY, pos.x - AR, pos.y)
        const d2 = bezier(pos.x + AR, pos.y, CX - CR, CY)
        const pid1 = `pq${i}`, pid2 = `pa${i}`
        const dashArr = isDis ? '7 5' : undefined
        return (
          <g key={i}>
            <path id={pid1} className={`${styles.npath}`} data-draw="1"
              d={d1} stroke={col} opacity={isDis ? .32 : .52}
              strokeDasharray={dashArr}
              style={{ transitionDelay: `${0.08 + i * 0.09}s` }} />
            <path id={pid2} className={`${styles.npath}`} data-draw="1"
              d={d2} stroke={col} opacity={isDis ? .22 : .48}
              strokeDasharray={dashArr}
              style={{ transitionDelay: `${0.08 + i * 0.09 + 0.3}s` }} />
            {!isDis && (
              <>
                <circle r="3" fill={col} opacity=".8">
                  <animateMotion dur={`${1.9 + i * 0.28}s`} repeatCount="indefinite" begin={`${i * 0.38}s`}>
                    <mpath href={`#${pid1}`} />
                  </animateMotion>
                </circle>
                <circle r="3" fill={col} opacity=".65">
                  <animateMotion dur={`${1.7 + i * 0.28}s`} repeatCount="indefinite" begin={`${i * 0.38 + 0.6}s`}>
                    <mpath href={`#${pid2}`} />
                  </animateMotion>
                </circle>
              </>
            )}
          </g>
        )
      })}

      {/* agent nodes */}
      {verdicts.map((v, i) => {
        const pos = AGENT_POS[i]
        if (!pos) return null
        const col = STANCE_COLOR[v.stance] || '#7a92b4'
        const short = v.agent_name.replace(' Agent', '').replace(' Expert', '')
        // pick the first meaningful finding as a one-line label
        const finding = v.findings[0] || v.summary
        const findingShort = finding.length > 32 ? finding.slice(0, 32) + '…' : finding
        // label sits right or left depending on column
        const isLeft = pos.x < 300
        const labelX = isLeft ? pos.x - AR - 8 : pos.x + AR + 8
        const anchor  = isLeft ? 'end' : 'start'
        return (
          <g key={i}>
            <circle cx={pos.x} cy={pos.y} r={AR + 7} fill={col} opacity=".07"
              filter={`url(#ga-${v.stance})`} />
            <circle cx={pos.x} cy={pos.y} r={AR} fill="rgba(8,15,34,.88)"
              stroke={col} strokeWidth="1.5" opacity=".9" />
            <circle cx={pos.x} cy={pos.y} r="5" fill={col} opacity=".85" />
            {/* agent name above */}
            <text x={pos.x} y={pos.y - AR - 7} textAnchor="middle"
              fill={col} fontSize="10.5" fontFamily="Inter,system-ui,sans-serif"
              fontWeight="700" opacity=".9">
              {short}
            </text>
            {/* stance label */}
            <text x={pos.x} y={pos.y - AR - 19} textAnchor="middle"
              fill={col} fontSize="8" fontFamily="Inter,system-ui,sans-serif"
              fontWeight="800" opacity=".6" letterSpacing="1">
              {v.stance}
            </text>
            {/* key finding beside node */}
            <text x={labelX} y={pos.y + 4} textAnchor={anchor}
              fill="rgba(180,200,220,.55)" fontSize="9" fontFamily="Inter,system-ui,sans-serif">
              {findingShort}
            </text>
          </g>
        )
      })}

      {/* query node */}
      <circle cx={QX} cy={QY} r={QR + 8} fill="rgba(56,189,248,.07)" filter="url(#gq)" />
      <circle cx={QX} cy={QY} r={QR} fill="rgba(8,15,34,.92)"
        stroke="rgba(56,189,248,.5)" strokeWidth="1.8" />
      <text x={QX} y={QY - 4} textAnchor="middle" fill="#38bdf8"
        fontSize="8.5" fontFamily="Inter,system-ui,sans-serif" fontWeight="700">YOUR</text>
      <text x={QX} y={QY + 7} textAnchor="middle" fill="#38bdf8"
        fontSize="8.5" fontFamily="Inter,system-ui,sans-serif" fontWeight="700">QUERY</text>

      {/* consensus node */}
      <circle cx={CX} cy={CY} r={CR + 12} fill={cCol} opacity=".06" filter="url(#gc)" />
      <circle cx={CX} cy={CY} r={CR + 4} fill={cCol} opacity=".04" />
      <circle cx={CX} cy={CY} r={CR} fill="rgba(8,15,34,.92)"
        stroke={cCol} strokeWidth="2" />
      <text x={CX} y={CY - 8} textAnchor="middle" fill={cCol}
        fontSize="8.5" fontFamily="Inter,system-ui,sans-serif" fontWeight="700">EMERGENT</text>
      <text x={CX} y={CY + 5} textAnchor="middle" fill={cCol}
        fontSize="11" fontFamily="Inter,system-ui,sans-serif" fontWeight="900">
        {consensusStance}
      </text>
    </svg>
  )
}

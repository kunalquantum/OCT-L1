import { useEffect, useRef } from 'react'
import { STANCE_COLOR } from '../constants'
import styles from './AgentCard.module.css'

const RANK = { PROCEED: 0, CAUTION: 1, DELAY: 2, BLOCK: 3 }

function alignInfo(agentStance, consensusStance) {
  if (agentStance === consensusStance) return ['aligned', '✓ Adopted into consensus']
  return Math.abs(RANK[agentStance] - RANK[consensusStance]) >= 2
    ? ['dissenting', '✕ Overruled by majority']
    : ['divergent', '~ Noted — partial agreement']
}

const CIRC = 125.6

export default function AgentCard({ verdict, index, consensusStance }) {
  const fillRef = useRef(null)
  const [alignClass, alignLabel] = alignInfo(verdict.stance, consensusStance)
  const col = STANCE_COLOR[verdict.stance] || '#7a92b4'
  const offset = CIRC * (1 - verdict.confidence)

  useEffect(() => {
    const id = setTimeout(() => {
      if (fillRef.current) fillRef.current.style.strokeDashoffset = offset
    }, 80 + index * 70)
    return () => clearTimeout(id)
  }, [offset, index])

  return (
    <div
      className={styles.card}
      data-stance={verdict.stance}
      style={{ animationDelay: `${index * 0.07}s`, '--col': col }}
    >
      <div className={styles.top}>
        <div>
          <div className={styles.name}>{verdict.agent_name}</div>
          <div className={styles.tags}>
            <span className={`${styles.tag} ${styles[verdict.stance.toLowerCase()]}`}>
              {verdict.stance}
            </span>
            <span className={`${styles.abadge} ${styles[alignClass]}`}>{alignLabel}</span>
          </div>
        </div>

        {/* circular confidence gauge */}
        <div className={styles.gauge}>
          <svg viewBox="0 0 52 52" width="52" height="52" style={{ transform: 'rotate(-90deg)' }}>
            <circle className={styles.gtrack} cx="26" cy="26" r="20" />
            <circle
              ref={fillRef}
              className={styles.gfill}
              cx="26" cy="26" r="20"
              stroke={col}
              style={{ strokeDashoffset: CIRC }}
            />
          </svg>
          <div className={styles.gaugeInner}>
            <span className={styles.gPct}>{Math.round(verdict.confidence * 100)}%</span>
            <span className={styles.gSub}>conf</span>
          </div>
        </div>
      </div>

      {/* contribution banner */}
      <div className={`${styles.banner} ${styles[alignClass]}`}>{alignLabel}</div>

      <p className={styles.summary}>{verdict.summary}</p>

      {verdict.findings.length > 0 && (
        <div className={styles.findingsWrap}>
          <span className={styles.findingsHead}>What this agent found</span>
          <ul className={styles.findings}>
            {verdict.findings.map((f, i) => <li key={i}>{f}</li>)}
          </ul>
        </div>
      )}

      {verdict.blockers.length > 0 && (
        <div className={styles.blockers}>
          <span className={styles.blkHead}>Raised as blockers</span>
          {verdict.blockers.map((b, i) => (
            <div key={i} className={styles.blocker}>{b}</div>
          ))}
        </div>
      )}
    </div>
  )
}

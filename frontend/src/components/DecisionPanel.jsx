import { useEffect, useRef } from 'react'
import { STANCE_COLOR } from '../constants'
import styles from './DecisionPanel.module.css'

const STANCES = ['PROCEED', 'CAUTION', 'DELAY', 'BLOCK']
const CIRC = 263

export default function DecisionPanel({ consensus, verdicts, reliability }) {
  const gaugeFillRef = useRef(null)
  const relFillRef = useRef(null)
  const voteRefs = useRef([])

  const stance = consensus.overall_stance
  const col = STANCE_COLOR[stance] || '#7a92b4'
  const cf = consensus.confidence_score
  const gaugeOffset = CIRC * (1 - cf)

  const counts = STANCES.reduce((acc, s) => {
    acc[s] = verdicts.filter(v => v.stance === s).length
    return acc
  }, {})

  useEffect(() => {
    const id = setTimeout(() => {
      if (gaugeFillRef.current) gaugeFillRef.current.style.strokeDashoffset = gaugeOffset
      if (relFillRef.current) relFillRef.current.style.width = `${Math.round(reliability * 100)}%`
      voteRefs.current.forEach((el, i) => {
        if (el) el.style.width = `${Math.round(counts[STANCES.filter(s => counts[s] > 0)[i]] / verdicts.length * 100)}%`
      })
    }, 100)
    return () => clearTimeout(id)
  }, [gaugeOffset, reliability])

  const activeStances = STANCES.filter(s => counts[s] > 0)

  return (
    <div className={styles.panel}>
      {/* top band */}
      <div className={`${styles.band} ${styles[stance.toLowerCase()]}`}>
        <div className={styles.gauge}>
          <svg viewBox="0 0 96 96" style={{ transform: 'rotate(-90deg)', width: 96, height: 96 }}>
            <circle className={styles.gtrack} cx="48" cy="48" r="42" />
            <circle
              ref={gaugeFillRef}
              className={styles.gfill}
              cx="48" cy="48" r="42"
              stroke={col}
              style={{ strokeDashoffset: CIRC }}
            />
          </svg>
          <div className={styles.gaugeInner}>
            <span className={styles.gPct}>{Math.round(cf * 100)}%</span>
            <span className={styles.gLbl}>conf</span>
          </div>
        </div>

        <div className={styles.mid}>
          <span className={`${styles.badge} ${styles[stance.toLowerCase()]}`}>{stance}</span>
          <p className={styles.rec}>{consensus.recommendation}</p>
          <div className={styles.relRow}>
            <span>Reliability</span>
            <div className={styles.relTrack}>
              <div ref={relFillRef} className={styles.relFill} style={{ width: 0 }} />
            </div>
            <span className={styles.relVal}>{Math.round(reliability * 100)}%</span>
          </div>
        </div>

        <div className={styles.stats}>
          <div className={styles.stat}><span>Agents</span><strong>{verdicts.length}</strong></div>
          <div className={styles.stat}><span>Agreement</span><strong>{Math.round(reliability * 100)}%</strong></div>
          <div className={styles.stat}><span>Blockers</span><strong>{consensus.major_blockers.length}</strong></div>
        </div>
      </div>

      {/* body */}
      <div className={styles.body}>
        <div className={styles.votes}>
          <p className={styles.votesLbl}>Vote Breakdown</p>
          {activeStances.map((s, i) => (
            <div key={s} className={styles.vrow}>
              <span className={styles.vstance} style={{ color: STANCE_COLOR[s] }}>{s}</span>
              <div className={styles.vtrack}>
                <div
                  ref={el => voteRefs.current[i] = el}
                  className={styles.vfill}
                  style={{ background: STANCE_COLOR[s], width: 0 }}
                />
              </div>
              <span className={styles.vcnt}>{counts[s]}/{verdicts.length}</span>
            </div>
          ))}
        </div>

        {consensus.major_blockers.length > 0 && (
          <div className={styles.blockers}>
            <p className={styles.blkLbl}>Critical Blockers</p>
            {consensus.major_blockers.map((b, i) => (
              <div key={i} className={styles.blkCard}>{b}</div>
            ))}
          </div>
        )}
      </div>

      {consensus.dissenting_agents.length > 0 && (
        <div className={styles.foot}>
          Agents that diverged from consensus:{' '}
          <strong>{consensus.dissenting_agents.join(', ')}</strong>
        </div>
      )}
    </div>
  )
}

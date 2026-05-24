import styles from './DeliberationSummary.module.css'
import { STANCE_COLOR } from '../constants'

export default function DeliberationSummary({ verdicts, consensus, queryText }) {
  const cs = consensus.overall_stance

  const raised   = verdicts.filter(v => ['CAUTION','DELAY','BLOCK'].includes(v.stance))
  const cleared  = verdicts.filter(v => v.stance === 'PROCEED')
  const allBlk   = verdicts.flatMap(v => v.blockers)
  const uniqueBlk = [...new Set(allBlk)]

  // adopted = aligned with consensus; overruled = far from consensus
  const rank = { PROCEED:0, CAUTION:1, DELAY:2, BLOCK:3 }
  const adopted   = verdicts.filter(v => v.stance === cs)
  const overruled = verdicts.filter(v => Math.abs(rank[v.stance] - rank[cs]) >= 2)

  const short = q => q.length > 80 ? q.slice(0, 80) + '…' : q

  return (
    <div className={styles.panel}>

      {/* query recap */}
      <div className={styles.queryRow}>
        <span className={styles.queryIcon}>↳</span>
        <p className={styles.queryText}>&ldquo;{short(queryText)}&rdquo;</p>
      </div>

      {/* two-column deliberation */}
      <div className={styles.cols}>

        {/* issues raised */}
        {raised.length > 0 && (
          <div className={styles.col}>
            <div className={`${styles.colHead} ${styles.warn}`}>
              ⚠ Issues raised — {raised.length} agent{raised.length > 1 ? 's' : ''}
            </div>
            {raised.map(v => (
              <div key={v.agent_name} className={styles.item}>
                <span className={styles.itemAgent} style={{ color: STANCE_COLOR[v.stance] }}>
                  {v.agent_name}
                </span>
                <span className={styles.itemSum}>{v.summary}</span>
                {v.blockers.map((b,i) => (
                  <span key={i} className={styles.itemBlocker}>✖ {b}</span>
                ))}
              </div>
            ))}
          </div>
        )}

        {/* cleared */}
        {cleared.length > 0 && (
          <div className={styles.col}>
            <div className={`${styles.colHead} ${styles.ok}`}>
              ✓ Cleared — {cleared.length} agent{cleared.length > 1 ? 's' : ''}
            </div>
            {cleared.map(v => (
              <div key={v.agent_name} className={styles.item}>
                <span className={styles.itemAgent} style={{ color: STANCE_COLOR[v.stance] }}>
                  {v.agent_name}
                </span>
                <span className={styles.itemSum}>{v.summary}</span>
              </div>
            ))}
          </div>
        )}

      </div>

      {/* adopted vs overruled */}
      {(adopted.length > 0 || overruled.length > 0) && (
        <div className={styles.footer}>
          {adopted.length > 0 && (
            <div className={styles.footGroup}>
              <span className={styles.footLabel}>Adopted into consensus</span>
              {adopted.map(v => (
                <span key={v.agent_name} className={styles.footTag} style={{ borderColor: STANCE_COLOR[cs], color: STANCE_COLOR[cs] }}>
                  {v.agent_name}
                </span>
              ))}
            </div>
          )}
          {overruled.length > 0 && (
            <div className={styles.footGroup}>
              <span className={styles.footLabel}>Overruled by majority</span>
              {overruled.map(v => (
                <span key={v.agent_name} className={styles.footTag} style={{ borderColor: '#ef4444', color: '#f87171' }}>
                  {v.agent_name}
                </span>
              ))}
            </div>
          )}
          {consensus.dissenting_agents.length > 0 && (
            <div className={styles.footGroup}>
              <span className={styles.footLabel}>Dissented</span>
              {consensus.dissenting_agents.map(name => (
                <span key={name} className={styles.footTag} style={{ borderColor: 'var(--border)', color: 'var(--muted)' }}>
                  {name}
                </span>
              ))}
            </div>
          )}
        </div>
      )}

      {/* critical blockers */}
      {uniqueBlk.length > 0 && (
        <div className={styles.blockers}>
          <span className={styles.blkHead}>🚫 Critical blockers preventing consensus</span>
          <div className={styles.blkList}>
            {uniqueBlk.map((b, i) => (
              <div key={i} className={styles.blkItem}>{b}</div>
            ))}
          </div>
        </div>
      )}

    </div>
  )
}

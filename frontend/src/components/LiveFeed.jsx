import { useEffect, useRef } from 'react'
import { STANCE_COLOR } from '../constants'
import styles from './LiveFeed.module.css'

const STANCE_ICON = { PROCEED: '✓', CAUTION: '⚠', DELAY: '⏳', BLOCK: '✕' }

export default function LiveFeed({ verdicts, pending, done }) {
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [verdicts.length])

  return (
    <div className={styles.feed}>
      <div className={styles.header}>
        <span className={styles.pulse} data-active={!done} />
        <span className={styles.title}>
          {done ? 'All agents reported' : `${pending} agent${pending !== 1 ? 's' : ''} still reasoning…`}
        </span>
      </div>

      <div className={styles.messages}>
        {verdicts.map((v, i) => {
          const col = STANCE_COLOR[v.stance] || '#7a92b4'
          const icon = STANCE_ICON[v.stance] || '·'
          return (
            <div key={v.agent_name} className={styles.msg} style={{ animationDelay: `${i * 0.04}s` }}>
              <div className={styles.avatar} style={{ background: col + '22', borderColor: col + '66' }}>
                <span style={{ color: col }}>{icon}</span>
              </div>
              <div className={styles.bubble}>
                <div className={styles.bubbleTop}>
                  <span className={styles.agentName} style={{ color: col }}>{v.agent_name}</span>
                  <span className={styles.stancePill} style={{ background: col + '22', color: col }}>
                    {v.stance}
                  </span>
                  <span className={styles.conf}>{Math.round(v.confidence * 100)}% conf</span>
                </div>
                <p className={styles.summary}>{v.summary}</p>
                {v.findings.length > 0 && (
                  <ul className={styles.findings}>
                    {v.findings.slice(0, 3).map((f, fi) => <li key={fi}>{f}</li>)}
                  </ul>
                )}
                {v.blockers.length > 0 && (
                  <div className={styles.blockers}>
                    {v.blockers.slice(0, 2).map((b, bi) => (
                      <div key={bi} className={styles.blocker}>{b}</div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )
        })}

        {!done && (
          <div className={styles.typing}>
            <div className={styles.dot} />
            <div className={styles.dot} />
            <div className={styles.dot} />
          </div>
        )}

        <div ref={bottomRef} />
      </div>
    </div>
  )
}

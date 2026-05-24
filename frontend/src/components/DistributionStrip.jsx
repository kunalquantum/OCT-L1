import { useEffect, useState } from 'react'
import { STANCE_COLOR } from '../constants'
import styles from './DistributionStrip.module.css'

const STANCES = ['PROCEED', 'CAUTION', 'DELAY', 'BLOCK']

export default function DistributionStrip({ verdicts, reliability }) {
  const [counter, setCounter] = useState(0)
  const target = Math.round(reliability * 100)

  useEffect(() => {
    setCounter(0)
    const step = Math.ceil(target / 36)
    const iv = setInterval(() => {
      setCounter(c => {
        const next = Math.min(c + step, target)
        if (next >= target) clearInterval(iv)
        return next
      })
    }, 24)
    return () => clearInterval(iv)
  }, [target])

  const counts = STANCES.reduce((acc, s) => {
    acc[s] = verdicts.filter(v => v.stance === s).length
    return acc
  }, {})

  const hint = reliability >= .75 ? 'High agreement'
    : reliability >= .5 ? 'Moderate agreement'
    : 'Low agreement — scrutinise'

  return (
    <div className={styles.strip}>
      {STANCES.filter(s => counts[s] > 0).map(s => (
        <div key={s} className={styles.dst}>
          <div className={styles.dot} style={{ background: STANCE_COLOR[s] }} />
          <div className={styles.info}>
            <span className={styles.stance} style={{ color: STANCE_COLOR[s] }}>{s}</span>
            <span className={styles.n}>{counts[s]} agent{counts[s] > 1 ? 's' : ''}</span>
          </div>
        </div>
      ))}

      <div className={styles.rel}>
        <span className={styles.relN}>{counter}%</span>
        <span className={styles.relLbl}>Reliability</span>
        <span className={styles.relHint}>{hint}</span>
      </div>
    </div>
  )
}

import styles from './Loader.module.css'

const ARMS = [
  { h: 20, d: 0,    g: 'linear-gradient(#38bdf8,#0ea5e9)' },
  { h: 34, d: .12,  g: 'linear-gradient(#60a5fa,#3b82f6)' },
  { h: 26, d: .24,  g: 'linear-gradient(#818cf8,#6366f1)' },
  { h: 40, d: .36,  g: 'linear-gradient(#a78bfa,#8b5cf6)' },
  { h: 28, d: .48,  g: 'linear-gradient(#818cf8,#6366f1)' },
  { h: 36, d: .60,  g: 'linear-gradient(#60a5fa,#3b82f6)' },
  { h: 22, d: .72,  g: 'linear-gradient(#38bdf8,#0ea5e9)' },
  { h: 32, d: .84,  g: 'linear-gradient(#818cf8,#6366f1)' },
]

export default function Loader() {
  return (
    <div className={styles.wrap}>
      <div className={styles.arms}>
        {ARMS.map((a, i) => (
          <div
            key={i}
            className={styles.arm}
            style={{ height: a.h, animationDelay: `${a.d}s`, background: a.g }}
          />
        ))}
      </div>
      <p className={styles.t}>Agents deliberating…</p>
      <p className={styles.s}>Logic · Risk · Domain · Contradiction · Cost · Compliance</p>
    </div>
  )
}

import styles from './Header.module.css'

export default function Header() {
  return (
    <header className={styles.header}>
      <div className={styles.logo}>
        <svg viewBox="0 0 32 32" fill="none">
          <circle cx="16" cy="13" r="7" fill="white" opacity=".92" />
          <path d="M9 19 Q6 24 8 28"      stroke="white" strokeWidth="1.8" strokeLinecap="round" opacity=".7" />
          <path d="M11.5 21 Q11 27 14 29" stroke="white" strokeWidth="1.8" strokeLinecap="round" opacity=".7" />
          <path d="M16 22 Q16 27 16 30"   stroke="white" strokeWidth="1.8" strokeLinecap="round" opacity=".7" />
          <path d="M20.5 21 Q21 27 18 29" stroke="white" strokeWidth="1.8" strokeLinecap="round" opacity=".7" />
          <path d="M23 19 Q26 24 24 28"   stroke="white" strokeWidth="1.8" strokeLinecap="round" opacity=".7" />
          <circle cx="13.5" cy="12.5" r="1.5" fill="#0ea5e9" />
          <circle cx="18.5" cy="12.5" r="1.5" fill="#818cf8" />
        </svg>
      </div>
      <div>
        <h1 className={styles.title}>CephMind</h1>
        <p className={styles.tagline}>
          Six agents <em>challenge each other in parallel.</em> Their disagreements are
          measured. A consensus <em>emerges with a reliability score</em> — not just an answer.
        </p>
      </div>
    </header>
  )
}

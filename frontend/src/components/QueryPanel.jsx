import { EXAMPLES } from '../constants'
import styles from './QueryPanel.module.css'

export default function QueryPanel({ query, domain, loading, onChange, onDomain, onSubmit }) {
  return (
    <div className={styles.box}>
      <div className={styles.row}>
        <div className={styles.field}>
          <label htmlFor="qi">Decision or question</label>
          <textarea
            id="qi"
            value={query}
            onChange={e => onChange(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) onSubmit() }}
            placeholder="e.g. Should this Oracle ERP migration proceed? UAT incomplete, no rollback plan…"
          />
        </div>
        <div className={styles.side}>
          <div className={styles.field}>
            <label htmlFor="dom">Domain</label>
            <select id="dom" value={domain} onChange={e => onDomain(e.target.value)}>
              <option value="general">General</option>
              <option value="erp">ERP</option>
              <option value="cloud">Cloud</option>
              <option value="finance">Finance</option>
            </select>
          </div>
          <button className={styles.btn} onClick={onSubmit} disabled={loading}>
            {loading ? 'Reasoning…' : 'Analyse →'}
          </button>
        </div>
      </div>

      <div className={styles.chips}>
        <span>Try:</span>
        {Object.entries(EXAMPLES).map(([key, ex]) => (
          <button
            key={key}
            className={styles.chip}
            onClick={() => { onChange(ex.text); onDomain(ex.domain) }}
          >
            {ex.label}
          </button>
        ))}
      </div>
    </div>
  )
}

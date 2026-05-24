import { useState } from 'react'
import Header from './components/Header'
import QueryPanel from './components/QueryPanel'
import Loader from './components/Loader'
import NetworkSVG from './components/NetworkSVG'
import DistributionStrip from './components/DistributionStrip'
import DeliberationSummary from './components/DeliberationSummary'
import AgentCard from './components/AgentCard'
import DecisionPanel from './components/DecisionPanel'
import styles from './App.module.css'

export default function App() {
  const [query, setQuery] = useState('')
  const [domain, setDomain] = useState('general')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)
  const [submittedQuery, setSubmittedQuery] = useState('')

  async function handleSubmit() {
    if (!query.trim()) return
    setLoading(true)
    setError('')
    setResult(null)
    setSubmittedQuery(query.trim())
    try {
      const res = await fetch('/api/reason', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: query.trim(), domain }),
      })
      if (!res.ok) {
        const e = await res.json().catch(() => ({ detail: 'Unknown error' }))
        throw new Error(e.detail || res.statusText)
      }
      setResult(await res.json())
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.page}>
      <Header />

      <QueryPanel
        query={query}
        domain={domain}
        loading={loading}
        onChange={setQuery}
        onDomain={setDomain}
        onSubmit={handleSubmit}
      />

      {error && <div className={styles.error}>{error}</div>}

      {loading && <Loader />}

      {result && (
        <>
          <div className={styles.secHead}><span>Reasoning Network</span></div>
          <div className={styles.netPanel}>
            <div className={styles.svgScroll}>
              <NetworkSVG
                verdicts={result.verdicts}
                consensusStance={result.consensus.overall_stance}
              />
            </div>
            <DistributionStrip
              verdicts={result.verdicts}
              reliability={result.reliability_score}
            />
          </div>

          <div className={styles.secHead}><span>What Was Deliberated</span></div>
          <DeliberationSummary
            verdicts={result.verdicts}
            consensus={result.consensus}
            queryText={submittedQuery}
          />

          <div className={styles.secHead}><span>Agent Deliberation</span></div>
          <div className={styles.grid}>
            {result.verdicts.map((v, i) => (
              <AgentCard
                key={v.agent_name}
                verdict={v}
                index={i}
                consensusStance={result.consensus.overall_stance}
              />
            ))}
          </div>

          <div className={styles.secHead}><span>Emergent Decision</span></div>
          <DecisionPanel
            consensus={result.consensus}
            verdicts={result.verdicts}
            reliability={result.reliability_score}
          />
        </>
      )}
    </div>
  )
}

import { useState } from 'react'
import Header from './components/Header'
import QueryPanel from './components/QueryPanel'
import Loader from './components/Loader'
import NetworkSVG from './components/NetworkSVG'
import LiveFeed from './components/LiveFeed'
import DistributionStrip from './components/DistributionStrip'
import DeliberationSummary from './components/DeliberationSummary'
import AgentCard from './components/AgentCard'
import DecisionPanel from './components/DecisionPanel'
import styles from './App.module.css'

export default function App() {
  const [query, setQuery]               = useState('')
  const [domain, setDomain]             = useState('general')
  const [loading, setLoading]           = useState(false)
  const [error, setError]               = useState('')
  const [result, setResult]             = useState(null)
  const [submittedQuery, setSubmittedQuery] = useState('')

  // streaming state
  const [streamedVerdicts, setStreamedVerdicts] = useState([])
  const [activeAgents, setActiveAgents]         = useState(null)   // null = not streaming
  const [streamDone, setStreamDone]             = useState(false)

  async function handleSubmit() {
    if (!query.trim()) return
    setLoading(true)
    setError('')
    setResult(null)
    setStreamedVerdicts([])
    setActiveAgents(new Set())
    setStreamDone(false)
    setSubmittedQuery(query.trim())

    try {
      const res = await fetch('/api/reason/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: query.trim(), domain }),
      })

      if (!res.ok) {
        const e = await res.json().catch(() => ({ detail: 'Unknown error' }))
        throw new Error(e.detail || res.statusText)
      }

      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      let collectedVerdicts = []

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop()  // keep incomplete line

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          const raw = line.slice(6).trim()
          if (!raw) continue
          let evt
          try { evt = JSON.parse(raw) } catch { continue }

          if (evt.type === 'verdict') {
            collectedVerdicts = [...collectedVerdicts, evt.data]
            setStreamedVerdicts(collectedVerdicts)
            setActiveAgents(prev => new Set([...(prev || []), evt.data.agent_name]))
          } else if (evt.type === 'consensus') {
            const { reliability_score, ...consensus } = evt.data
            setResult({
              verdicts: collectedVerdicts,
              consensus,
              reliability_score,
            })
            setStreamDone(true)
            setActiveAgents(null)
          }
        }
      }
    } catch (e) {
      setError(e.message)
      setActiveAgents(null)
    } finally {
      setLoading(false)
    }
  }

  // During streaming: show live feed + partial network
  const isStreaming = activeAgents !== null
  const allAgentNames = ['Compliance Agent', 'Contradiction Agent', 'Cost Agent',
                         'Domain Expert', 'Logic Agent', 'Risk Agent']

  // Build placeholder verdicts for agents not yet reported (for NetworkSVG skeleton)
  const skeletonVerdicts = isStreaming
    ? allAgentNames.map(name => {
        const live = streamedVerdicts.find(v => v.agent_name === name)
        return live || { agent_name: name, stance: 'CAUTION', confidence: 0, summary: '', findings: [], blockers: [] }
      })
    : null

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

      {loading && !isStreaming && <Loader />}

      {/* ── Live streaming view ───────────────────────────────── */}
      {(isStreaming || (streamedVerdicts.length > 0 && !result)) && (
        <>
          <div className={styles.secHead}><span>Live Reasoning</span></div>
          <div className={styles.liveGrid}>
            <LiveFeed
              verdicts={streamedVerdicts}
              pending={allAgentNames.length - streamedVerdicts.length}
              done={streamDone}
            />
            <div className={styles.netPanel}>
              <div className={styles.svgScroll}>
                <NetworkSVG
                  verdicts={skeletonVerdicts}
                  consensusStance="CAUTION"
                  activeAgents={activeAgents}
                />
              </div>
            </div>
          </div>
        </>
      )}

      {/* ── Final results ─────────────────────────────────────── */}
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

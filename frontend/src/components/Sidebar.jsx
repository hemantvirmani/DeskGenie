import { useState } from 'react'

function Sidebar({ isOpen, tools, config, selectedAgent, onAgentChange }) {
  const [benchmarkStatus, setBenchmarkStatus] = useState(null) // null, 'running', 'completed', 'error'
  const [benchmarkResult, setBenchmarkResult] = useState(null)
  const [showBenchmarkModal, setShowBenchmarkModal] = useState(false)

  const runBenchmark = async () => {
    setBenchmarkStatus('running')
    setBenchmarkResult(null)

    try {
      // Start benchmark
      const response = await fetch('/api/benchmark', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          filter_indices: null, // Run all questions
          agent_type: selectedAgent
        })
      })

      if (!response.ok) throw new Error('Failed to start benchmark')

      const { task_id } = await response.json()

      // Poll for results
      const pollInterval = setInterval(async () => {
        const statusRes = await fetch(`/api/task/${task_id}`)
        const statusData = await statusRes.json()

        if (statusData.status === 'completed') {
          clearInterval(pollInterval)
          setBenchmarkStatus('completed')
          setBenchmarkResult(statusData.result)
          setShowBenchmarkModal(true)
        } else if (statusData.status === 'error') {
          clearInterval(pollInterval)
          setBenchmarkStatus('error')
          setBenchmarkResult(statusData.error)
          setShowBenchmarkModal(true)
        }
      }, 2000)
    } catch (error) {
      setBenchmarkStatus('error')
      setBenchmarkResult(error.message)
      setShowBenchmarkModal(true)
    }
  }
  // Group tools by category
  const toolsByCategory = tools.reduce((acc, tool) => {
    if (!acc[tool.category]) {
      acc[tool.category] = []
    }
    acc[tool.category].push(tool)
    return acc
  }, {})

  const categoryIcons = {
    pdf: (
      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
        <path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zM6 20V4h7v5h5v11H6z"/>
      </svg>
    ),
    image: (
      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
        <path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/>
      </svg>
    ),
    file: (
      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
        <path d="M10 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-8l-2-2z"/>
      </svg>
    ),
    document: (
      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
        <path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/>
      </svg>
    ),
    media: (
      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
        <path d="M18 4l2 4h-3l-2-4h-2l2 4h-3l-2-4H8l2 4H7L5 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V4h-4z"/>
      </svg>
    ),
    chat: (
      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
        <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/>
      </svg>
    ),
  }

  if (!isOpen) {
    return null
  }

  return (
    <aside className="w-64 bg-slate-800 border-r border-slate-700 flex flex-col">
      {/* Agent Selector */}
      <div className="p-4 border-b border-slate-700">
        <label className="block text-sm font-medium text-slate-400 mb-2">
          Agent
        </label>
        <select
          value={selectedAgent || ''}
          onChange={(e) => onAgentChange(e.target.value)}
          className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          {config?.available_agents?.map((agent) => (
            <option key={agent} value={agent}>
              {agent}
            </option>
          ))}
        </select>
      </div>

      {/* Status */}
      <div className="p-4 border-b border-slate-700">
        <h3 className="text-sm font-medium text-slate-400 mb-2">Status</h3>
        <div className="space-y-2 text-sm">
          <div className="flex items-center justify-between">
            <span className="text-slate-300">Ollama</span>
            <span
              className={`px-2 py-0.5 rounded text-xs ${
                config?.ollama_enabled
                  ? 'bg-green-900/50 text-green-400'
                  : 'bg-red-900/50 text-red-400'
              }`}
            >
              {config?.ollama_enabled ? 'Enabled' : 'Disabled'}
            </span>
          </div>
        </div>

        {/* Benchmark Button */}
        <button
          onClick={runBenchmark}
          disabled={benchmarkStatus === 'running'}
          className={`w-full mt-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
            benchmarkStatus === 'running'
              ? 'bg-yellow-900/50 text-yellow-400 cursor-wait'
              : 'bg-primary-600 hover:bg-primary-700 text-white'
          }`}
        >
          {benchmarkStatus === 'running' ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
              </svg>
              Running Benchmark...
            </span>
          ) : (
            'Run GAIA Benchmark'
          )}
        </button>
      </div>

      {/* Benchmark Results Modal */}
      {showBenchmarkModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-slate-800 rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[80vh] flex flex-col">
            <div className="p-4 border-b border-slate-700 flex items-center justify-between">
              <h3 className="text-lg font-medium text-white">
                Benchmark Results
                <span className={`ml-2 px-2 py-0.5 rounded text-xs ${
                  benchmarkStatus === 'completed'
                    ? 'bg-green-900/50 text-green-400'
                    : 'bg-red-900/50 text-red-400'
                }`}>
                  {benchmarkStatus === 'completed' ? 'Completed' : 'Error'}
                </span>
              </h3>
              <button
                onClick={() => setShowBenchmarkModal(false)}
                className="p-1 hover:bg-slate-700 rounded"
              >
                <svg className="w-5 h-5 text-slate-400" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                </svg>
              </button>
            </div>
            <div className="p-4 overflow-y-auto flex-1">
              <pre className="text-sm text-slate-300 whitespace-pre-wrap font-mono bg-slate-900 p-3 rounded">
                {benchmarkResult || 'No results'}
              </pre>
            </div>
          </div>
        </div>
      )}

      {/* Tools List */}
      <div className="flex-1 overflow-y-auto p-4">
        <h3 className="text-sm font-medium text-slate-400 mb-3">Available Tools</h3>
        <div className="space-y-4">
          {Object.entries(toolsByCategory).map(([category, categoryTools]) => (
            <div key={category}>
              <div className="flex items-center gap-2 text-xs font-medium text-slate-500 uppercase mb-2">
                {categoryIcons[category] || null}
                <span>{category}</span>
              </div>
              <ul className="space-y-1">
                {categoryTools.map((tool) => (
                  <li
                    key={tool.name}
                    className="text-sm text-slate-300 hover:text-white hover:bg-slate-700/50 px-2 py-1 rounded cursor-pointer transition-colors"
                    title={tool.description}
                  >
                    {tool.name.replace(/_/g, ' ')}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-slate-700 text-xs text-slate-500">
        <p>DeskGenie v1.0.0</p>
        <p className="mt-1">Model: {config?.ollama_model || 'N/A'}</p>
      </div>
    </aside>
  )
}

export default Sidebar

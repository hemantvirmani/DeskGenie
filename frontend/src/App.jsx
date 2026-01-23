import { useState, useEffect, useRef } from 'react'
import { X, Play, Settings, MessageSquare, ChevronLeft, ChevronRight, ScrollText } from 'lucide-react'
import ChatWindow from './components/ChatWindow'

function App() {
  const [config, setConfig] = useState(null)
  const [selectedAgent, setSelectedAgent] = useState(null)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [showCustomModal, setShowCustomModal] = useState(false)
  const [customIndices, setCustomIndices] = useState('')
  const [showLogsPanel, setShowLogsPanel] = useState(false)
  const [logs, setLogs] = useState([])
  const [isRunningBenchmark, setIsRunningBenchmark] = useState(false)
  const logsEndRef = useRef(null)

  // Auto-scroll logs panel when new logs arrive
  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [logs])

  useEffect(() => {
    // Fetch config on mount
    fetch('/api/config')
      .then(res => res.json())
      .then(data => {
        setConfig(data)
        setSelectedAgent(data.active_agent)
      })
      .catch(err => console.error('Failed to fetch config:', err))
  }, [])

  const addLog = (message, type = 'info') => {
    const timestamp = new Date().toLocaleTimeString()
    setLogs(prev => [...prev, { timestamp, message, type }])
  }

  const runBenchmark = async (filterIndices = null) => {
    setIsRunningBenchmark(true)
    setShowLogsPanel(true)
    setLogs([]) // Clear previous logs
    addLog(`Starting benchmark${filterIndices ? ` with indices: ${filterIndices.join(', ')}` : ' (all 20 questions)'}...`, 'info')

    try {
      const response = await fetch('/api/benchmark', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          filter_indices: filterIndices,
          agent_type: selectedAgent
        })
      })

      if (!response.ok) throw new Error('Failed to start benchmark')

      const { task_id } = await response.json()
      addLog(`Benchmark started (Task ID: ${task_id.slice(0, 8)}...)`, 'info')

      // Connect to SSE stream for real-time logs
      const eventSource = new EventSource(`/api/task/${task_id}/logs/stream`)

      eventSource.onmessage = (event) => {
        try {
          const logEntry = JSON.parse(event.data)

          if (logEntry.error) {
            addLog(logEntry.error, 'error')
            eventSource.close()
            setIsRunningBenchmark(false)
            return
          }

          // Map log levels to display types
          const levelMap = {
            'info': 'info',
            'error': 'error',
            'warning': 'warning',
            'success': 'success',
            'tool': 'tool',
            'step': 'step',
            'result': 'result',
            'debug': 'info'
          }

          const displayType = levelMap[logEntry.level] || 'info'
          addLog(logEntry.message, displayType)
        } catch (e) {
          // Ignore parse errors (might be keepalive)
        }
      }

      eventSource.onerror = () => {
        eventSource.close()
        // Check final task status
        checkTaskStatus(task_id)
      }

      // Also poll for task completion (SSE might close early)
      const checkTaskStatus = async (taskId) => {
        try {
          const statusRes = await fetch(`/api/task/${taskId}`)
          const statusData = await statusRes.json()

          if (statusData.status === 'completed') {
            setIsRunningBenchmark(false)
          } else if (statusData.status === 'error') {
            setIsRunningBenchmark(false)
            addLog(`Error: ${statusData.error}`, 'error')
          } else if (statusData.status === 'running') {
            // Still running, check again later
            setTimeout(() => checkTaskStatus(taskId), 2000)
          }
        } catch (err) {
          setIsRunningBenchmark(false)
        }
      }

    } catch (error) {
      setIsRunningBenchmark(false)
      addLog(`Error: ${error.message}`, 'error')
    }
  }

  const handleRunPresets = () => {
    runBenchmark(null)
  }

  const handleRunCustom = () => {
    setShowCustomModal(true)
  }

  const handleCustomSubmit = () => {
    const indices = customIndices
      .split(',')
      .map(s => parseInt(s.trim(), 10))
      .filter(n => !isNaN(n))

    if (indices.length === 0) {
      addLog('Please enter valid comma-separated indices', 'error')
      return
    }

    setShowCustomModal(false)
    setCustomIndices('')
    runBenchmark(indices)
  }

  return (
    <div className="flex h-screen bg-slate-900 text-white">
      {/* Sidebar - Chat History */}
      <aside className={`${sidebarOpen ? 'w-64' : 'w-0'} bg-slate-800 border-r border-slate-700 flex flex-col transition-all duration-300 overflow-hidden`}>
        <div className="p-4 border-b border-slate-700 flex items-center justify-between">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <MessageSquare className="w-5 h-5" />
            Chat History
          </h2>
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          <p className="text-slate-500 text-sm text-center mt-8">
            Chat history will appear here
          </p>
        </div>

        {/* Agent Selector */}
        <div className="p-4 border-t border-slate-700">
          <label className="block text-sm font-medium text-slate-400 mb-2">
            Agent
          </label>
          <select
            value={selectedAgent || ''}
            onChange={(e) => setSelectedAgent(e.target.value)}
            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {config?.available_agents?.map((agent) => (
              <option key={agent} value={agent}>
                {agent}
              </option>
            ))}
          </select>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-700 text-xs text-slate-500">
          <p>DeskGenie v1.0.0</p>
        </div>
      </aside>

      {/* Sidebar Toggle Button */}
      <button
        onClick={() => setSidebarOpen(!sidebarOpen)}
        className="absolute left-0 top-1/2 -translate-y-1/2 z-10 bg-slate-700 hover:bg-slate-600 p-1 rounded-r-lg transition-all duration-300"
        style={{ left: sidebarOpen ? '256px' : '0px' }}
      >
        {sidebarOpen ? <ChevronLeft className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
      </button>

      {/* Main Content */}
      <div className="flex flex-col flex-1 min-w-0">
        {/* Header */}
        <header className="bg-slate-800 border-b border-slate-700 px-6 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-xl font-bold flex items-center gap-2">
              <span className="text-2xl">🧞‍♂️</span>
              DeskGenie
            </h1>

            <div className="flex items-center gap-3">
              <button
                onClick={handleRunPresets}
                disabled={isRunningBenchmark}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                  isRunningBenchmark
                    ? 'bg-slate-600 text-slate-400 cursor-not-allowed'
                    : 'bg-blue-600 hover:bg-blue-700 text-white'
                }`}
              >
                <Play className="w-4 h-4" />
                Run 20 Presets
              </button>

              <button
                onClick={handleRunCustom}
                disabled={isRunningBenchmark}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                  isRunningBenchmark
                    ? 'bg-slate-600 text-slate-400 cursor-not-allowed'
                    : 'bg-slate-700 hover:bg-slate-600 text-white'
                }`}
              >
                <Settings className="w-4 h-4" />
                Custom Questions
              </button>

              <button
                onClick={() => setShowLogsPanel(!showLogsPanel)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                  showLogsPanel
                    ? 'bg-blue-600 text-white'
                    : 'bg-slate-700 hover:bg-slate-600 text-white'
                }`}
              >
                <ScrollText className="w-4 h-4" />
                Logs
              </button>
            </div>
          </div>
        </header>

        {/* Main Area - Chat + Optional Logs Panel */}
        <main className="flex-1 overflow-hidden flex">
          {/* Chat Window */}
          <div className={`flex-1 ${showLogsPanel ? 'border-r border-slate-700' : ''}`}>
            <ChatWindow
              selectedAgent={selectedAgent}
              addLog={addLog}
              setShowLogsPanel={setShowLogsPanel}
              isRunningBenchmark={isRunningBenchmark}
            />
          </div>

          {/* Logs Panel */}
          {showLogsPanel && (
            <div className="w-96 bg-slate-800 flex flex-col">
              <div className="px-4 py-3 border-b border-slate-700 flex items-center justify-between">
                <h3 className="font-medium text-slate-300">Logs</h3>
                <button
                  onClick={() => setLogs([])}
                  className="text-xs text-slate-500 hover:text-slate-300 transition-colors"
                >
                  Clear
                </button>
              </div>

              <div className="flex-1 overflow-y-auto p-4 font-mono text-sm">
                {logs.length === 0 ? (
                  <p className="text-slate-500 text-center mt-8">
                    Logs will appear here when you chat or run benchmarks
                  </p>
                ) : (
                  <div className="space-y-1">
                    {logs.map((log, index) => (
                      <div
                        key={index}
                        className={`${
                          log.type === 'error'
                            ? 'text-red-400'
                            : log.type === 'warning'
                            ? 'text-yellow-400'
                            : log.type === 'success'
                            ? 'text-green-400'
                            : log.type === 'result'
                            ? 'text-emerald-300'
                            : log.type === 'tool'
                            ? 'text-purple-400'
                            : log.type === 'step'
                            ? 'text-cyan-400'
                            : 'text-blue-400'
                        }`}
                      >
                        <span className="text-slate-500">[{log.timestamp}]</span>{' '}
                        {log.message}
                      </div>
                    ))}
                    <div ref={logsEndRef} />
                  </div>
                )}
              </div>
            </div>
          )}
        </main>
      </div>

      {/* Custom Questions Modal */}
      {showCustomModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-slate-800 rounded-lg shadow-xl max-w-md w-full mx-4">
            <div className="p-4 border-b border-slate-700 flex items-center justify-between">
              <h3 className="text-lg font-medium text-white">
                Custom Question Indices
              </h3>
              <button
                onClick={() => setShowCustomModal(false)}
                className="p-1 hover:bg-slate-700 rounded"
              >
                <X className="w-5 h-5 text-slate-400" />
              </button>
            </div>

            <div className="p-4">
              <label className="block text-sm font-medium text-slate-400 mb-2">
                Enter comma-separated question numbers (1-20)
              </label>
              <input
                type="text"
                value={customIndices}
                onChange={(e) => setCustomIndices(e.target.value)}
                placeholder="e.g., 1, 5, 10, 15"
                className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500 placeholder-slate-500"
                autoFocus
              />
              <p className="text-xs text-slate-500 mt-2">
                Example: "1, 3, 6" will run questions
              </p>
            </div>

            <div className="p-4 border-t border-slate-700 flex justify-end gap-3">
              <button
                onClick={() => setShowCustomModal(false)}
                className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-white transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleCustomSubmit}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-white transition-colors"
              >
                Run
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default App

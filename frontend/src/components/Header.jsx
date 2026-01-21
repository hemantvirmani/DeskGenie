import { useState, useEffect } from 'react'

function Header({ onToggleSidebar, sidebarOpen }) {
  const [status, setStatus] = useState('checking')

  useEffect(() => {
    // Check API health
    fetch('/api/health')
      .then(res => res.json())
      .then(() => setStatus('connected'))
      .catch(() => setStatus('disconnected'))
  }, [])

  return (
    <header className="flex items-center justify-between px-4 py-3 bg-slate-800 border-b border-slate-700">
      <div className="flex items-center gap-3">
        <button
          onClick={onToggleSidebar}
          className="p-2 rounded-lg hover:bg-slate-700 transition-colors"
          aria-label="Toggle sidebar"
        >
          <svg
            className={`w-5 h-5 transition-transform ${sidebarOpen ? '' : 'rotate-180'}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 6h16M4 12h16M4 18h16"
            />
          </svg>
        </button>

        <div className="flex items-center gap-2">
          <svg className="w-8 h-8 text-primary-400" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
          </svg>
          <h1 className="text-xl font-bold text-white">DeskGenie</h1>
        </div>
      </div>

      <div className="flex items-center gap-4">
        {/* Connection Status */}
        <div className="flex items-center gap-2 text-sm">
          <div
            className={`w-2 h-2 rounded-full ${
              status === 'connected'
                ? 'bg-green-400'
                : status === 'disconnected'
                ? 'bg-red-400'
                : 'bg-yellow-400 animate-pulse'
            }`}
          />
          <span className="text-slate-400">
            {status === 'connected'
              ? 'Connected'
              : status === 'disconnected'
              ? 'Disconnected'
              : 'Connecting...'}
          </span>
        </div>
      </div>
    </header>
  )
}

export default Header

import { useState, useEffect } from 'react'
import ChatWindow from './components/ChatWindow'
import Sidebar from './components/Sidebar'
import Header from './components/Header'

function App() {
  const [config, setConfig] = useState(null)
  const [tools, setTools] = useState([])
  const [selectedAgent, setSelectedAgent] = useState(null)
  const [sidebarOpen, setSidebarOpen] = useState(true)

  useEffect(() => {
    // Fetch config on mount
    fetch('/api/config')
      .then(res => res.json())
      .then(data => {
        setConfig(data)
        setSelectedAgent(data.active_agent)
      })
      .catch(err => console.error('Failed to fetch config:', err))

    // Fetch tools
    fetch('/api/tools')
      .then(res => res.json())
      .then(data => setTools(data))
      .catch(err => console.error('Failed to fetch tools:', err))
  }, [])

  return (
    <div className="flex h-screen bg-slate-900 text-white">
      {/* Sidebar */}
      <Sidebar
        isOpen={sidebarOpen}
        tools={tools}
        config={config}
        selectedAgent={selectedAgent}
        onAgentChange={setSelectedAgent}
      />

      {/* Main Content */}
      <div className="flex flex-col flex-1 min-w-0">
        <Header
          onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
          sidebarOpen={sidebarOpen}
        />

        <main className="flex-1 overflow-hidden">
          <ChatWindow
            selectedAgent={selectedAgent}
          />
        </main>
      </div>
    </div>
  )
}

export default App

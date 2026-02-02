import { useState, useEffect, useRef, useCallback } from 'react'
import { ChevronLeft, ChevronRight, ScrollText } from 'lucide-react'
import ChatWindow from './components/ChatWindow'
import ChatGroupList from './components/ChatGroupList'
import { UIStrings } from './uiStrings'
import { Logger } from './consoleStrings'

// Helper functions for chat groups
const generateGroupId = () => {
  return `group_${Date.now()}_${Math.random().toString(36).slice(2, 11)}`
}

const generateGroupName = () => {
  return `Chat - ${new Date().toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  })}`
}

function App() {
  const [config, setConfig] = useState(null)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [showLogsPanel, setShowLogsPanel] = useState(true)
  const [chatGroups, setChatGroups] = useState([])
  const [activeGroupId, setActiveGroupId] = useState(null)
  const [isLoaded, setIsLoaded] = useState(false)
  const logsEndRef = useRef(null)
  const saveTimeoutRef = useRef(null)

  // Get active group's data
  const activeGroup = chatGroups.find(g => g.id === activeGroupId)
  const messages = activeGroup?.messages ?? []
  const logs = activeGroup?.logs ?? []

  // Auto-scroll logs panel when new logs arrive
  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [logs])

  // Load chats from API on mount
  useEffect(() => {
    const loadChats = async () => {
      try {
        const response = await fetch('/api/chats')
        const data = await response.json()

        if (data.chats && data.chats.length > 0) {
          setChatGroups(data.chats)
          setActiveGroupId(data.chats[0].id)
        } else {
          // No saved chats, create a default one
          const newGroup = {
            id: generateGroupId(),
            name: generateGroupName(),
            messages: [],
            logs: [],
            createdAt: Date.now(),
            updatedAt: Date.now()
          }
          setChatGroups([newGroup])
          setActiveGroupId(newGroup.id)
          // Save the new default group
          saveChat(newGroup)
        }
      } catch (err) {
        Logger.error('CHAT_LOAD_FAILED', { error: err.message })
        // Create default group on error
        const newGroup = {
          id: generateGroupId(),
          name: generateGroupName(),
          messages: [],
          logs: [],
          createdAt: Date.now(),
          updatedAt: Date.now()
        }
        setChatGroups([newGroup])
        setActiveGroupId(newGroup.id)
      }
      setIsLoaded(true)
    }

    loadChats()
  }, [])

  // Fetch config on mount
  useEffect(() => {
    fetch('/api/config')
      .then(res => res.json())
      .then(data => setConfig(data))
      .catch(err => Logger.error('CONFIG_FETCH_FAILED', { error: err.message }))
  }, [])

  // Save chat to API
  const saveChat = useCallback(async (chat) => {
    try {
      await fetch('/api/chats', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(chat)
      })
    } catch (err) {
      Logger.error('CHAT_SAVE_FAILED', { error: err.message })
    }
  }, [])

  // Delete chat from API
  const deleteChatFromAPI = useCallback(async (chatId) => {
    try {
      await fetch(`/api/chats/${chatId}`, { method: 'DELETE' })
    } catch (err) {
      Logger.error('CHAT_DELETE_FAILED', { error: err.message })
    }
  }, [])

  // Auto-save active chat when it changes (debounced)
  useEffect(() => {
    if (!isLoaded || !activeGroup) return

    // Clear previous timeout
    if (saveTimeoutRef.current) {
      clearTimeout(saveTimeoutRef.current)
    }

    // Debounce save by 1 second
    saveTimeoutRef.current = setTimeout(() => {
      saveChat(activeGroup)
    }, 1000)

    return () => {
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current)
      }
    }
  }, [activeGroup, isLoaded, saveChat])

  // Chat group management functions
  const createChatGroup = () => {
    const newGroup = {
      id: generateGroupId(),
      name: generateGroupName(),
      messages: [],
      logs: [],
      createdAt: Date.now(),
      updatedAt: Date.now()
    }
    setChatGroups(prev => [newGroup, ...prev])
    setActiveGroupId(newGroup.id)
    saveChat(newGroup)
    return newGroup.id
  }

  const renameChatGroup = (groupId, newName) => {
    setChatGroups(prev => prev.map(group => {
      if (group.id === groupId) {
        const updated = { ...group, name: newName.trim() || group.name, updatedAt: Date.now() }
        saveChat(updated)
        return updated
      }
      return group
    }))
  }

  const deleteChatGroup = (groupId) => {
    // Delete from API
    deleteChatFromAPI(groupId)

    setChatGroups(prev => {
      const filtered = prev.filter(g => g.id !== groupId)

      // If deleting active group, switch to another
      if (groupId === activeGroupId) {
        if (filtered.length > 0) {
          setActiveGroupId(filtered[0].id)
        } else {
          // Create a new default group if none left
          const newGroup = {
            id: generateGroupId(),
            name: generateGroupName(),
            messages: [],
            logs: [],
            createdAt: Date.now(),
            updatedAt: Date.now()
          }
          setActiveGroupId(newGroup.id)
          saveChat(newGroup)
          return [newGroup]
        }
      }
      return filtered
    })
  }

  const switchToGroup = (groupId) => {
    setActiveGroupId(groupId)
  }

  // Message management for active group
  const addMessage = (message) => {
    setChatGroups(prev => prev.map(group =>
      group.id === activeGroupId
        ? {
            ...group,
            messages: [...group.messages, message],
            updatedAt: Date.now()
          }
        : group
    ))
  }

  const updateLastMessage = (updatedMessage) => {
    setChatGroups(prev => prev.map(group =>
      group.id === activeGroupId
        ? {
            ...group,
            messages: [
              ...group.messages.slice(0, -1),
              updatedMessage
            ],
            updatedAt: Date.now()
          }
        : group
    ))
  }

  // Log management for active group
  const addLog = (message, type = 'info') => {
    const timestamp = new Date().toLocaleTimeString()
    setChatGroups(prev => prev.map(group =>
      group.id === activeGroupId
        ? {
            ...group,
            logs: [...group.logs, { timestamp, message, type }]
          }
        : group
    ))
  }

  const clearLogs = () => {
    setChatGroups(prev => prev.map(group =>
      group.id === activeGroupId
        ? { ...group, logs: [], updatedAt: Date.now() }
        : group
    ))
  }

  return (
    <div className="flex h-screen bg-slate-900 text-white">
      {/* Sidebar - Chat Groups */}
      <aside className={`${sidebarOpen ? 'w-64' : 'w-0'} bg-slate-800 border-r border-slate-700 flex flex-col transition-all duration-300 overflow-hidden`}>
        <div className="p-4 border-b border-slate-700 flex items-center justify-between">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            {UIStrings.CHAT_HISTORY_TITLE}
          </h2>
        </div>

        <ChatGroupList
          groups={chatGroups}
          activeGroupId={activeGroupId}
          onSelectGroup={switchToGroup}
          onNewGroup={createChatGroup}
          onRenameGroup={renameChatGroup}
          onDeleteGroup={deleteChatGroup}
        />

        {/* Footer */}
        <div className="p-4 border-t border-slate-700 text-xs text-slate-500">
          <p>{UIStrings.VERSION_INFO}</p>
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
              {UIStrings.APP_TITLE}
            </h1>

            <div className="flex items-center gap-3">
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
              messages={messages}
              addMessage={addMessage}
              updateLastMessage={updateLastMessage}
              addLog={addLog}
              setShowLogsPanel={setShowLogsPanel}
              onNewChat={createChatGroup}
            />
          </div>

          {/* Logs Panel */}
          {showLogsPanel && (
            <div className="w-96 bg-slate-800 flex flex-col">
              <div className="px-4 py-3 border-b border-slate-700 flex items-center justify-between">
                <h3 className="font-medium text-slate-300">{UIStrings.LOGS_TITLE}</h3>
                  <button
                    onClick={clearLogs}
                    className="text-xs text-slate-500 hover:text-slate-300 transition-colors"
                  >
                    {UIStrings.CLEAR_LOGS}
                  </button>
              </div>

              <div className="flex-1 overflow-y-auto p-4 font-mono text-sm">
                {logs.length === 0 ? (
                  <p className="text-slate-500 text-center mt-8">
                    {UIStrings.LOGS_PLACEHOLDER}
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
    </div>
  )
}

export default App

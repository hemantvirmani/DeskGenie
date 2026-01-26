import { useState, useRef, useEffect } from 'react'
import MessageBubble from './MessageBubble'
import ChatInput from './ChatInput'

function ChatWindow({ addLog, setShowLogsPanel, isRunningBenchmark }) {
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async (content) => {
    // Add user message
    const userMessage = { role: 'user', content }
    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)

    // Show logs panel and add initial log
    if (setShowLogsPanel) setShowLogsPanel(true)
    if (addLog) addLog('='.repeat(30), 'info')
    if (addLog) addLog(`Chat: "${content.slice(0, 50)}${content.length > 50 ? '...' : ''}"`, 'info')

    // Add placeholder for assistant response
    const assistantPlaceholder = { role: 'assistant', content: '', status: 'loading' }
    setMessages(prev => [...prev, assistantPlaceholder])

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: content
        })
      })

      if (!response.ok) throw new Error('Failed to send message')

      const { task_id } = await response.json()
      if (addLog) addLog(`Task started (ID: ${task_id.slice(0, 8)}...)`, 'info')

      // Connect to SSE stream for real-time logs
      const eventSource = new EventSource(`/api/task/${task_id}/logs/stream`)

      eventSource.onmessage = (event) => {
        try {
          const logEntry = JSON.parse(event.data)

          if (logEntry.error) {
            if (addLog) addLog(logEntry.error, 'error')
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
          if (addLog) addLog(logEntry.message, displayType)
        } catch (e) {
          // Ignore parse errors (might be keepalive)
        }
      }

      eventSource.onerror = () => {
        eventSource.close()
      }

      // Poll for response (SSE is for logs, polling is for final result)
      const pollInterval = setInterval(async () => {
        try {
          const statusRes = await fetch(`/api/task/${task_id}`)
          const statusData = await statusRes.json()

          if (statusData.status === 'completed') {
            clearInterval(pollInterval)
            eventSource.close()
            setIsLoading(false)
            setMessages(prev => {
              const newMessages = [...prev]
              newMessages[newMessages.length - 1] = {
                role: 'assistant',
                content: statusData.result || 'No response'
              }
              return newMessages
            })
          } else if (statusData.status === 'error') {
            clearInterval(pollInterval)
            eventSource.close()
            setIsLoading(false)
            if (addLog) addLog(`Error: ${statusData.error}`, 'error')
            setMessages(prev => {
              const newMessages = [...prev]
              newMessages[newMessages.length - 1] = {
                role: 'assistant',
                content: `Error: ${statusData.error}`
              }
              return newMessages
            })
          }
        } catch (err) {
          clearInterval(pollInterval)
          eventSource.close()
          setIsLoading(false)
          if (addLog) addLog(`Error: ${err.message}`, 'error')
          setMessages(prev => {
            const newMessages = [...prev]
            newMessages[newMessages.length - 1] = {
              role: 'assistant',
              content: `Error: ${err.message}`
            }
            return newMessages
          })
        }
      }, 1000)
    } catch (error) {
      setIsLoading(false)
      if (addLog) addLog(`Error: ${error.message}`, 'error')
      setMessages(prev => {
        const newMessages = [...prev]
        newMessages[newMessages.length - 1] = {
          role: 'assistant',
          content: `Error: ${error.message}`
        }
        return newMessages
      })
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center text-slate-500">
              <p className="text-lg mb-2">Welcome to DeskGenie!</p>
              <p className="text-sm">Ask a question or give a command to get started.</p>
            </div>
          </div>
        ) : (
          messages.map((message, index) => (
            <MessageBubble key={index} message={message} />
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <ChatInput onSendMessage={handleSendMessage} disabled={isLoading || isRunningBenchmark} />
    </div>
  )
}

export default ChatWindow

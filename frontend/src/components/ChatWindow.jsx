import { useState, useRef, useEffect } from 'react'
import MessageBubble from './MessageBubble'
import ChatInput from './ChatInput'
import { UIStrings } from '../uiStrings'
import { LogStrings, formatLog } from '../logStrings'

function ChatWindow({ messages, addMessage, updateLastMessage, addLog, setShowLogsPanel, onNewChat }) {
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Handle GAIA benchmark runs by creating message bubbles
  const handleRunBenchmark = async (filterQuestions = null) => {
    // Add user message for benchmark
    const benchmarkMessage = filterQuestions
      ? { role: 'user', content: `Running GAIA benchmark with custom questions: ${filterQuestions.join(', ')}` }
      : { role: 'user', content: 'Running GAIA benchmark with all questions' }

    addMessage(benchmarkMessage)
    setIsLoading(true)

    // Show logs panel and add initial log
    if (setShowLogsPanel) setShowLogsPanel(true)
    if (addLog) addLog(LogStrings.LOG_SEPARATOR, 'info')
    if (addLog) {
      const benchmarkLog = filterQuestions
        ? formatLog(LogStrings.STARTING_BENCHMARK_CUSTOM, { questions: filterQuestions.join(', ') })
        : LogStrings.STARTING_BENCHMARK_ALL
      addLog(benchmarkLog, 'question')
    }

    // Add placeholder for benchmark result
    const benchmarkPlaceholder = { role: 'assistant', content: LogStrings.RUNNING_BENCHMARK, status: 'loading' }
    addMessage(benchmarkPlaceholder)

    try {
      const response = await fetch('/api/benchmark', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          filter_indices: filterQuestions ? filterQuestions.map(n => n - 1) : null
        })
      })

      if (!response.ok) throw new Error('Failed to start benchmark')

      const { task_id } = await response.json()
      if (addLog) addLog(formatLog(LogStrings.TASK_STARTED, { taskId: task_id.slice(0, 8) }), 'info')

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
            'question': 'question',
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
            updateLastMessage({
              role: 'assistant',
              content: statusData.result || LogStrings.BENCHMARK_COMPLETED
            })
          } else if (statusData.status === 'error') {
            clearInterval(pollInterval)
            eventSource.close()
            setIsLoading(false)
            if (addLog) addLog(formatLog(LogStrings.ERROR_PREFIX, { error: statusData.error }), 'error')
            updateLastMessage({
              role: 'assistant',
              content: formatLog(LogStrings.BENCHMARK_FAILED, { error: statusData.error })
            })
          }
        } catch (err) {
          clearInterval(pollInterval)
          eventSource.close()
          setIsLoading(false)
          if (addLog) addLog(formatLog(LogStrings.ERROR_PREFIX, { error: err.message }), 'error')
          updateLastMessage({
            role: 'assistant',
            content: formatLog(LogStrings.BENCHMARK_ERROR, { error: err.message })
          })
        }
      }, 1000)
    } catch (error) {
      setIsLoading(false)
      if (addLog) addLog(formatLog(LogStrings.ERROR_PREFIX, { error: error.message }), 'error')
      updateLastMessage({
        role: 'assistant',
        content: formatLog(LogStrings.BENCHMARK_ERROR, { error: error.message })
      })
    }
  }

  const handleSendMessage = async (content) => {
    const trimmed = content.trim()

    // Check for /new command (exact match, case-insensitive)
    if (trimmed.toLowerCase() === '/new') {
      if (onNewChat) onNewChat()
      return
    }

    // Easter egg: /gaia [optional comma-separated indices]
    if (trimmed.toLowerCase().startsWith('/gaia')) {
      const rest = trimmed.slice(5).trim()
      if (rest === '' || rest.toLowerCase() === 'all') {
        handleRunBenchmark(null)
      } else {
        const indices = rest.split(',')
          .map(s => parseInt(s.trim(), 10))
          .filter(n => !isNaN(n) && n > 0)
        if (indices.length === 0) {
          if (addLog) addLog(LogStrings.ERROR_INVALID_INDICES, 'error')
        } else {
          handleRunBenchmark(indices)
        }
      }
      return
    }

    // Add user message
    const userMessage = { role: 'user', content }
    addMessage(userMessage)
    setIsLoading(true)

    // Show logs panel and add initial log
    if (setShowLogsPanel) setShowLogsPanel(true)
    if (addLog) addLog(LogStrings.LOG_SEPARATOR, 'info')
    const preview = content.slice(0, 50) + (content.length > 50 ? '...' : '')
    if (addLog) addLog(formatLog(LogStrings.CHAT_PREFIX, { preview }), 'question')

    // Add placeholder for assistant response
    const assistantPlaceholder = { role: 'assistant', content: '', status: 'loading' }
    addMessage(assistantPlaceholder)

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
      if (addLog) addLog(formatLog(LogStrings.TASK_STARTED, { taskId: task_id.slice(0, 8) }), 'info')

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
            'question': 'question',
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
            updateLastMessage({
              role: 'assistant',
              content: statusData.result || LogStrings.NO_RESPONSE
            })
          } else if (statusData.status === 'error') {
            clearInterval(pollInterval)
            eventSource.close()
            setIsLoading(false)
            if (addLog) addLog(formatLog(LogStrings.ERROR_PREFIX, { error: statusData.error }), 'error')
            updateLastMessage({
              role: 'assistant',
              content: formatLog(LogStrings.ERROR_PREFIX, { error: statusData.error })
            })
          }
        } catch (err) {
          clearInterval(pollInterval)
          eventSource.close()
          setIsLoading(false)
          if (addLog) addLog(formatLog(LogStrings.ERROR_PREFIX, { error: err.message }), 'error')
          updateLastMessage({
            role: 'assistant',
            content: formatLog(LogStrings.ERROR_PREFIX, { error: err.message })
          })
        }
      }, 1000)
    } catch (error) {
      setIsLoading(false)
      if (addLog) addLog(formatLog(LogStrings.ERROR_PREFIX, { error: error.message }), 'error')
      updateLastMessage({
        role: 'assistant',
        content: formatLog(LogStrings.ERROR_PREFIX, { error: error.message })
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
              <p className="text-lg mb-2">{UIStrings.WELCOME_TITLE}</p>
              <p className="text-sm">{UIStrings.WELCOME_SUBTITLE}</p>
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
      <ChatInput
        onSendMessage={handleSendMessage}
        disabled={isLoading}
      />
    </div>
  )
}

export default ChatWindow

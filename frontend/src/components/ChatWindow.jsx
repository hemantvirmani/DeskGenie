import { useState, useRef, useEffect } from 'react'
import { X } from 'lucide-react'
import MessageBubble from './MessageBubble'
import ChatInput from './ChatInput'
import { UIStrings } from '../uiStrings'
import { LogStrings, formatLog } from '../logStrings'

function ChatWindow({ messages, addMessage, updateLastMessage, addLog, setShowLogsPanel, onNewChat }) {
  const [isLoading, setIsLoading] = useState(false)
  const [showCustomModal, setShowCustomModal] = useState(false)
  const [customQuestions, setCustomQuestions] = useState('')
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
    // Check for /new command first (exact match, case-insensitive)
    if (content.trim().toLowerCase() === '/new') {
      if (onNewChat) onNewChat()
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

  const handleCustomSubmit = () => {
    const questions = customQuestions
      .split(',')
      .map(s => parseInt(s.trim(), 10))
      .filter(n => !isNaN(n))

    if (questions.length === 0) {
      if (addLog) addLog(LogStrings.ERROR_INVALID_INDICES, 'error')
      return
    }

    setShowCustomModal(false)
    setCustomQuestions('')
    handleRunBenchmark(questions)
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
        onRunPresets={() => handleRunBenchmark(null)}
        onRunCustom={() => setShowCustomModal(true)}
      />

      {/* Custom Questions Modal */}
      {showCustomModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-slate-800 rounded-lg shadow-xl max-w-md w-full mx-4">
            <div className="p-4 border-b border-slate-700 flex items-center justify-between">
              <h3 className="text-lg font-medium text-white">
                {UIStrings.CUSTOM_QUESTIONS_TITLE}
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
                {UIStrings.CUSTOM_QUESTIONS_LABEL}
              </label>
              <input
                type="text"
                value={customQuestions}
                onChange={(e) => setCustomQuestions(e.target.value)}
                placeholder={UIStrings.CUSTOM_QUESTIONS_PLACEHOLDER}
                className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500 placeholder-slate-500"
                autoFocus
              />
              <p className="text-xs text-slate-500 mt-2">
                {UIStrings.CUSTOM_QUESTIONS_EXAMPLE}
              </p>
            </div>

            <div className="p-4 border-t border-slate-700 flex justify-end gap-3">
              <button
                onClick={() => setShowCustomModal(false)}
                className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-white transition-colors"
              >
                {UIStrings.CANCEL_BUTTON}
              </button>
              <button
                onClick={handleCustomSubmit}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-white transition-colors"
              >
                {UIStrings.RUN_BUTTON}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ChatWindow

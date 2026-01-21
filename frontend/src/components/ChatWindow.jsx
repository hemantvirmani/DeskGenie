import { useState, useRef, useEffect } from 'react'
import MessageBubble from './MessageBubble'
import ChatInput from './ChatInput'

function ChatWindow({ selectedAgent }) {
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: 'assistant',
      content: 'Hello! I\'m DeskGenie, your desktop AI assistant. I can help you with:\n\n- PDF operations (merge, split, extract pages)\n- Image processing (convert, resize, compress)\n- File management (rename, organize, find duplicates)\n- Document tasks (Word to PDF, OCR)\n- Media processing (video to audio, compress)\n- Chat with Ollama LLM\n\nWhat would you like to do?',
      timestamp: new Date(),
    },
  ])
  const [isLoading, setIsLoading] = useState(false)
  const [currentTaskId, setCurrentTaskId] = useState(null)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Poll for task status
  useEffect(() => {
    if (!currentTaskId) return

    const pollInterval = setInterval(async () => {
      try {
        const res = await fetch(`/api/task/${currentTaskId}`)
        const data = await res.json()

        if (data.status === 'completed') {
          setMessages((prev) => [
            ...prev,
            {
              id: Date.now(),
              role: 'assistant',
              content: data.result || 'Task completed.',
              timestamp: new Date(),
            },
          ])
          setIsLoading(false)
          setCurrentTaskId(null)
        } else if (data.status === 'error') {
          setMessages((prev) => [
            ...prev,
            {
              id: Date.now(),
              role: 'assistant',
              content: `Error: ${data.error}`,
              timestamp: new Date(),
              isError: true,
            },
          ])
          setIsLoading(false)
          setCurrentTaskId(null)
        }
      } catch (err) {
        console.error('Failed to poll task status:', err)
      }
    }, 1000)

    return () => clearInterval(pollInterval)
  }, [currentTaskId])

  const handleSendMessage = async (content, file) => {
    // Add user message
    const userMessage = {
      id: Date.now(),
      role: 'user',
      content,
      file: file?.name,
      timestamp: new Date(),
    }
    setMessages((prev) => [...prev, userMessage])
    setIsLoading(true)

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: content,
          file_name: file?.name,
          agent_type: selectedAgent,
        }),
      })

      const data = await res.json()
      setCurrentTaskId(data.task_id)
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now(),
          role: 'assistant',
          content: `Failed to send message: ${err.message}`,
          timestamp: new Date(),
          isError: true,
        },
      ])
      setIsLoading(false)
    }
  }

  const handleClearChat = () => {
    setMessages([
      {
        id: Date.now(),
        role: 'assistant',
        content: 'Chat cleared. How can I help you?',
        timestamp: new Date(),
      },
    ])
  }

  return (
    <div className="flex flex-col h-full">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}

        {/* Loading Indicator */}
        {isLoading && (
          <div className="flex items-center gap-2 text-slate-400">
            <div className="flex gap-1">
              <div className="w-2 h-2 bg-primary-400 rounded-full typing-dot" />
              <div className="w-2 h-2 bg-primary-400 rounded-full typing-dot" />
              <div className="w-2 h-2 bg-primary-400 rounded-full typing-dot" />
            </div>
            <span className="text-sm">Processing...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <ChatInput
        onSendMessage={handleSendMessage}
        onClearChat={handleClearChat}
        disabled={isLoading}
      />
    </div>
  )
}

export default ChatWindow

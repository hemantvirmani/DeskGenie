import { useState, useRef, useEffect } from 'react'
import MessageBubble from './MessageBubble'
import ChatInput from './ChatInput'

function ChatWindow({ selectedAgent }) {
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

    // Add placeholder for assistant response
    const assistantPlaceholder = { role: 'assistant', content: '', status: 'loading' }
    setMessages(prev => [...prev, assistantPlaceholder])

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: content,
          agent_type: selectedAgent
        })
      })

      if (!response.ok) throw new Error('Failed to send message')

      const { task_id } = await response.json()

      // Poll for response
      const pollInterval = setInterval(async () => {
        try {
          const statusRes = await fetch(`/api/task/${task_id}`)
          const statusData = await statusRes.json()

          if (statusData.status === 'completed') {
            clearInterval(pollInterval)
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
            setIsLoading(false)
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
          setIsLoading(false)
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
      <ChatInput onSendMessage={handleSendMessage} disabled={isLoading} />
    </div>
  )
}

export default ChatWindow

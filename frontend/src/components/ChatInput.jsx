import { useState } from 'react'
import { Send, CirclePlay, CirclePlus } from 'lucide-react'
import { UIStrings } from '../uiStrings'

function ChatInput({ onSendMessage, disabled, onRunPresets, onRunCustom }) {
  const [message, setMessage] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (message.trim() && !disabled) {
      onSendMessage(message.trim())
      setMessage('')
    }
  }

  return (
    <form onSubmit={handleSubmit} className="p-4 border-t border-slate-700">
      <div className="flex gap-2 items-center">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder={UIStrings.INPUT_PLACEHOLDER}
          disabled={disabled}
          className="flex-1 min-w-0 px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        />
        <button
          type="submit"
          disabled={disabled || !message.trim()}
          className="px-3 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 disabled:cursor-not-allowed rounded-lg text-white transition-colors"
        >
          <Send className="w-5 h-5" />
        </button>

        <div className="border-l border-slate-600 h-8 mx-1" />

        <button
          type="button"
          onClick={onRunPresets}
          disabled={disabled}
          className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
            disabled
              ? 'bg-slate-600 text-slate-400 cursor-not-allowed'
              : 'bg-slate-700 hover:bg-slate-600 text-white'
          }`}
        >
          <CirclePlay className="w-4 h-4" />
          {UIStrings.GAIA_PRESETS_BUTTON}
        </button>

        <button
          type="button"
          onClick={onRunCustom}
          disabled={disabled}
          className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
            disabled
              ? 'bg-slate-600 text-slate-400 cursor-not-allowed'
              : 'bg-slate-700 hover:bg-slate-600 text-white'
          }`}
        >
          <CirclePlus className="w-4 h-4" />
          {UIStrings.CUSTOM_GAIA_BUTTON}
        </button>
      </div>
    </form>
  )
}

export default ChatInput

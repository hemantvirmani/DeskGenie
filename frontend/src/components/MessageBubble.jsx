import { UIStrings } from '../uiStrings'

function MessageBubble({ message }) {
  const isUser = message.role === 'user'

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[80%] px-4 py-3 rounded-lg ${
          isUser
            ? 'bg-blue-600 text-white'
            : 'bg-slate-700 text-slate-200'
        }`}
      >
        <p className="whitespace-pre-wrap">{message.content}</p>
        {message.status === 'loading' && (
          <div className="flex items-center gap-2 mt-2 text-slate-400">
            <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
            </svg>
            <span className="text-sm">{UIStrings.PROCESSING_TEXT}</span>
          </div>
        )}
        {message.status === 'interrupted' && (
          <div className="flex items-center gap-2 mt-2 text-amber-400">
            <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v4m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
            </svg>
            <span className="text-sm">{UIStrings.INTERRUPTED_TEXT}</span>
          </div>
        )}
      </div>
    </div>
  )
}

export default MessageBubble

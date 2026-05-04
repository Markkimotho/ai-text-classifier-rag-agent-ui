export default function MessageBubble({ message }) {
  const isUser = message.role === 'user'
  const hasSources = message.meta?.sources?.length > 0
  const hasTrace = message.meta?.tool_trace?.length > 0

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-3`}>
      <div className={`max-w-[80%] ${isUser ? 'order-2' : 'order-1'}`}>
        <div
          className={`rounded-2xl px-4 py-2.5 text-sm leading-relaxed whitespace-pre-wrap break-words ${
            isUser
              ? 'bg-blue-600 text-white rounded-br-sm'
              : 'bg-white text-gray-800 rounded-bl-sm shadow-sm border border-gray-100'
          }`}
        >
          {message.text}
          {!isUser && !message.text && (
            <span className="inline-flex gap-1">
              <span className="animate-bounce">.</span>
              <span className="animate-bounce [animation-delay:150ms]">.</span>
              <span className="animate-bounce [animation-delay:300ms]">.</span>
            </span>
          )}
        </div>

        {hasTrace && (
          <div className="mt-1 flex flex-wrap gap-1">
            {message.meta.tool_trace.map((tool, i) => (
              <span key={i} className="text-xs bg-purple-100 text-purple-700 rounded-full px-2 py-0.5">
                {tool}
              </span>
            ))}
          </div>
        )}

        {hasSources && (
          <details className="mt-1">
            <summary className="text-xs text-gray-400 cursor-pointer hover:text-gray-600">
              {message.meta.sources.length} source{message.meta.sources.length > 1 ? 's' : ''}
            </summary>
            <div className="mt-1 space-y-1">
              {message.meta.sources.map((src, i) => (
                <p key={i} className="text-xs text-gray-500 bg-gray-50 rounded p-2 border border-gray-100 line-clamp-3">
                  {src}
                </p>
              ))}
            </div>
          </details>
        )}
      </div>
    </div>
  )
}

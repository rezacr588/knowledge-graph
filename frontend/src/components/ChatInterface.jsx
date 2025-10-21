import { useState, useRef, useEffect } from 'react'
import { MessageSquare, Send, Loader2, FileText, ChevronDown, ChevronUp } from 'lucide-react'
import axios from 'axios'

function ChatInterface() {
  const languageOptions = [
    { value: 'en', label: 'English' },
    { value: 'ar', label: 'Arabic (العربية)' },
    { value: 'es', label: 'Spanish (Español)' }
  ]

  const placeholders = {
    en: 'Ask a question about your documents...',
    ar: 'اطرح سؤالاً حول مستنداتك...',
    es: 'Haz una pregunta sobre tus documentos...'
  }

  const sendLabels = {
    en: 'Send',
    ar: 'إرسال',
    es: 'Enviar'
  }

  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [expandedContexts, setExpandedContexts] = useState({})
  const [language, setLanguage] = useState('en')
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const toggleContext = (messageIndex) => {
    setExpandedContexts(prev => ({
      ...prev,
      [messageIndex]: !prev[messageIndex]
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMessage = input.trim()
    setInput('')
    
    // Add user message to chat
    const newUserMessage = {
      role: 'user',
      content: userMessage,
      language,
      timestamp: new Date().toISOString()
    }
    setMessages(prev => [...prev, newUserMessage])
    setLoading(true)

    try {
      // Prepare conversation history (last 5 messages for context)
      const conversationHistory = messages.slice(-10).map(msg => ({
        role: msg.role,
        content: msg.content
      }))

      // Send chat request
      const response = await axios.post('/api/chat', {
        message: userMessage,
        conversation_history: conversationHistory,
        top_k: 5,
        language,
        retrieval_methods: ['bm25', 'colbert', 'graph']
      })

      // Add assistant response to chat
      const assistantMessage = {
        role: 'assistant',
        content: response.data.message,
        language,
        timestamp: new Date().toISOString(),
        context: response.data.retrieved_chunks,
        retrieval_time: response.data.retrieval_time_ms,
        generation_time: response.data.generation_time_ms
      }
      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Chat error:', error)
      const errorMessage = {
        role: 'assistant',
        content: error.response?.data?.detail || 'Sorry, I encountered an error. Please try again.',
        language: 'en',
        timestamp: new Date().toISOString(),
        isError: true
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
      inputRef.current?.focus()
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-lg h-[calc(100vh-12rem)] flex flex-col">
      {/* Chat Header */}
      <div className="p-4 border-b bg-gradient-to-r from-blue-50 to-purple-50">
        <div className="flex items-center space-x-2">
          <MessageSquare className="h-5 w-5 text-blue-600" />
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Chat with Documents</h2>
            <p className="text-sm text-gray-600">Ask questions about your uploaded documents</p>
          </div>
          <div className="ml-auto flex items-center space-x-2">
            <label htmlFor="chat-language" className="text-sm text-gray-700">
              Language
            </label>
            <select
              id="chat-language"
              value={language}
              onChange={(event) => setLanguage(event.target.value)}
              className="px-3 py-1 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={loading}
            >
              {languageOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="h-full flex items-center justify-center text-center">
            <div className="max-w-md">
              <MessageSquare className="h-12 w-12 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Start a conversation
              </h3>
              <p className="text-gray-600">
                Ask questions about your documents. I'll search through them and provide answers based on the content.
              </p>
            </div>
          </div>
        ) : (
          messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-lg p-4 ${
                  message.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : message.isError
                    ? 'bg-red-50 border border-red-200 text-red-900'
                    : 'bg-gray-100 text-gray-900'
                }`}
              >
                <div
                  className="whitespace-pre-wrap break-words"
                  style={{
                    direction: message.language === 'ar' ? 'rtl' : 'ltr',
                    textAlign: message.language === 'ar' ? 'right' : 'left'
                  }}
                >
                  {message.content}
                </div>
                
                {/* Show context sources for assistant messages */}
                {message.role === 'assistant' && message.context && message.context.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-300">
                    <button
                      onClick={() => toggleContext(index)}
                      className="flex items-center space-x-2 text-sm text-gray-700 hover:text-gray-900"
                    >
                      <FileText className="h-4 w-4" />
                      <span>Sources ({message.context.length})</span>
                      {expandedContexts[index] ? (
                        <ChevronUp className="h-4 w-4" />
                      ) : (
                        <ChevronDown className="h-4 w-4" />
                      )}
                    </button>
                    
                    {expandedContexts[index] && (
                      <div className="mt-2 space-y-2">
                        {message.context.slice(0, 3).map((chunk, chunkIndex) => (
                          <div
                            key={chunkIndex}
                            className="text-xs p-2 bg-white rounded border border-gray-200"
                          >
                            <div className="font-medium text-gray-700 mb-1">
                              Score: {chunk.rrf_score.toFixed(3)}
                            </div>
                            <div className="text-gray-600 line-clamp-2">
                              {chunk.text}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                    
                    {/* Timing info */}
                    {message.retrieval_time !== undefined && (
                      <div className="mt-2 text-xs text-gray-600">
                        Retrieval: {message.retrieval_time.toFixed(0)}ms | 
                        Generation: {message.generation_time.toFixed(0)}ms
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))
        )}
        
        {/* Loading indicator */}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg p-4">
              <Loader2 className="h-5 w-5 text-blue-600 animate-spin" />
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 border-t bg-gray-50">
        <form onSubmit={handleSubmit} className="flex space-x-2">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={placeholders[language] || placeholders.en}
            disabled={loading}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
          >
            {loading ? (
              <Loader2 className="h-5 w-5 animate-spin" />
            ) : (
              <>
                <Send className="h-5 w-5" />
                <span>{sendLabels[language] || sendLabels.en}</span>
              </>
            )}
          </button>
        </form>
        <p className="text-xs text-gray-500 mt-2">
          Press Enter to send. Responses are generated based on your uploaded documents.
        </p>
      </div>
    </div>
  )
}

export default ChatInterface

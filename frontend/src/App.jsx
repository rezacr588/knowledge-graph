import { useState, useEffect } from 'react'
import { Upload, Search, Activity, Database, Zap, Network, MessageSquare, BookOpen, GitBranch } from 'lucide-react'
import DocumentUpload from './components/DocumentUpload'
import QueryInterface from './components/QueryInterface'
import ResultsDisplay from './components/ResultsDisplay'
import HealthStatus from './components/HealthStatus'
import ChatInterface from './components/ChatInterface'
import GraphVisualization from './components/GraphVisualization'
import Documentation from './components/Documentation'
import StoredChunks from './components/StoredChunks'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('query')
  const [results, setResults] = useState(null)
  const [health, setHealth] = useState(null)

  useEffect(() => {
    checkHealth()
    const interval = setInterval(checkHealth, 30000)
    return () => clearInterval(interval)
  }, [])

  const checkHealth = async () => {
    try {
      const response = await fetch('/api/health')
      const data = await response.json()
      setHealth(data)
    } catch (error) {
      console.error('Health check failed:', error)
      setHealth({ status: 'unhealthy' })
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg">
                <Network className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  Hybrid RAG System
                </h1>
                <p className="text-sm text-gray-500">
                  BM25 + ColBERT + Knowledge Graph
                </p>
              </div>
            </div>
            <HealthStatus health={health} />
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8">
            <button
              onClick={() => setActiveTab('query')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'query'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center space-x-2">
                <Search className="h-4 w-4" />
                <span>Query</span>
              </div>
            </button>
            <button
              onClick={() => setActiveTab('upload')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'upload'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center space-x-2">
                <Upload className="h-4 w-4" />
                <span>Upload</span>
              </div>
            </button>
            <button
              onClick={() => setActiveTab('chat')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'chat'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center space-x-2">
                <MessageSquare className="h-4 w-4" />
                <span>Chat</span>
              </div>
            </button>
            <button
              onClick={() => setActiveTab('graph')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'graph'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center space-x-2">
                <GitBranch className="h-4 w-4" />
                <span>Graph</span>
              </div>
            </button>
            <button
              onClick={() => setActiveTab('chunks')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'chunks'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center space-x-2">
                <Database className="h-4 w-4" />
                <span>Chunks</span>
              </div>
            </button>
            <button
              onClick={() => setActiveTab('docs')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'docs'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center space-x-2">
                <BookOpen className="h-4 w-4" />
                <span>Docs</span>
              </div>
            </button>
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'query' ? (
          <div className="space-y-6">
            <QueryInterface onResults={setResults} />
            {results && <ResultsDisplay results={results} />}
          </div>
        ) : activeTab === 'upload' ? (
          <DocumentUpload />
        ) : activeTab === 'chat' ? (
          <ChatInterface />
        ) : activeTab === 'graph' ? (
          <GraphVisualization />
        ) : activeTab === 'chunks' ? (
          <StoredChunks />
        ) : (
          <Documentation />
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between text-sm text-gray-500">
            <div className="flex items-center space-x-6">
              <div className="flex items-center space-x-2">
                <Database className="h-4 w-4" />
                <span>Multilingual: EN, AR, ES</span>
              </div>
              <div className="flex items-center space-x-2">
                <Zap className="h-4 w-4" />
                <span>~360ms latency</span>
              </div>
              <div className="flex items-center space-x-2">
                <Activity className="h-4 w-4" />
                <span>Production-ready</span>
              </div>
            </div>
            <div>
              <a
                href="http://localhost:8000/docs"
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-800"
              >
                API Documentation →
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App

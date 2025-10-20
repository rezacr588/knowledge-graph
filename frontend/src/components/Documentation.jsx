import { BookOpen, Upload, Search, MessageSquare, Network, Zap, Database, GitBranch, Brain, FileText, Users, Link as LinkIcon } from 'lucide-react'

function Documentation() {
  return (
    <div className="max-w-5xl mx-auto space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg shadow-lg p-8 text-white">
        <div className="flex items-center space-x-3 mb-4">
          <BookOpen className="h-8 w-8" />
          <h1 className="text-3xl font-bold">How It Works</h1>
        </div>
        <p className="text-lg text-blue-100">
          A comprehensive guide to understanding the Hybrid RAG System's architecture and features.
        </p>
      </div>

      {/* Overview */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">System Overview</h2>
        <p className="text-gray-700 mb-4">
          The Hybrid RAG (Retrieval-Augmented Generation) System combines multiple search techniques 
          to provide accurate, context-aware answers from your documents. It uses three complementary 
          retrieval methods and a knowledge graph to understand relationships between concepts.
        </p>
        <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
          <p className="text-sm text-blue-900">
            <strong>Key Innovation:</strong> By combining BM25 (keyword search), Dense Retrieval (semantic search), 
            and Knowledge Graph traversal, the system achieves better results than any single method alone.
          </p>
        </div>
      </div>

      {/* Architecture */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center space-x-2">
          <GitBranch className="h-6 w-6 text-purple-600" />
          <span>System Architecture</span>
        </h2>
        
        <div className="space-y-6">
          {/* Retrieval Methods */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Retrieval Methods</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <Search className="h-5 w-5 text-blue-600" />
                  <h4 className="font-semibold text-blue-900">BM25</h4>
                </div>
                <p className="text-sm text-blue-800">
                  Traditional keyword-based search. Excellent at finding exact matches and technical terms.
                </p>
              </div>
              
              <div className="bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <Brain className="h-5 w-5 text-purple-600" />
                  <h4 className="font-semibold text-purple-900">Dense Retrieval</h4>
                </div>
                <p className="text-sm text-purple-800">
                  Semantic search using embeddings. Understands meaning and context beyond exact words.
                </p>
              </div>
              
              <div className="bg-gradient-to-br from-green-50 to-green-100 border border-green-200 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <Network className="h-5 w-5 text-green-600" />
                  <h4 className="font-semibold text-green-900">Knowledge Graph</h4>
                </div>
                <p className="text-sm text-green-800">
                  Relationship-based retrieval. Finds connected information through entities and links.
                </p>
              </div>
            </div>
          </div>

          {/* Fusion */}
          <div className="bg-gradient-to-r from-orange-50 to-yellow-50 border border-orange-200 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <Zap className="h-5 w-5 text-orange-600" />
              <h4 className="font-semibold text-orange-900">Reciprocal Rank Fusion (RRF)</h4>
            </div>
            <p className="text-sm text-orange-800">
              Combines results from all three methods using a sophisticated ranking algorithm. 
              Results that appear highly ranked in multiple methods get boosted scores.
            </p>
          </div>
        </div>
      </div>

      {/* How to Use */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">How to Use</h2>
        
        <div className="space-y-6">
          {/* Step 1: Upload */}
          <div className="flex space-x-4">
            <div className="flex-shrink-0">
              <div className="w-10 h-10 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
                1
              </div>
            </div>
            <div className="flex-1">
              <div className="flex items-center space-x-2 mb-2">
                <Upload className="h-5 w-5 text-blue-600" />
                <h3 className="text-lg font-semibold text-gray-900">Upload Documents</h3>
              </div>
              <p className="text-gray-700 mb-2">
                Navigate to the <strong>Upload</strong> tab and upload your documents (PDF, TXT, DOCX, etc.).
              </p>
              <ul className="list-disc list-inside text-sm text-gray-600 space-y-1 ml-4">
                <li>Documents are automatically chunked into semantic sections</li>
                <li>Entities (people, places, concepts) are extracted using NLP</li>
                <li>Relationships between entities are identified and stored</li>
                <li>Multiple search indexes are built in parallel</li>
              </ul>
            </div>
          </div>

          {/* Step 2: Query */}
          <div className="flex space-x-4">
            <div className="flex-shrink-0">
              <div className="w-10 h-10 bg-purple-600 text-white rounded-full flex items-center justify-center font-bold">
                2
              </div>
            </div>
            <div className="flex-1">
              <div className="flex items-center space-x-2 mb-2">
                <Search className="h-5 w-5 text-purple-600" />
                <h3 className="text-lg font-semibold text-gray-900">Search & Query</h3>
              </div>
              <p className="text-gray-700 mb-2">
                Use the <strong>Query</strong> tab to search across your documents using hybrid retrieval.
              </p>
              <ul className="list-disc list-inside text-sm text-gray-600 space-y-1 ml-4">
                <li>All three retrieval methods run in parallel</li>
                <li>Results are fused and ranked by relevance</li>
                <li>See which methods contributed to each result</li>
                <li>View relevance scores and rankings</li>
              </ul>
            </div>
          </div>

          {/* Step 3: Chat */}
          <div className="flex space-x-4">
            <div className="flex-shrink-0">
              <div className="w-10 h-10 bg-green-600 text-white rounded-full flex items-center justify-center font-bold">
                3
              </div>
            </div>
            <div className="flex-1">
              <div className="flex items-center space-x-2 mb-2">
                <MessageSquare className="h-5 w-5 text-green-600" />
                <h3 className="text-lg font-semibold text-gray-900">Chat with Documents</h3>
              </div>
              <p className="text-gray-700 mb-2">
                The <strong>Chat</strong> tab provides a conversational interface powered by Gemini AI.
              </p>
              <ul className="list-disc list-inside text-sm text-gray-600 space-y-1 ml-4">
                <li>Ask natural language questions about your documents</li>
                <li>AI retrieves relevant context using hybrid search</li>
                <li>Responses are generated based on actual document content</li>
                <li>View source citations for each answer</li>
              </ul>
            </div>
          </div>

          {/* Step 4: Visualize */}
          <div className="flex space-x-4">
            <div className="flex-shrink-0">
              <div className="w-10 h-10 bg-orange-600 text-white rounded-full flex items-center justify-center font-bold">
                4
              </div>
            </div>
            <div className="flex-1">
              <div className="flex items-center space-x-2 mb-2">
                <Network className="h-5 w-5 text-orange-600" />
                <h3 className="text-lg font-semibold text-gray-900">Explore Knowledge Graph</h3>
              </div>
              <p className="text-gray-700 mb-2">
                The <strong>Graph</strong> tab visualizes entities and their relationships.
              </p>
              <ul className="list-disc list-inside text-sm text-gray-600 space-y-1 ml-4">
                <li>See all extracted entities as nodes</li>
                <li>Relationships are shown as connecting edges</li>
                <li>Click nodes to view detailed information</li>
                <li>Different colors represent different entity types</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Knowledge Graph Details */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center space-x-2">
          <Database className="h-6 w-6 text-blue-600" />
          <span>Knowledge Graph</span>
        </h2>
        
        <p className="text-gray-700 mb-4">
          The knowledge graph stores structured information extracted from your documents:
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <FileText className="h-5 w-5 text-blue-600" />
              <h4 className="font-semibold text-blue-900">Documents & Chunks</h4>
            </div>
            <p className="text-sm text-blue-800">
              Documents are split into chunks. Each chunk maintains a link back to its source document.
            </p>
          </div>

          <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <Users className="h-5 w-5 text-purple-600" />
              <h4 className="font-semibold text-purple-900">Entities</h4>
            </div>
            <p className="text-sm text-purple-800">
              Named entities like people, organizations, locations, and concepts are extracted and stored.
            </p>
          </div>

          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <LinkIcon className="h-5 w-5 text-green-600" />
              <h4 className="font-semibold text-green-900">Relationships</h4>
            </div>
            <p className="text-sm text-green-800">
              Connections between entities and chunks are captured, enabling graph-based retrieval.
            </p>
          </div>
        </div>
      </div>

      {/* Technical Specs */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Technical Specifications</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Backend Technologies</h3>
            <ul className="space-y-2 text-sm text-gray-700">
              <li className="flex items-start">
                <span className="text-blue-600 mr-2">•</span>
                <span><strong>FastAPI:</strong> High-performance Python web framework</span>
              </li>
              <li className="flex items-start">
                <span className="text-blue-600 mr-2">•</span>
                <span><strong>Neo4j:</strong> Graph database for knowledge graph storage</span>
              </li>
              <li className="flex items-start">
                <span className="text-blue-600 mr-2">•</span>
                <span><strong>Sentence Transformers:</strong> Dense vector embeddings</span>
              </li>
              <li className="flex items-start">
                <span className="text-blue-600 mr-2">•</span>
                <span><strong>spaCy:</strong> Named entity recognition</span>
              </li>
              <li className="flex items-start">
                <span className="text-blue-600 mr-2">•</span>
                <span><strong>Google Gemini:</strong> AI chat responses</span>
              </li>
            </ul>
          </div>

          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Features</h3>
            <ul className="space-y-2 text-sm text-gray-700">
              <li className="flex items-start">
                <span className="text-green-600 mr-2">✓</span>
                <span>Multi-language support (English, Spanish, Arabic)</span>
              </li>
              <li className="flex items-start">
                <span className="text-green-600 mr-2">✓</span>
                <span>Multiple document format support</span>
              </li>
              <li className="flex items-start">
                <span className="text-green-600 mr-2">✓</span>
                <span>Real-time entity extraction</span>
              </li>
              <li className="flex items-start">
                <span className="text-green-600 mr-2">✓</span>
                <span>~360ms average query latency</span>
              </li>
              <li className="flex items-start">
                <span className="text-green-600 mr-2">✓</span>
                <span>Production-ready with health monitoring</span>
              </li>
            </ul>
          </div>
        </div>
      </div>

      {/* Tips & Best Practices */}
      <div className="bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200 rounded-lg p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">💡 Tips & Best Practices</h2>
        <ul className="space-y-2 text-sm text-gray-800">
          <li className="flex items-start">
            <span className="font-bold mr-2">•</span>
            <span><strong>Document Quality:</strong> Well-structured documents with clear headings yield better results</span>
          </li>
          <li className="flex items-start">
            <span className="font-bold mr-2">•</span>
            <span><strong>Query Specificity:</strong> More specific questions get more precise answers</span>
          </li>
          <li className="flex items-start">
            <span className="font-bold mr-2">•</span>
            <span><strong>Graph Exploration:</strong> Use the graph view to discover connections you didn't know existed</span>
          </li>
          <li className="flex items-start">
            <span className="font-bold mr-2">•</span>
            <span><strong>Chat Context:</strong> The chat remembers your conversation, so you can ask follow-up questions</span>
          </li>
        </ul>
      </div>
    </div>
  )
}

export default Documentation

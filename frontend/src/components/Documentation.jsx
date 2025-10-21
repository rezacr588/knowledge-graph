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

      {/* Ingestion Pipeline */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center space-x-2">
          <Upload className="h-6 w-6 text-blue-600" />
          <span>Document Ingestion Pipeline</span>
        </h2>
        <p className="text-gray-700 mb-4">
          Every document you upload flows through a deterministic pipeline so all downstream indexes stay in sync.
          The `/api/ingest/stream` endpoint powers the Upload tab and emits real-time Server-Sent Events as each stage completes.
        </p>
        <ol className="list-decimal list-inside space-y-2 text-sm text-gray-700 mb-4">
          <li>
            <strong>Document parsing:</strong> <code>DocumentParser</code> normalizes TXT, PDF, and DOCX uploads, handling encryption and encoding fallbacks automatically.
          </li>
          <li>
            <strong>Chunking & IDs:</strong> File bytes are hashed into a stable <code>document_id</code>. Paragraph-level chunks inherit IDs such as <code>doc123_chunk_0</code> and store an <code>embedding_id</code> for vector lookup.
          </li>
          <li>
            <strong>Graph persistence:</strong> <code>Neo4jClient.add_document</code> and <code>add_chunk</code> build <code>Document → CONTAINS → Chunk</code> structures inside Neo4j, keeping language and metadata attached.
          </li>
          <li>
            <strong>Entity extraction:</strong> <code>EntityExtractor</code> (spaCy with optional Gemini validation) tags each chunk, upserts <code>Entity</code> nodes, and links them via <code>MENTIONS</code> relationships.
          </li>
          <li>
            <strong>Index updates:</strong> BM25 ingests the same chunks for keyword search while the dense retriever encodes them for semantic search (in-memory or Qdrant-backed).
          </li>
        </ol>
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-sm text-blue-900">
          Progress updates such as 'Parsing...', 'Building BM25...', and 'Building dense embeddings...' mirror these steps so operators can monitor ingestion health from the UI.
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
          <span>Knowledge Graph Architecture</span>
        </h2>
        
        <p className="text-gray-700 mb-4">
          The knowledge graph is powered by <strong>Neo4j</strong>, a graph database that stores structured information 
          extracted from your documents. It enables relationship-based retrieval that goes beyond simple keyword matching.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <FileText className="h-5 w-5 text-blue-600" />
              <h4 className="font-semibold text-blue-900">Documents & Chunks</h4>
            </div>
            <p className="text-sm text-blue-800 mb-2">
              Documents are split into manageable chunks (paragraphs or sections). Each chunk maintains a link back to its source document.
            </p>
            <div className="text-xs text-blue-700 bg-blue-100 rounded p-2 font-mono">
              Document → HAS_CHUNK → Chunk
            </div>
          </div>

          <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <Users className="h-5 w-5 text-purple-600" />
              <h4 className="font-semibold text-purple-900">Entities</h4>
            </div>
            <p className="text-sm text-purple-800 mb-2">
              Named entities (PERSON, ORG, LOCATION, etc.) are extracted using spaCy NLP and Google Gemini AI. Each entity type gets a unique color in the graph.
            </p>
            <div className="text-xs text-purple-700 bg-purple-100 rounded p-2 space-y-1">
              <div>• PERSON: Individuals, names</div>
              <div>• ORG: Companies, institutions</div>
              <div>• GPE: Countries, cities</div>
              <div>• TECH: Technologies, concepts</div>
            </div>
          </div>

          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <LinkIcon className="h-5 w-5 text-green-600" />
              <h4 className="font-semibold text-green-900">Relationships</h4>
            </div>
            <p className="text-sm text-green-800 mb-2">
              Connections between entities and chunks enable graph traversal. Finding one entity automatically finds related entities.
            </p>
            <div className="text-xs text-green-700 bg-green-100 rounded p-2 font-mono">
              Chunk → CONTAINS → Entity
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-r from-gray-50 to-gray-100 border border-gray-300 rounded-lg p-5">
          <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
            <Network className="h-5 w-5 text-gray-600 mr-2" />
            Graph Structure Example
          </h4>
          <div className="bg-white rounded p-4 font-mono text-xs overflow-x-auto">
            <pre className="text-gray-700">
{`(Document: "AI Research Paper")
    |
    +-- HAS_CHUNK --> (Chunk: "Introduction to AI")
    |                      |
    |                      +-- CONTAINS --> (Entity: "Machine Learning")
    |                      |                     |
    |                      |                     +-- RELATED_TO --> (Entity: "Deep Learning")
    |                      |
    |                      +-- CONTAINS --> (Entity: "Neural Networks")
    |
    +-- HAS_CHUNK --> (Chunk: "Applications")
                           |
                           +-- CONTAINS --> (Entity: "Computer Vision")
                           +-- CONTAINS --> (Entity: "NLP")`}
            </pre>
          </div>
          <p className="text-sm text-gray-600 mt-3">
            <strong>How it helps:</strong> When you search for "Machine Learning", the system can traverse the graph 
            to find related concepts like "Deep Learning" and "Neural Networks", even if your query didn't mention them explicitly.
          </p>
        </div>

        <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-white border border-blue-200 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <Search className="h-5 w-5 text-blue-600" />
              <h4 className="font-semibold text-blue-900">Graph Retrieval Flow</h4>
            </div>
            <ul className="text-sm text-gray-700 space-y-1 list-disc list-inside">
              <li>Query entities are extracted with the same <code>EntityExtractor</code> used during ingestion.</li>
              <li>Neo4j lookups find the closest matching nodes (name + language aware).</li>
              <li>Relevant chunks are ranked by confidence-weighted <code>MENTIONS</code> relationships.</li>
              <li>Results feed into Reciprocal Rank Fusion alongside BM25 and dense scores.</li>
            </ul>
          </div>
          <div className="bg-white border border-green-200 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <Database className="h-5 w-5 text-green-600" />
              <h4 className="font-semibold text-green-900">Operational Notes</h4>
            </div>
            <ul className="text-sm text-gray-700 space-y-1 list-disc list-inside">
              <li>Unique constraints on <code>Document</code>, <code>Chunk</code>, and <code>Entity</code> IDs keep the graph consistent.</li>
              <li><code>/api/graph/stats</code> and <code>/api/graph/visualization</code> expose live graph health for the UI.</li>
              <li><code>reset_ingested_content()</code> clears Neo4j, BM25, and dense stores together before a fresh ingest.</li>
              <li>Entity relationships can be enriched with additional <code>RELATES_TO</code> edges for advanced traversal.</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Retrieval Methods Deep Dive */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center space-x-2">
          <Search className="h-6 w-6 text-purple-600" />
          <span>Retrieval Methods Explained</span>
        </h2>

        <div className="space-y-6">
          {/* BM25 */}
          <div className="border-l-4 border-blue-500 bg-blue-50 rounded-r-lg p-5">
            <h3 className="text-xl font-bold text-blue-900 mb-3 flex items-center">
              <Search className="h-5 w-5 mr-2" />
              1. BM25 (Best Matching 25)
            </h3>
            <p className="text-gray-700 mb-3">
              <strong>Type:</strong> Sparse retrieval / Keyword-based search
            </p>
            <p className="text-gray-700 mb-3">
              BM25 is a probabilistic ranking function that scores documents based on term frequency and document length. 
              It's highly effective for finding exact keyword matches and technical terminology.
            </p>
            <div className="bg-white rounded-lg p-4 mb-3">
              <p className="text-sm font-semibold text-gray-900 mb-2">How it works:</p>
              <ul className="text-sm text-gray-700 space-y-1 list-disc list-inside">
                <li>Tokenizes documents and queries into individual words</li>
                <li>Calculates term frequency (TF): How often a term appears in a document</li>
                <li>Calculates inverse document frequency (IDF): How rare/common a term is across all documents</li>
                <li>Normalizes by document length to prevent bias toward longer documents</li>
                <li>Scores each document: Higher scores = better matches</li>
              </ul>
            </div>
            <div className="bg-blue-100 rounded p-3">
              <p className="text-sm text-blue-900">
                <strong>Best for:</strong> Technical queries, proper nouns, acronyms, and exact phrase matching. 
                Example: "What is the revenue in Q4 2023?"
              </p>
            </div>
          </div>

          {/* Dense Retrieval */}
          <div className="border-l-4 border-purple-500 bg-purple-50 rounded-r-lg p-5">
            <h3 className="text-xl font-bold text-purple-900 mb-3 flex items-center">
              <Brain className="h-5 w-5 mr-2" />
              2. Dense Retrieval (Semantic Search)
            </h3>
            <p className="text-gray-700 mb-3">
              <strong>Type:</strong> Dense retrieval / Vector-based semantic search
            </p>
            <p className="text-gray-700 mb-3">
              Dense retrieval uses <strong>Sentence Transformers</strong> to convert text into high-dimensional vectors (embeddings). 
              It finds documents with similar meaning, even if they use different words.
            </p>
            <div className="bg-white rounded-lg p-4 mb-3">
              <p className="text-sm font-semibold text-gray-900 mb-2">How it works:</p>
              <ul className="text-sm text-gray-700 space-y-1 list-disc list-inside">
                <li>Converts text into 384-dimensional vectors using neural networks</li>
                <li>Captures semantic meaning: "car" and "automobile" are close in vector space</li>
                <li>Uses cosine similarity to find documents with similar embeddings</li>
                <li>Handles synonyms, paraphrases, and conceptual similarity</li>
                <li>Language-agnostic: Works across multiple languages</li>
              </ul>
            </div>
            <div className="bg-purple-100 rounded p-3">
              <p className="text-sm text-purple-900">
                <strong>Best for:</strong> Conceptual queries, questions with different phrasing, semantic understanding. 
                Example: "How do companies make money?" (finds text about "revenue generation" and "profit")</p>
            </div>
          </div>

          {/* Graph Retrieval */}
          <div className="border-l-4 border-green-500 bg-green-50 rounded-r-lg p-5">
            <h3 className="text-xl font-bold text-green-900 mb-3 flex items-center">
              <Network className="h-5 w-5 mr-2" />
              3. Knowledge Graph Retrieval
            </h3>
            <p className="text-gray-700 mb-3">
              <strong>Type:</strong> Structured retrieval / Relationship-based search
            </p>
            <p className="text-gray-700 mb-3">
              Graph retrieval uses the knowledge graph to find information through entity relationships. 
              It discovers connections that keyword or semantic search might miss.
            </p>
            <div className="bg-white rounded-lg p-4 mb-3">
              <p className="text-sm font-semibold text-gray-900 mb-2">How it works:</p>
              <ul className="text-sm text-gray-700 space-y-1 list-disc list-inside">
                <li>Extracts entities from your query using NLP</li>
                <li>Finds matching entities in the knowledge graph</li>
                <li>Traverses relationships: Entity → Chunk → Related Entities</li>
                <li>Ranks chunks by number of entity matches and connection strength</li>
                <li>Returns chunks that contain or are connected to query entities</li>
              </ul>
            </div>
            <div className="bg-green-100 rounded p-3">
              <p className="text-sm text-green-900">
                <strong>Best for:</strong> Finding related information, discovering connections, entity-centric queries. 
                Example: "Tell me about companies related to AI" (finds all organizations mentioned with AI entities)
              </p>
            </div>
          </div>

          {/* RRF Fusion */}
          <div className="border-l-4 border-orange-500 bg-orange-50 rounded-r-lg p-5">
            <h3 className="text-xl font-bold text-orange-900 mb-3 flex items-center">
              <Zap className="h-5 w-5 mr-2" />
              4. Reciprocal Rank Fusion (RRF)
            </h3>
            <p className="text-gray-700 mb-3">
              RRF combines results from all three methods into a single, optimally-ranked list. 
              It's based on the principle that documents appearing in multiple result sets are likely more relevant.
            </p>
            <div className="bg-white rounded-lg p-4 mb-3">
              <p className="text-sm font-semibold text-gray-900 mb-2">How it works:</p>
              <ul className="text-sm text-gray-700 space-y-1 list-disc list-inside">
                <li>Each method produces a ranked list of results</li>
                <li>RRF assigns scores based on rank position: 1/(k + rank)</li>
                <li>Default k=60 balances emphasis on top results</li>
                <li>Scores are summed across all methods</li>
                <li>Final list is sorted by combined RRF score</li>
                <li>Results appearing high in multiple methods get boosted</li>
              </ul>
            </div>
            <div className="bg-orange-100 rounded p-3">
              <p className="text-sm text-orange-900">
                <strong>Formula:</strong> RRF_score = Σ [ 1 / (k + rank_method) ] for each method
              </p>
            </div>
            <div className="mt-3 bg-white rounded p-3 border border-orange-200">
              <p className="text-sm text-gray-700">
                <strong>Example:</strong> A chunk ranked #1 in BM25, #3 in Dense, and #2 in Graph will score higher 
                than a chunk that's only #1 in one method but missing from the others.
              </p>
            </div>
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

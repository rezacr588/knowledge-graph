import { useState, useEffect, useRef } from 'react'
import { Network, RefreshCw, Loader2, Info, Users, FileText, Link as LinkIcon } from 'lucide-react'
import axios from 'axios'

// Color mapping for entity types
const ENTITY_COLORS = {
  'PERSON': '#3B82F6',      // Blue
  'ORGANIZATION': '#8B5CF6', // Purple
  'LOCATION': '#10B981',     // Green
  'CONCEPT': '#F59E0B',      // Orange
  'PRODUCT': '#EC4899',      // Pink
  'EVENT': '#EF4444',        // Red
  'DATE': '#6366F1',         // Indigo
  'DEFAULT': '#6B7280'       // Gray
}

function GraphVisualization() {
  const [graphData, setGraphData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedNode, setSelectedNode] = useState(null)
  const canvasRef = useRef(null)
  const [hoveredNode, setHoveredNode] = useState(null)

  useEffect(() => {
    loadGraphData()
  }, [])

  useEffect(() => {
    if (graphData && canvasRef.current) {
      drawGraph()
    }
  }, [graphData, selectedNode, hoveredNode])

  const loadGraphData = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await axios.get('/api/graph/visualization?limit=50')
      setGraphData(response.data)
    } catch (err) {
      console.error('Failed to load graph:', err)
      setError(err.response?.data?.detail || 'Failed to load graph data')
    } finally {
      setLoading(false)
    }
  }

  const drawGraph = () => {
    const canvas = canvasRef.current
    if (!canvas || !graphData) return

    const ctx = canvas.getContext('2d')
    const width = canvas.width
    const height = canvas.height

    // Clear canvas
    ctx.clearRect(0, 0, width, height)
    ctx.fillStyle = '#F9FAFB'
    ctx.fillRect(0, 0, width, height)

    const nodes = graphData.nodes || []
    const edges = graphData.edges || []

    if (nodes.length === 0) {
      ctx.fillStyle = '#6B7280'
      ctx.font = '16px sans-serif'
      ctx.textAlign = 'center'
      ctx.fillText('No entities found. Upload documents to see the knowledge graph.', width / 2, height / 2)
      return
    }

    // Simple force-directed layout simulation (pre-calculated positions)
    const nodePositions = calculateNodePositions(nodes, edges, width, height)

    // Draw edges first
    ctx.strokeStyle = '#D1D5DB'
    ctx.lineWidth = 1
    edges.forEach(edge => {
      const sourcePos = nodePositions[edge.source]
      const targetPos = nodePositions[edge.target]
      
      if (sourcePos && targetPos) {
        ctx.beginPath()
        ctx.moveTo(sourcePos.x, sourcePos.y)
        ctx.lineTo(targetPos.x, targetPos.y)
        ctx.stroke()
      }
    })

    // Draw nodes
    nodes.forEach((node, idx) => {
      const pos = nodePositions[node.id]
      if (!pos) return

      const color = ENTITY_COLORS[node.type] || ENTITY_COLORS.DEFAULT
      const isSelected = selectedNode?.id === node.id
      const isHovered = hoveredNode === idx
      const radius = isSelected || isHovered ? 10 : 8

      // Draw node circle
      ctx.beginPath()
      ctx.arc(pos.x, pos.y, radius, 0, 2 * Math.PI)
      ctx.fillStyle = color
      ctx.fill()
      
      if (isSelected || isHovered) {
        ctx.strokeStyle = '#1F2937'
        ctx.lineWidth = 2
        ctx.stroke()
      }

      // Draw label
      ctx.fillStyle = '#1F2937'
      ctx.font = isSelected || isHovered ? 'bold 12px sans-serif' : '11px sans-serif'
      ctx.textAlign = 'center'
      ctx.fillText(node.name, pos.x, pos.y - radius - 4)
    })
  }

  const calculateNodePositions = (nodes, edges, width, height) => {
    const positions = {}
    const padding = 60
    const centerX = width / 2
    const centerY = height / 2
    
    // Group nodes by type
    const nodesByType = {}
    nodes.forEach(node => {
      if (!nodesByType[node.type]) {
        nodesByType[node.type] = []
      }
      nodesByType[node.type].push(node)
    })

    // Arrange in circular layout by type
    const types = Object.keys(nodesByType)
    const angleStep = (2 * Math.PI) / nodes.length
    
    let currentAngle = 0
    nodes.forEach(node => {
      const radius = Math.min(width, height) / 2 - padding
      const x = centerX + radius * Math.cos(currentAngle) * 0.7
      const y = centerY + radius * Math.sin(currentAngle) * 0.7
      
      positions[node.id] = { x, y }
      currentAngle += angleStep
    })

    return positions
  }

  const handleCanvasClick = (e) => {
    if (!graphData) return

    const canvas = canvasRef.current
    const rect = canvas.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top

    const nodePositions = calculateNodePositions(
      graphData.nodes,
      graphData.edges,
      canvas.width,
      canvas.height
    )

    // Find clicked node
    let clickedNode = null
    for (const node of graphData.nodes) {
      const pos = nodePositions[node.id]
      if (!pos) continue

      const distance = Math.sqrt((x - pos.x) ** 2 + (y - pos.y) ** 2)
      if (distance < 10) {
        clickedNode = node
        break
      }
    }

    setSelectedNode(clickedNode)
  }

  const handleCanvasMouseMove = (e) => {
    if (!graphData) return

    const canvas = canvasRef.current
    const rect = canvas.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top

    const nodePositions = calculateNodePositions(
      graphData.nodes,
      graphData.edges,
      canvas.width,
      canvas.height
    )

    // Find hovered node
    let hoveredIdx = null
    for (let i = 0; i < graphData.nodes.length; i++) {
      const node = graphData.nodes[i]
      const pos = nodePositions[node.id]
      if (!pos) continue

      const distance = Math.sqrt((x - pos.x) ** 2 + (y - pos.y) ** 2)
      if (distance < 10) {
        hoveredIdx = i
        break
      }
    }

    setHoveredNode(hoveredIdx)
    canvas.style.cursor = hoveredIdx !== null ? 'pointer' : 'default'
  }

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-8">
        <div className="flex items-center justify-center h-96">
          <Loader2 className="h-8 w-8 text-blue-600 animate-spin" />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-8">
        <div className="text-center">
          <Network className="h-12 w-12 text-red-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Failed to Load Graph</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={loadGraphData}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <RefreshCw className="h-4 w-4 inline mr-2" />
            Retry
          </button>
        </div>
      </div>
    )
  }

  const stats = graphData?.stats || {}

  return (
    <div className="space-y-4">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Documents</p>
              <p className="text-2xl font-bold text-gray-900">{stats.documents || 0}</p>
            </div>
            <FileText className="h-8 w-8 text-blue-500" />
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Chunks</p>
              <p className="text-2xl font-bold text-gray-900">{stats.chunks || 0}</p>
            </div>
            <FileText className="h-8 w-8 text-green-500" />
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Entities</p>
              <p className="text-2xl font-bold text-gray-900">{stats.entities || 0}</p>
            </div>
            <Users className="h-8 w-8 text-purple-500" />
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Relationships</p>
              <p className="text-2xl font-bold text-gray-900">{stats.relationships || 0}</p>
            </div>
            <LinkIcon className="h-8 w-8 text-orange-500" />
          </div>
        </div>
      </div>

      {/* Graph Visualization */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Network className="h-5 w-5 text-blue-600" />
            <h2 className="text-lg font-semibold text-gray-900">Knowledge Graph</h2>
          </div>
          <button
            onClick={loadGraphData}
            className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200 flex items-center space-x-1"
          >
            <RefreshCw className="h-4 w-4" />
            <span>Refresh</span>
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Canvas */}
          <div className="lg:col-span-2">
            <canvas
              ref={canvasRef}
              width={800}
              height={600}
              onClick={handleCanvasClick}
              onMouseMove={handleCanvasMouseMove}
              className="border border-gray-200 rounded-lg w-full"
            />
          </div>

          {/* Side Panel */}
          <div className="space-y-4">
            {/* Legend */}
            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="text-sm font-semibold text-gray-900 mb-3">Entity Types</h3>
              <div className="space-y-2">
                {Object.entries(ENTITY_COLORS).filter(([key]) => key !== 'DEFAULT').map(([type, color]) => (
                  <div key={type} className="flex items-center space-x-2">
                    <div
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: color }}
                    />
                    <span className="text-xs text-gray-700">{type}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Selected Node Info */}
            {selectedNode ? (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="text-sm font-semibold text-gray-900 mb-2">Selected Entity</h3>
                <div className="space-y-2 text-sm">
                  <div>
                    <span className="font-medium">Name:</span> {selectedNode.name}
                  </div>
                  <div>
                    <span className="font-medium">Type:</span> {selectedNode.type}
                  </div>
                  <div>
                    <span className="font-medium">Language:</span> {selectedNode.language.toUpperCase()}
                  </div>
                  <div>
                    <span className="font-medium">Confidence:</span> {(selectedNode.confidence * 100).toFixed(1)}%
                  </div>
                </div>
                <button
                  onClick={() => setSelectedNode(null)}
                  className="mt-3 w-full px-3 py-1 text-xs bg-white border border-blue-300 text-blue-700 rounded hover:bg-blue-50"
                >
                  Clear Selection
                </button>
              </div>
            ) : (
              <div className="bg-gray-50 rounded-lg p-4 text-center text-sm text-gray-600">
                <Info className="h-5 w-5 mx-auto mb-2 text-gray-400" />
                Click on a node to see details
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default GraphVisualization

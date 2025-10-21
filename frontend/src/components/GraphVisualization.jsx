import { useState, useEffect, useRef } from 'react'
import { Network, RefreshCw, Loader2, Info, Users, FileText, Link as LinkIcon, ZoomIn, ZoomOut, Maximize2, Move, Maximize } from 'lucide-react'
import axios from 'axios'

// Enhanced color mapping for entity types
const ENTITY_COLORS = {
  'PERSON': '#3B82F6',       // Blue
  'ORGANIZATION': '#8B5CF6', // Purple
  'ORG': '#8B5CF6',          // Purple (alias)
  'LOCATION': '#10B981',     // Green
  'GPE': '#10B981',          // Green (geo-political)
  'CONCEPT': '#F59E0B',      // Orange
  'PRODUCT': '#EC4899',      // Pink
  'EVENT': '#EF4444',        // Red
  'DATE': '#6366F1',         // Indigo
  'TECH': '#14B8A6',         // Teal
  'TECHNOLOGY': '#14B8A6',   // Teal (alias)
  'DEFAULT': '#6B7280'       // Gray
}

function GraphVisualization() {
  const [graphData, setGraphData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedNode, setSelectedNode] = useState(null)
  const canvasRef = useRef(null)
  const [hoveredNode, setHoveredNode] = useState(null)
  const [nodePositions, setNodePositions] = useState(null)
  const [zoom, setZoom] = useState(1)
  const [pan, setPan] = useState({ x: 0, y: 0 })
  const [isDragging, setIsDragging] = useState(false)
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 })
  const [isFullscreen, setIsFullscreen] = useState(false)
  const containerRef = useRef(null)

  useEffect(() => {
    loadGraphData()
  }, [])

  useEffect(() => {
    if (graphData && canvasRef.current) {
      // Calculate positions when graph data changes
      const canvas = canvasRef.current
      const positions = calculateNodePositions(
        graphData.nodes || [],
        graphData.edges || [],
        canvas.width,
        canvas.height
      )
      setNodePositions(positions)
    }
  }, [graphData])

  useEffect(() => {
    if (graphData && canvasRef.current && nodePositions) {
      drawGraph()
    }
  }, [graphData, selectedNode, hoveredNode, nodePositions, zoom, pan])

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

    // Clear with gradient background
    ctx.clearRect(0, 0, width, height)
    const gradient = ctx.createLinearGradient(0, 0, 0, height)
    gradient.addColorStop(0, '#F9FAFB')
    gradient.addColorStop(1, '#F3F4F6')
    ctx.fillStyle = gradient
    ctx.fillRect(0, 0, width, height)
    
    // Apply zoom and pan transformations
    ctx.save()
    ctx.translate(pan.x, pan.y)
    ctx.scale(zoom, zoom)

    const nodes = graphData.nodes || []
    const edges = graphData.edges || []

    if (nodes.length === 0) {
      ctx.fillStyle = '#6B7280'
      ctx.font = '16px sans-serif'
      ctx.textAlign = 'center'
      ctx.fillText('No entities found. Upload documents to see the knowledge graph.', width / 2, height / 2)
      return
    }

    // Use cached positions from state
    if (!nodePositions) return

    // Get node degrees for sizing
    const getNodeDegree = (nodeId) => {
      return edges.filter(e => e.source === nodeId || e.target === nodeId).length
    }
    
    // Get connected nodes for highlighting
    const getConnectedNodes = (nodeId) => {
      const connected = new Set()
      edges.forEach(edge => {
        if (edge.source === nodeId) connected.add(edge.target)
        if (edge.target === nodeId) connected.add(edge.source)
      })
      return connected
    }
    
    const connectedNodes = hoveredNode !== null 
      ? getConnectedNodes(nodes[hoveredNode].id)
      : new Set()

    // Draw edges first (with labels and better visibility)
    edges.forEach((edge, idx) => {
      const sourcePos = nodePositions[edge.source]
      const targetPos = nodePositions[edge.target]
      
      if (sourcePos && targetPos) {
        const isHoveredEdge = hoveredNode !== null && (graphData.nodes[hoveredNode]?.id === edge.source || graphData.nodes[hoveredNode]?.id === edge.target)
        const isSelectedEdge = selectedNode && (selectedNode.id === edge.source || selectedNode.id === edge.target)
        const isDimmed = (hoveredNode !== null || selectedNode) && !isHoveredEdge && !isSelectedEdge
        
        // Choose edge color based on type
        let edgeColor = '#6B7280' // Default gray
        if (edge.type === 'CO_OCCURS') edgeColor = '#3B82F6' // Blue for co-occurrence
        if (edge.type === 'RELATES_TO') edgeColor = '#9333EA' // Purple for direct relations
        
        ctx.strokeStyle = edgeColor
        ctx.lineWidth = (isHoveredEdge || isSelectedEdge) ? (edge.weight ? Math.min(edge.weight + 2, 6) : 4) : (edge.weight ? Math.min(edge.weight, 3) : 2.5)
        ctx.globalAlpha = isDimmed ? 0.15 : ((isHoveredEdge || isSelectedEdge) ? 0.9 : 0.6)
        
        // Draw line
        ctx.beginPath()
        ctx.moveTo(sourcePos.x, sourcePos.y)
        ctx.lineTo(targetPos.x, targetPos.y)
        ctx.stroke()
        
        // Draw edge label (always visible, or on hover for clarity)
        if (edge.label && (edges.length < 30 || isHoveredEdge || isSelectedEdge)) {
          const midX = (sourcePos.x + targetPos.x) / 2
          const midY = (sourcePos.y + targetPos.y) / 2
          
          ctx.font = 'bold 10px sans-serif'
          ctx.textAlign = 'center'
          ctx.textBaseline = 'middle'
          
          // Label background
          const metrics = ctx.measureText(edge.label)
          const textWidth = metrics.width
          ctx.fillStyle = '#FFFFFF'
          ctx.globalAlpha = isDimmed ? 0.2 : 0.95
          ctx.shadowColor = 'rgba(0, 0, 0, 0.1)'
          ctx.shadowBlur = 3
          ctx.fillRect(midX - textWidth/2 - 5, midY - 8, textWidth + 10, 16)
          ctx.shadowBlur = 0
          
          // Label text
          ctx.fillStyle = (isHoveredEdge || isSelectedEdge) ? '#1F2937' : '#6B7280'
          ctx.globalAlpha = isDimmed ? 0.2 : 1
          ctx.fillText(edge.label, midX, midY)
        }
        
        ctx.globalAlpha = 1
      }
    })

    // Draw nodes with enhanced visibility
    nodes.forEach((node, idx) => {
      const pos = nodePositions[node.id]
      if (!pos) return

      const color = ENTITY_COLORS[node.type] || ENTITY_COLORS.DEFAULT
      const isSelected = selectedNode?.id === node.id
      const isHovered = hoveredNode === idx
      const isConnected = connectedNodes.has(node.id)
      const isDimmed = (hoveredNode !== null || selectedNode) && !isSelected && !isHovered && !isConnected
      
      // Vary node size by degree
      const degree = getNodeDegree(node.id)
      const baseRadius = 12
      const sizeBonus = Math.min(degree * 1.5, 10)
      const radius = (isSelected || isHovered) ? baseRadius + sizeBonus + 4 : baseRadius + sizeBonus

      // Draw 3D shadow (elevation effect)
      ctx.beginPath()
      ctx.arc(pos.x + 3, pos.y + 3, radius, 0, 2 * Math.PI)
      ctx.fillStyle = 'rgba(0, 0, 0, 0.2)'
      ctx.globalAlpha = isDimmed ? 0.1 : 0.3
      ctx.fill()
      ctx.globalAlpha = 1
      
      // Draw glow for selected/hovered
      if (isSelected || isHovered) {
        ctx.beginPath()
        ctx.arc(pos.x, pos.y, radius + 12, 0, 2 * Math.PI)
        const glowGradient = ctx.createRadialGradient(pos.x, pos.y, radius, pos.x, pos.y, radius + 12)
        glowGradient.addColorStop(0, color + '60')
        glowGradient.addColorStop(0.5, color + '30')
        glowGradient.addColorStop(1, color + '00')
        ctx.fillStyle = glowGradient
        ctx.fill()
      }

      // Draw node with enhanced 3D gradient
      ctx.beginPath()
      ctx.arc(pos.x, pos.y, radius, 0, 2 * Math.PI)
      const nodeGradient = ctx.createRadialGradient(
        pos.x - radius/2.5, 
        pos.y - radius/2.5, 
        radius * 0.1,
        pos.x, 
        pos.y, 
        radius * 1.2
      )
      nodeGradient.addColorStop(0, adjustColor(color, 60))  // Bright highlight
      nodeGradient.addColorStop(0.3, color)                  // Main color
      nodeGradient.addColorStop(0.7, adjustColor(color, -30)) // Darker
      nodeGradient.addColorStop(1, adjustColor(color, -50))   // Darkest edge
      ctx.fillStyle = nodeGradient
      ctx.globalAlpha = isDimmed ? 0.25 : 1
      ctx.fill()
      
      // Node border with 3D effect (lighter on top)
      ctx.strokeStyle = (isSelected || isHovered) ? '#1F2937' : 'rgba(255, 255, 255, 0.8)'
      ctx.lineWidth = (isSelected || isHovered) ? 3 : 2.5
      ctx.shadowColor = 'rgba(0, 0, 0, 0.3)'
      ctx.shadowBlur = (isSelected || isHovered) ? 8 : 4
      ctx.shadowOffsetX = 2
      ctx.shadowOffsetY = 2
      ctx.stroke()
      ctx.shadowBlur = 0
      ctx.shadowOffsetX = 0
      ctx.shadowOffsetY = 0
      
      // Draw type badge for hub nodes
      if (degree > 3 && radius > 16) {
        ctx.font = 'bold 9px sans-serif'
        ctx.textAlign = 'center'
        ctx.textBaseline = 'middle'
        ctx.fillStyle = '#FFFFFF'
        ctx.globalAlpha = isDimmed ? 0.25 : 0.9
        ctx.fillText(node.type.substring(0, 3).toUpperCase(), pos.x, pos.y)
      }
      ctx.globalAlpha = 1

      // Draw label with background
      const labelY = pos.y - radius - 10
      const displayName = node.name.length > 22 ? node.name.substring(0, 22) + '...' : node.name
      
      ctx.font = (isSelected || isHovered) ? 'bold 13px sans-serif' : '12px sans-serif'
      ctx.textAlign = 'center'
      ctx.textBaseline = 'bottom'
      
      // Label background
      const labelMetrics = ctx.measureText(displayName)
      const labelWidth = labelMetrics.width
      ctx.fillStyle = 'rgba(255, 255, 255, 0.95)'
      ctx.globalAlpha = isDimmed ? 0.25 : 0.95
      ctx.shadowColor = 'rgba(0, 0, 0, 0.1)'
      ctx.shadowBlur = 3
      ctx.fillRect(pos.x - labelWidth/2 - 6, labelY - 16, labelWidth + 12, 18)
      ctx.shadowBlur = 0
      
      // Label text
      ctx.fillStyle = (isSelected || isHovered) ? '#1F2937' : '#374151'
      ctx.globalAlpha = isDimmed ? 0.25 : 1
      ctx.fillText(displayName, pos.x, labelY - 6)
      ctx.globalAlpha = 1
    })
    
    // Restore context after drawing
    ctx.restore()
  }
  
  const adjustColor = (color, amount) => {
    const hex = color.replace('#', '')
    const r = Math.max(0, Math.min(255, parseInt(hex.slice(0, 2), 16) + amount))
    const g = Math.max(0, Math.min(255, parseInt(hex.slice(2, 4), 16) + amount))
    const b = Math.max(0, Math.min(255, parseInt(hex.slice(4, 6), 16) + amount))
    return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`
  }

  const calculateNodePositions = (nodes, edges, width, height) => {
    const positions = {}
    const velocities = {}
    const centerX = width / 2
    const centerY = height / 2
    
    // Initialize random positions with velocities
    nodes.forEach(node => {
      const angle = Math.random() * 2 * Math.PI
      const radius = Math.min(width, height) * 0.3
      positions[node.id] = {
        x: centerX + Math.cos(angle) * radius * Math.random(),
        y: centerY + Math.sin(angle) * radius * Math.random()
      }
      velocities[node.id] = { x: 0, y: 0 }
    })

    // Force-directed layout simulation (simplified)
    // Run multiple iterations to find optimal positions
    const iterations = 150
    const repulsionStrength = 12000 // 3x stronger - more space!
    const attractionStrength = 0.008 // Weaker attraction
    const damping = 0.85
    const minDistance = 150 // 50% larger minimum distance
    
    // Build adjacency map for quick edge lookup
    const adjacency = {}
    edges.forEach(edge => {
      if (!adjacency[edge.source]) adjacency[edge.source] = []
      if (!adjacency[edge.target]) adjacency[edge.target] = []
      adjacency[edge.source].push(edge.target)
      adjacency[edge.target].push(edge.source)
    })

    for (let iter = 0; iter < iterations; iter++) {
      const forces = {}
      nodes.forEach(node => {
        forces[node.id] = { x: 0, y: 0 }
      })

      // 1. Repulsion force: All nodes repel each other
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const node1 = nodes[i]
          const node2 = nodes[j]
          const pos1 = positions[node1.id]
          const pos2 = positions[node2.id]
          
          const dx = pos2.x - pos1.x
          const dy = pos2.y - pos1.y
          const distSq = dx * dx + dy * dy + 0.01 // Avoid division by zero
          const dist = Math.sqrt(distSq)
          
          if (dist < minDistance * 3) {
            const force = repulsionStrength / distSq
            const fx = (dx / dist) * force
            const fy = (dy / dist) * force
            
            forces[node1.id].x -= fx
            forces[node1.id].y -= fy
            forces[node2.id].x += fx
            forces[node2.id].y += fy
          }
        }
      }

      // 2. Attraction force: Connected nodes attract each other
      edges.forEach(edge => {
        const pos1 = positions[edge.source]
        const pos2 = positions[edge.target]
        
        if (pos1 && pos2) {
          const dx = pos2.x - pos1.x
          const dy = pos2.y - pos1.y
          const dist = Math.sqrt(dx * dx + dy * dy)
          
          // Spring force pulling connected nodes together
          const optimalDistance = 250 // More space between connected nodes
          const force = (dist - optimalDistance) * attractionStrength
          const fx = (dx / dist) * force
          const fy = (dy / dist) * force
          
          forces[edge.source].x += fx
          forces[edge.source].y += fy
          forces[edge.target].x -= fx
          forces[edge.target].y -= fy
        }
      })

      // 3. Center gravity: Pull nodes toward center
      const gravityStrength = 0.05
      nodes.forEach(node => {
        const pos = positions[node.id]
        const dx = centerX - pos.x
        const dy = centerY - pos.y
        forces[node.id].x += dx * gravityStrength
        forces[node.id].y += dy * gravityStrength
      })

      // Apply forces to velocities and update positions
      nodes.forEach(node => {
        const velocity = velocities[node.id]
        const force = forces[node.id]
        const pos = positions[node.id]
        
        // Update velocity
        velocity.x = (velocity.x + force.x) * damping
        velocity.y = (velocity.y + force.y) * damping
        
        // Update position
        pos.x += velocity.x
        pos.y += velocity.y
        
        // Keep within bounds with some padding
        const padding = 100
        pos.x = Math.max(padding, Math.min(width - padding, pos.x))
        pos.y = Math.max(padding, Math.min(height - padding, pos.y))
      })
    }

    return positions
  }

  const handleCanvasClick = (e) => {
    if (!graphData || !nodePositions || isDragging) return

    const canvas = canvasRef.current
    const rect = canvas.getBoundingClientRect()
    // Transform mouse coordinates to account for zoom and pan
    const x = (e.clientX - rect.left - pan.x) / zoom
    const y = (e.clientY - rect.top - pan.y) / zoom

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
    if (!graphData || !nodePositions) return

    const canvas = canvasRef.current
    const rect = canvas.getBoundingClientRect()
    
    // Handle dragging to pan
    if (isDragging) {
      const dx = e.clientX - dragStart.x
      const dy = e.clientY - dragStart.y
      setPan({ x: pan.x + dx, y: pan.y + dy })
      setDragStart({ x: e.clientX, y: e.clientY })
      canvas.style.cursor = 'grabbing'
      return
    }
    
    // Transform mouse coordinates
    const x = (e.clientX - rect.left - pan.x) / zoom
    const y = (e.clientY - rect.top - pan.y) / zoom

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
    canvas.style.cursor = hoveredIdx !== null ? 'pointer' : 'grab'
  }
  
  const handleMouseDown = (e) => {
    if (!canvasRef.current) return
    // Only start dragging if not clicking on a node
    const canvas = canvasRef.current
    const rect = canvas.getBoundingClientRect()
    const x = (e.clientX - rect.left - pan.x) / zoom
    const y = (e.clientY - rect.top - pan.y) / zoom
    
    // Check if clicking on a node
    let onNode = false
    if (graphData && nodePositions) {
      for (const node of graphData.nodes) {
        const pos = nodePositions[node.id]
        if (!pos) continue
        const degree = graphData.edges.filter(e => e.source === node.id || e.target === node.id).length
        const radius = 12 + Math.min(degree * 1.5, 10)
        const distance = Math.sqrt((x - pos.x) ** 2 + (y - pos.y) ** 2)
        if (distance < radius + 5) {
          onNode = true
          break
        }
      }
    }
    
    if (!onNode) {
      setIsDragging(true)
      setDragStart({ x: e.clientX, y: e.clientY })
      canvas.style.cursor = 'grabbing'
    }
  }
  
  const handleMouseUp = () => {
    setIsDragging(false)
    if (canvasRef.current) {
      canvasRef.current.style.cursor = hoveredNode !== null ? 'pointer' : 'grab'
    }
  }
  
  const handleWheel = (e) => {
    e.preventDefault()
    const delta = e.deltaY > 0 ? 0.9 : 1.1
    const newZoom = Math.max(0.3, Math.min(3, zoom * delta))
    
    // Zoom towards mouse position
    const canvas = canvasRef.current
    const rect = canvas.getBoundingClientRect()
    const mouseX = e.clientX - rect.left
    const mouseY = e.clientY - rect.top
    
    // Adjust pan to zoom towards cursor
    const newPan = {
      x: mouseX - (mouseX - pan.x) * (newZoom / zoom),
      y: mouseY - (mouseY - pan.y) * (newZoom / zoom)
    }
    
    setZoom(newZoom)
    setPan(newPan)
  }
  
  const handleZoomIn = () => {
    const newZoom = Math.min(3, zoom * 1.2)
    setZoom(newZoom)
  }
  
  const handleZoomOut = () => {
    const newZoom = Math.max(0.3, zoom / 1.2)
    setZoom(newZoom)
  }
  
  const handleResetView = () => {
    setZoom(1)
    setPan({ x: 0, y: 0 })
  }
  
  const toggleFullscreen = () => {
    if (!containerRef.current) return
    
    if (!document.fullscreenElement) {
      containerRef.current.requestFullscreen().then(() => {
        setIsFullscreen(true)
      }).catch(err => {
        console.error('Error entering fullscreen:', err)
      })
    } else {
      document.exitFullscreen().then(() => {
        setIsFullscreen(false)
      })
    }
  }
  
  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement)
    }
    
    document.addEventListener('fullscreenchange', handleFullscreenChange)
    return () => document.removeEventListener('fullscreenchange', handleFullscreenChange)
  }, [])

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
      <div ref={containerRef} className={`bg-white rounded-lg shadow-lg p-6 transition-all ${isFullscreen ? 'fixed inset-0 z-50' : ''}`}>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Network className="h-5 w-5 text-blue-600" />
            <h2 className="text-lg font-semibold text-gray-900">Knowledge Graph</h2>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={toggleFullscreen}
              className={`px-3 py-2 text-sm rounded-lg flex items-center space-x-2 transition ${
                isFullscreen
                  ? 'bg-blue-600 text-white hover:bg-blue-700'
                  : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
              }`}
              title="Toggle fullscreen"
            >
              <Maximize className="h-4 w-4" />
              <span>{isFullscreen ? 'Exit' : 'Fullscreen'}</span>
            </button>
            <button
              onClick={loadGraphData}
              className="px-3 py-2 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 flex items-center space-x-2 transition"
            >
              <RefreshCw className="h-4 w-4" />
              <span>Refresh</span>
            </button>
          </div>
        </div>

        {/* Info about relationships */}
        {graphData && (graphData.edges?.length > 0 || graphData.nodes?.length > 0) && (
          <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-start space-x-2">
              <Info className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
              <div className="text-sm text-blue-900">
                <p className="font-medium mb-1">Interactive Graph Visualization</p>
                <p className="text-blue-700">
                  {graphData.nodes?.length || 0} entities connected by {graphData.edges?.length || 0} relationships.
                  {graphData.edges?.length > 0 && (
                    <span className="block mt-1">
                      <strong>Hover over nodes</strong> to highlight their connections. 
                      Edges show co-occurrence relationships (entities mentioned together).
                    </span>
                  )}
                  {graphData.edges?.length === 0 && (
                    <span className="block mt-1">
                      No relationships yet. Upload more documents with related entities to see connections!
                    </span>
                  )}
                </p>
              </div>
            </div>
          </div>
        )}

        <div className={`grid gap-6 ${isFullscreen ? 'grid-cols-1' : 'grid-cols-1 lg:grid-cols-3'}`}>
          {/* Canvas */}
          <div className={isFullscreen ? '' : 'lg:col-span-2'}>
            <div className={`relative border-2 border-gray-200 rounded-xl overflow-hidden shadow-inner bg-gradient-to-br from-gray-50 to-gray-100 ${isFullscreen ? 'h-[calc(100vh-12rem)]' : ''}`}>
              <canvas
                ref={canvasRef}
                width={isFullscreen ? 2000 : 1200}
                height={isFullscreen ? 1200 : 800}
                onClick={handleCanvasClick}
                onMouseMove={handleCanvasMouseMove}
                onMouseDown={handleMouseDown}
                onMouseUp={handleMouseUp}
                onMouseLeave={handleMouseUp}
                onWheel={handleWheel}
                className="w-full cursor-grab"
                style={{ display: 'block', height: isFullscreen ? '100%' : 'auto' }}
              />
              
              {/* Zoom controls */}
              <div className="absolute bottom-4 right-4 flex flex-col gap-2">
                <button
                  onClick={handleZoomIn}
                  className="p-2 bg-white rounded-lg shadow-lg hover:bg-gray-50 transition border border-gray-200"
                  title="Zoom in"
                >
                  <ZoomIn className="h-5 w-5 text-gray-700" />
                </button>
                <button
                  onClick={handleZoomOut}
                  className="p-2 bg-white rounded-lg shadow-lg hover:bg-gray-50 transition border border-gray-200"
                  title="Zoom out"
                >
                  <ZoomOut className="h-5 w-5 text-gray-700" />
                </button>
                <button
                  onClick={handleResetView}
                  className="p-2 bg-white rounded-lg shadow-lg hover:bg-gray-50 transition border border-gray-200"
                  title="Reset view"
                >
                  <Maximize2 className="h-5 w-5 text-gray-700" />
                </button>
              </div>
              
              {/* Zoom indicator */}
              <div className="absolute bottom-4 left-4 px-3 py-2 bg-white rounded-lg shadow-lg border border-gray-200">
                <div className="flex items-center space-x-2">
                  <Move className="h-4 w-4 text-gray-600" />
                  <span className="text-sm font-medium text-gray-700">{Math.round(zoom * 100)}%</span>
                </div>
              </div>
            </div>
            <p className="text-xs text-gray-500 mt-2 text-center">
              🖱️ Drag to pan • Scroll to zoom • Click nodes to select • Hover to highlight
            </p>
          </div>

          {/* Side Panel */}
          {!isFullscreen && <div className="space-y-4">
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
          </div>}
        </div>
      </div>
    </div>
  )
}

export default GraphVisualization

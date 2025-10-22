import { useState, useEffect, useRef } from 'react'
import { Network, RefreshCw, Loader2, Info, Users, FileText, Link as LinkIcon, Maximize, ZoomIn, ZoomOut, Maximize2, Trash2, Settings, X } from 'lucide-react'
import * as d3 from 'd3'
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
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [showLegend, setShowLegend] = useState(true)
  const [showResetConfirm, setShowResetConfirm] = useState(false)
  const [isResetting, setIsResetting] = useState(false)
  const [showSettings, setShowSettings] = useState(false)
  const containerRef = useRef(null)
  const svgRef = useRef(null)
  const simulationRef = useRef(null)

  useEffect(() => {
    loadGraphData()
  }, [])

  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement)
    }
    
    document.addEventListener('fullscreenchange', handleFullscreenChange)
    return () => document.removeEventListener('fullscreenchange', handleFullscreenChange)
  }, [])

  const loadGraphData = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await axios.get('/api/graph/visualization?limit=100')
      setGraphData(response.data)
    } catch (err) {
      console.error('Failed to load graph:', err)
      setError(err.response?.data?.detail || 'Failed to load graph data')
    } finally {
      setLoading(false)
    }
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

  const handleZoomIn = () => {
    if (svgRef.current) {
      const svg = d3.select(svgRef.current)
      svg.transition().call(
        d3.zoom().scaleBy.bind(null, svg),
        1.2
      )
    }
  }

  const handleZoomOut = () => {
    if (svgRef.current) {
      const svg = d3.select(svgRef.current)
      svg.transition().call(
        d3.zoom().scaleBy.bind(null, svg),
        0.8
      )
    }
  }

  const handleResetView = () => {
    if (svgRef.current) {
      const svg = d3.select(svgRef.current)
      svg.transition().call(
        d3.zoom().transform.bind(null, svg),
        d3.zoomIdentity
      )
      if (simulationRef.current) {
        simulationRef.current.alpha(1).restart()
      }
    }
  }

  const handleResetDatabase = async () => {
    setIsResetting(true)
    setError(null)
    try {
      await axios.post('/api/admin/reset-all')
      // Reload data after successful reset
      setShowResetConfirm(false)
      setSelectedNode(null)
      await loadGraphData()
      alert('✅ Database reset successfully! All data has been cleared.')
    } catch (err) {
      console.error('Failed to reset database:', err)
      setError(err.response?.data?.detail || 'Failed to reset database')
      alert('❌ Failed to reset database. Check console for details.')
    } finally {
      setIsResetting(false)
    }
  }

  // Transform backend data to NVL format
  const transformToNVLFormat = () => {
    if (!graphData) return { nodes: [], relationships: [] }

    const nodes = (graphData.nodes || []).map(node => {
      const isSelected = selectedNode?.id === node.id
      return {
        id: node.id,
        caption: node.name,
        size: isSelected ? 50 : 20 + (node.confidence || 0) * 30, // Larger if selected
        color: isSelected ? '#EF4444' : (ENTITY_COLORS[node.type] || ENTITY_COLORS.DEFAULT), // Red if selected
        labels: [node.type],
        properties: {
          type: node.type,
          language: node.language,
          confidence: node.confidence
        },
        ...(isSelected && {
          style: {
            'border-width': 4,
            'border-color': '#1F2937',
            'glow': true
          }
        })
      }
    })

    const relationships = (graphData.edges || []).map((edge, idx) => {
      const isConnectedToSelected = selectedNode && (
        edge.source === selectedNode.id || edge.target === selectedNode.id
      )
      return {
        id: edge.id || `edge_${idx}`,
        source: edge.source,  // D3 requires 'source'
        target: edge.target,  // D3 requires 'target'
        caption: edge.label || edge.type,
        type: edge.type,
        properties: {
          confidence: edge.confidence,
          weight: edge.weight
        },
        ...(isConnectedToSelected && {
          style: {
            width: 4,
            color: '#EF4444' // Red for connected relationships
          }
        })
      }
    })

    return { nodes, relationships }
  }

  const { nodes, relationships } = transformToNVLFormat()
  
  // Debug logging
  useEffect(() => {
    if (graphData) {
      console.log('Graph Data:', {
        nodeCount: nodes.length,
        relationshipCount: relationships.length,
        sampleNode: nodes[0],
        sampleRel: relationships[0]
      })
    }
  }, [graphData, nodes, relationships])

  // Render D3 graph - Updated with validation
  useEffect(() => {
    if (!svgRef.current || !graphData || nodes.length === 0) return
    
    console.log('=== Rendering D3 Graph (v2) ===')

    const svg = d3.select(svgRef.current)
    const width = svgRef.current.clientWidth
    const height = svgRef.current.clientHeight

    // Create node ID set for validation
    const nodeIds = new Set(nodes.map(n => n.id))
    
    // Filter relationships to only include valid ones
    const validRelationships = relationships.filter(rel => {
      const hasValidSource = nodeIds.has(rel.source)
      const hasValidTarget = nodeIds.has(rel.target)
      if (!hasValidSource || !hasValidTarget) {
        console.warn('Invalid relationship:', rel, 'source:', hasValidSource, 'target:', hasValidTarget)
        return false
      }
      return true
    })

    console.log('Nodes:', nodes.length)
    console.log('All relationships:', relationships.length)
    console.log('Valid relationships:', validRelationships.length)
    console.log('Sample node IDs:', nodes.slice(0, 3).map(n => n.id))
    console.log('Sample relationships:', validRelationships.slice(0, 3))

    if (validRelationships.length === 0 && relationships.length > 0) {
      console.error('No valid relationships! Check if node IDs match relationship from/to IDs')
    }

    // Clear previous graph
    svg.selectAll('*').remove()

    // Create zoom behavior
    const zoom = d3.zoom()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => {
        g.attr('transform', event.transform)
      })

    svg.call(zoom)

    const g = svg.append('g')

    // Create simulation with error handling
    let simulation
    try {
      simulation = d3.forceSimulation(nodes)
        .force('link', d3.forceLink(validRelationships)
          .id(d => d.id)
          .distance(100)
          .strength(0.5))
        .force('charge', d3.forceManyBody().strength(-300))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collision', d3.forceCollide().radius(d => (d.size || 20) / 2 + 10))
      
      simulationRef.current = simulation
      console.log('✅ Simulation created successfully')
    } catch (error) {
      console.error('❌ Error creating simulation:', error)
      console.error('Nodes:', nodes)
      console.error('Valid relationships:', validRelationships)
      return // Exit if simulation fails
    }

    // Draw links
    const link = g.append('g')
      .selectAll('line')
      .data(validRelationships)
      .join('line')
      .attr('stroke', d => {
        const isConnected = selectedNode && (d.source.id === selectedNode.id || d.target.id === selectedNode.id)
        return isConnected ? '#EF4444' : '#CBD5E1'
      })
      .attr('stroke-width', d => {
        const isConnected = selectedNode && (d.source.id === selectedNode.id || d.target.id === selectedNode.id)
        return isConnected ? 3 : 2
      })
      .attr('stroke-opacity', 0.6)

    // Draw link labels
    const linkLabel = g.append('g')
      .selectAll('text')
      .data(validRelationships)
      .join('text')
      .attr('text-anchor', 'middle')
      .attr('font-size', '10px')
      .attr('fill', '#64748B')
      .text(d => d.caption || d.type)

    // Draw nodes
    const node = g.append('g')
      .selectAll('circle')
      .data(nodes)
      .join('circle')
      .attr('r', d => (d.id === selectedNode?.id ? 25 : d.size / 2))
      .attr('fill', d => (d.id === selectedNode?.id ? '#EF4444' : d.color))
      .attr('stroke', d => (d.id === selectedNode?.id ? '#1F2937' : '#FFF'))
      .attr('stroke-width', d => (d.id === selectedNode?.id ? 3 : 2))
      .style('cursor', 'pointer')
      .call(d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended))
      .on('click', (event, d) => {
        event.stopPropagation()
        setSelectedNode(d)
      })

    // Draw node labels
    const nodeLabel = g.append('g')
      .selectAll('text')
      .data(nodes)
      .join('text')
      .attr('text-anchor', 'middle')
      .attr('dy', '0.3em')
      .attr('font-size', d => (d.id === selectedNode?.id ? '12px' : '11px'))
      .attr('font-weight', d => (d.id === selectedNode?.id ? 'bold' : 'normal'))
      .attr('fill', '#1F2937')
      .attr('pointer-events', 'none')
      .text(d => d.caption)

    // Canvas click to deselect
    svg.on('click', () => setSelectedNode(null))

    // Update positions on simulation tick
    simulation.on('tick', () => {
      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y)

      linkLabel
        .attr('x', d => (d.source.x + d.target.x) / 2)
        .attr('y', d => (d.source.y + d.target.y) / 2)

      node
        .attr('cx', d => d.x)
        .attr('cy', d => d.y)

      nodeLabel
        .attr('x', d => d.x)
        .attr('y', d => d.y)
    })

    // Drag functions
    function dragstarted(event) {
      if (!event.active) simulation.alphaTarget(0.3).restart()
      event.subject.fx = event.subject.x
      event.subject.fy = event.subject.y
    }

    function dragged(event) {
      event.subject.fx = event.x
      event.subject.fy = event.y
    }

    function dragended(event) {
      if (!event.active) simulation.alphaTarget(0)
      event.subject.fx = null
      event.subject.fy = null
    }

    // Cleanup
    return () => {
      simulation.stop()
    }
  }, [graphData, nodes, relationships, selectedNode])

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
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
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
            <h2 className="text-lg font-semibold text-gray-900">Knowledge Graph Explorer</h2>
            <span className="text-sm text-gray-500">({nodes.length} entities · {relationships.length} relationships)</span>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowSettings(true)}
              className="px-3 py-2 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 flex items-center space-x-2 transition"
              title="Settings"
            >
              <Settings className="h-4 w-4" />
              <span>Settings</span>
            </button>
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
        {relationships.length > 0 && (
          <div className="mb-4 p-4 bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-lg">
            <div className="flex items-start space-x-3">
              <Info className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
              <div className="text-sm">
                <p className="font-semibold text-gray-900 mb-1">💡 Interactive Graph Tips</p>
                <ul className="text-gray-700 space-y-1">
                  <li>• <strong>Click</strong> nodes to view detailed information</li>
                  <li>• <strong>Drag</strong> nodes to rearrange the layout</li>
                  <li>• <strong>Scroll</strong> to zoom in/out</li>
                  <li>• <strong>Drag canvas</strong> to pan around</li>
                  <li>• Color-coded by entity type</li>
                </ul>
              </div>
            </div>
          </div>
        )}

        <div className="w-full">
          {/* Graph Canvas */}
          <div className="w-full">
            <div 
              className={`relative border-2 border-gray-200 rounded-xl shadow-inner bg-gray-50`}
              style={{ 
                height: isFullscreen ? 'calc(100vh - 12rem)' : '800px',
                width: '100%',
                overflow: 'hidden'
              }}
            >
              {nodes.length === 0 ? (
                <div className="flex items-center justify-center h-full">
                  <div className="text-center text-gray-500">
                    <Network className="h-12 w-12 mx-auto mb-2 text-gray-400" />
                    <p>No entities to display</p>
                    <p className="text-sm">Upload documents to see the knowledge graph</p>
                  </div>
                </div>
              ) : (
                <svg
                  ref={svgRef}
                  style={{
                    width: '100%',
                    height: '100%',
                    background: '#f9fafb'
                  }}
                />
              )}
              
              {/* Legend Panel - Floating on Graph */}
              {showLegend && (
                <div className="absolute top-4 right-4 z-20 w-64">
                  <div className="bg-white rounded-lg shadow-xl border border-gray-200 backdrop-blur-sm bg-opacity-95">
                    <div className="flex items-center justify-between p-3 border-b border-gray-200">
                      <div className="flex items-center space-x-2">
                        <Users className="h-4 w-4 text-gray-700" />
                        <h3 className="text-sm font-bold text-gray-900">Entity Types</h3>
                      </div>
                      <button
                        onClick={() => setShowLegend(false)}
                        className="text-gray-400 hover:text-gray-600 transition"
                        title="Hide legend"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </div>
                    <div className="p-3 space-y-2 max-h-96 overflow-y-auto">
                      {Object.entries(ENTITY_COLORS)
                        .filter(([key]) => !['DEFAULT', 'ORG', 'TECHNOLOGY'].includes(key))
                        .map(([type, color]) => (
                          <div key={type} className="flex items-center space-x-2">
                            <div
                              className="w-3 h-3 rounded-full flex-shrink-0 shadow-sm border border-white"
                              style={{ backgroundColor: color }}
                            />
                            <span className="text-xs font-medium text-gray-700">{type}</span>
                          </div>
                        ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Toggle Legend Button (when hidden) */}
              {!showLegend && (
                <button
                  onClick={() => setShowLegend(true)}
                  className="absolute top-4 right-4 z-20 p-2 bg-white rounded-lg shadow-lg hover:bg-gray-50 transition border border-gray-200"
                  title="Show legend"
                >
                  <Users className="h-5 w-5 text-gray-700" />
                </button>
              )}

              {/* Empty State Message */}
              {!selectedNode && nodes.length > 0 && (
                <div className="absolute top-4 left-4 z-20">
                  <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-3 backdrop-blur-sm bg-opacity-90">
                    <div className="flex items-center space-x-2 text-sm text-gray-600">
                      <Info className="h-4 w-4 text-blue-500" />
                      <span>Click on a node to see details</span>
                    </div>
                  </div>
                </div>
              )}

              {/* Selected Entity Info Box - Floating on Graph */}
              {selectedNode && (
                <div className="absolute top-4 left-4 z-20 w-80">
                  <div className="bg-white rounded-lg shadow-2xl border-2 border-red-500 backdrop-blur-sm bg-opacity-95 p-4">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center space-x-2">
                        <div 
                          className="w-4 h-4 rounded-full border-2 border-white shadow-lg"
                          style={{ backgroundColor: ENTITY_COLORS[selectedNode.labels?.[0] || selectedNode.properties?.type] || ENTITY_COLORS.DEFAULT }}
                        />
                        <h3 className="font-bold text-gray-900 text-lg">
                          {selectedNode.caption || selectedNode.id}
                        </h3>
                      </div>
                      <button
                        onClick={() => setSelectedNode(null)}
                        className="text-gray-400 hover:text-gray-600 transition"
                        title="Close"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </div>
                    
                    <div className="space-y-2 text-sm">
                      <div className="flex items-center space-x-2">
                        <span className="font-semibold text-gray-600">Type:</span>
                        <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs font-medium">
                          {selectedNode.labels?.[0] || selectedNode.properties?.type || 'Unknown'}
                        </span>
                      </div>
                      
                      {selectedNode.properties?.language && (
                        <div className="flex items-center space-x-2">
                          <span className="font-semibold text-gray-600">Language:</span>
                          <span className="text-gray-900">{selectedNode.properties.language.toUpperCase()}</span>
                        </div>
                      )}
                      
                      {selectedNode.properties?.confidence && (
                        <div className="flex items-center space-x-2">
                          <span className="font-semibold text-gray-600">Confidence:</span>
                          <div className="flex-1">
                            <div className="flex items-center space-x-2">
                              <div className="flex-1 bg-gray-200 rounded-full h-2">
                                <div 
                                  className="bg-green-500 h-2 rounded-full transition-all"
                                  style={{ width: `${selectedNode.properties.confidence * 100}%` }}
                                />
                              </div>
                              <span className="text-gray-900 font-medium">
                                {(selectedNode.properties.confidence * 100).toFixed(1)}%
                              </span>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                    
                    <div className="mt-4 pt-3 border-t border-gray-200 flex space-x-2">
                      <button
                        onClick={() => {
                          if (nvlRef.current && selectedNode) {
                            nvlRef.current.zoomToNodes?.([selectedNode.id], { duration: 500, zoomLevel: 1.5 })
                          }
                        }}
                        className="flex-1 px-3 py-2 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 flex items-center justify-center space-x-1 transition"
                      >
                        <Maximize2 className="h-3 w-3" />
                        <span>Center</span>
                      </button>
                      <button
                        onClick={() => setSelectedNode(null)}
                        className="flex-1 px-3 py-2 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition"
                      >
                        Close
                      </button>
                    </div>
                  </div>
                </div>
              )}
              
              {/* Zoom Controls */}
              <div className="absolute bottom-4 right-4 flex flex-col gap-2 z-10">
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
                  title="Fit to view"
                >
                  <Maximize2 className="h-5 w-5 text-gray-700" />
                </button>
              </div>
            </div>
            <p className="text-xs text-gray-500 mt-2 text-center">
              🖱️ Drag nodes • Scroll to zoom • Click to select • Toggle panels with icons
            </p>
          </div>
        </div>
      </div>

      {/* Settings Panel */}
      {showSettings && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-2xl w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
            {/* Header */}
            <div className="sticky top-0 bg-white border-b border-gray-200 p-6 flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <Settings className="h-6 w-6 text-gray-700" />
                <h2 className="text-xl font-bold text-gray-900">Settings</h2>
              </div>
              <button
                onClick={() => setShowSettings(false)}
                className="p-2 hover:bg-gray-100 rounded-lg transition"
                title="Close settings"
              >
                <X className="h-5 w-5 text-gray-500" />
              </button>
            </div>

            {/* Content */}
            <div className="p-6 space-y-6">
              {/* Database Management Section */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                  <Network className="h-5 w-5 mr-2 text-blue-600" />
                  Database Management
                </h3>
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <div className="flex items-start space-x-3">
                    <Trash2 className="h-5 w-5 text-red-600 mt-0.5 flex-shrink-0" />
                    <div className="flex-1">
                      <h4 className="font-semibold text-gray-900 mb-1">Reset All Data</h4>
                      <p className="text-sm text-gray-600 mb-3">
                        Permanently delete all data from Neo4j, Qdrant, BM25 index, chunk store, and in-memory caches. This includes all vectors, entities, relationships, documents, and chunks. This action cannot be undone.
                      </p>
                      <button
                        onClick={() => {
                          setShowSettings(false)
                          setShowResetConfirm(true)
                        }}
                        className="px-4 py-2 text-sm bg-red-600 text-white rounded-lg hover:bg-red-700 flex items-center space-x-2 transition"
                      >
                        <Trash2 className="h-4 w-4" />
                        <span>Reset Database</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              {/* Graph Display Section */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                  <Network className="h-5 w-5 mr-2 text-blue-600" />
                  Graph Display
                </h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div>
                      <p className="font-medium text-gray-900">Show Legend</p>
                      <p className="text-sm text-gray-600">Display entity type legend on graph</p>
                    </div>
                    <button
                      onClick={() => setShowLegend(!showLegend)}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full transition ${
                        showLegend ? 'bg-blue-600' : 'bg-gray-300'
                      }`}
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white transition ${
                          showLegend ? 'translate-x-6' : 'translate-x-1'
                        }`}
                      />
                    </button>
                  </div>
                </div>
              </div>

              {/* Statistics Section */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                  <Info className="h-5 w-5 mr-2 text-blue-600" />
                  Current Statistics
                </h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <p className="text-sm text-gray-600 mb-1">Entities</p>
                    <p className="text-2xl font-bold text-gray-900">{graphData?.stats?.entities || 0}</p>
                  </div>
                  <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                    <p className="text-sm text-gray-600 mb-1">Relationships</p>
                    <p className="text-2xl font-bold text-gray-900">{graphData?.stats?.relationships || 0}</p>
                  </div>
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <p className="text-sm text-gray-600 mb-1">Documents</p>
                    <p className="text-2xl font-bold text-gray-900">{graphData?.stats?.documents || 0}</p>
                  </div>
                  <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
                    <p className="text-sm text-gray-600 mb-1">Chunks</p>
                    <p className="text-2xl font-bold text-gray-900">{graphData?.stats?.chunks || 0}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="sticky bottom-0 bg-gray-50 border-t border-gray-200 p-4">
              <button
                onClick={() => setShowSettings(false)}
                className="w-full px-4 py-2 text-sm bg-gray-700 text-white rounded-lg hover:bg-gray-800 transition"
              >
                Close Settings
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Reset Confirmation Modal */}
      {showResetConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-2xl p-6 max-w-md w-full mx-4">
            <div className="flex items-start space-x-3 mb-4">
              <div className="flex-shrink-0">
                <Trash2 className="h-6 w-6 text-red-600" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-gray-900 mb-2">Reset All Data?</h3>
                <p className="text-sm text-gray-600 mb-2">
                  This will permanently delete:
                </p>
                <ul className="text-sm text-gray-700 space-y-1 ml-4">
                  <li>• All <strong>vectors and chunks</strong> from Qdrant</li>
                  <li>• All <strong>entities and relationships</strong> from Neo4j</li>
                  <li>• All <strong>BM25 index</strong> data (in-memory)</li>
                  <li>• All <strong>persisted chunks</strong> from disk</li>
                  <li>• All <strong>in-memory documents</strong></li>
                </ul>
                <p className="text-sm text-red-600 font-semibold mt-3">
                  ⚠️ This action cannot be undone!
                </p>
              </div>
            </div>
            
            <div className="flex space-x-3">
              <button
                onClick={() => setShowResetConfirm(false)}
                disabled={isResetting}
                className="flex-1 px-4 py-2 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                onClick={handleResetDatabase}
                disabled={isResetting}
                className="flex-1 px-4 py-2 text-sm bg-red-600 text-white rounded-lg hover:bg-red-700 transition disabled:opacity-50 flex items-center justify-center space-x-2"
              >
                {isResetting ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span>Resetting...</span>
                  </>
                ) : (
                  <>
                    <Trash2 className="h-4 w-4" />
                    <span>Reset Everything</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default GraphVisualization

import { useState, useEffect, useRef } from 'react'
import { Network, RefreshCw, Loader2, Info, Users, FileText, Link as LinkIcon, Maximize, ZoomIn, ZoomOut, Maximize2 } from 'lucide-react'
import { InteractiveNvlWrapper } from '@neo4j-nvl/react'
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
  const containerRef = useRef(null)
  const nvlRef = useRef(null)

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
    if (nvlRef.current) {
      const currentZoom = nvlRef.current.getZoom?.() || 1
      nvlRef.current.setZoom?.(currentZoom * 1.2)
    }
  }

  const handleZoomOut = () => {
    if (nvlRef.current) {
      const currentZoom = nvlRef.current.getZoom?.() || 1
      nvlRef.current.setZoom?.(currentZoom / 1.2)
    }
  }

  const handleResetView = () => {
    if (nvlRef.current) {
      nvlRef.current.fit?.()
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
        from: edge.source,
        to: edge.target,
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

  // Mouse event callbacks for NVL
  const mouseEventCallbacks = {
    onNodeClick: (node, hitTargets, evt) => {
      console.log('Node clicked:', node)
      setSelectedNode(node)
      // Zoom to the selected node
      if (nvlRef.current && node) {
        nvlRef.current.zoomToNodes?.([node.id], { duration: 500 })
      }
    },
    onNodeDoubleClick: (node, hitTargets, evt) => {
      console.log('Node double clicked:', node)
      // Double-click to focus and highlight
      if (nvlRef.current && node) {
        nvlRef.current.zoomToNodes?.([node.id], { duration: 300, zoomLevel: 2 })
      }
    },
    onCanvasClick: (evt) => {
      setSelectedNode(null)
    },
    onZoom: (zoomLevel) => {
      console.log('Zoom level:', zoomLevel)
    },
    onPan: (evt) => {
      console.log('Panning')
    },
    onDrag: (nodes) => {
      console.log('Dragging nodes:', nodes.length)
    }
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

  // Update graph when selection changes
  useEffect(() => {
    if (nvlRef.current && selectedNode) {
      // Force graph to re-render with new styles
      nvlRef.current.render?.()
    }
  }, [selectedNode])

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
                <InteractiveNvlWrapper
                  ref={nvlRef}
                  nodes={nodes}
                  rels={relationships}
                  mouseEventCallbacks={mouseEventCallbacks}
                  nvlOptions={{
                    layout: 'force',
                    initialZoom: 0.8,
                    disableWebGL: false,
                    instanceId: 'knowledge-graph',
                    allowDynamicMinZoom: true,
                    maxZoom: 4,
                    minZoom: 0.1
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
    </div>
  )
}

export default GraphVisualization

import { useState, useEffect } from 'react'
import { Upload, FileText, CheckCircle, Loader2, Clock } from 'lucide-react'
import axios from 'axios'

export default function DocumentUpload() {
  const [file, setFile] = useState(null)
  const [language, setLanguage] = useState('en')
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [progress, setProgress] = useState({ stage: '', percent: 0 })
  const [startTime, setStartTime] = useState(null)
  const [elapsedTime, setElapsedTime] = useState(0)
  const [isDragActive, setIsDragActive] = useState(false)

  const handleFileChange = (e) => {
    setFile(e.target.files[0])
    setResult(null)
    setError(null)
  }

  // Timer for elapsed time
  useEffect(() => {
    let interval
    if (uploading && startTime) {
      interval = setInterval(() => {
        setElapsedTime(Date.now() - startTime)
      }, 100)
    }
    return () => clearInterval(interval)
  }, [uploading, startTime])

  const handleDragOver = (event) => {
    event.preventDefault()
    event.stopPropagation()
    if (!uploading) {
      setIsDragActive(true)
    }
  }

  const handleDragLeave = (event) => {
    event.preventDefault()
    event.stopPropagation()
    setIsDragActive(false)
  }

  const handleDrop = (event) => {
    event.preventDefault()
    event.stopPropagation()
    setIsDragActive(false)

    if (uploading) return

    const droppedFiles = event.dataTransfer.files
    if (droppedFiles && droppedFiles.length > 0) {
      setFile(droppedFiles[0])
      setResult(null)
      setError(null)
    }
  }

  const handleUpload = async () => {
    if (!file) return

    setUploading(true)
    setError(null)
    setResult(null)
    setStartTime(Date.now())
    setElapsedTime(0)
    setProgress({ stage: 'Starting...', percent: 0 })

    const formData = new FormData()
    formData.append('file', file)
    formData.append('language', language)

    try {
      // Use fetch with streaming response
      const response = await fetch('/api/ingest/stream', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`)
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        // Decode chunk and add to buffer
        buffer += decoder.decode(value, { stream: true })
        
        // Split by newlines to get complete SSE messages
        const lines = buffer.split('\n')
        
        // Keep the last incomplete line in the buffer
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.substring(6))
              
              if (data.error) {
                throw new Error(data.error)
              } else if (data.result) {
                // Final result received
                setResult(data.result)
                setFile(null)
              } else if (data.message && data.percent !== undefined) {
                // Progress update
                setProgress({
                  stage: data.message,
                  percent: data.percent
                })
              }
            } catch (parseErr) {
              console.warn('Failed to parse SSE data:', line, parseErr)
            }
          }
        }
      }
    } catch (err) {
      console.error('Upload error:', err)
      setError(err.message || 'Upload failed')
    } finally {
      setUploading(false)
      setStartTime(null)
    }
  }

  return (
    <div className="max-w-3xl mx-auto">
      <div className="bg-white rounded-lg shadow-sm border p-8">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
            <Upload className="h-8 w-8 text-blue-600" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900">
            Upload Document
          </h2>
          <p className="mt-2 text-gray-600">
            Add documents to the hybrid RAG system
          </p>
        </div>

        {/* File Upload Area */}
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select File
            </label>
            <div
              className={`mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-dashed rounded-lg transition-colors ${
                isDragActive
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-300 hover:border-gray-400'
              }`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              <div className="space-y-1 text-center">
                <FileText className="mx-auto h-12 w-12 text-gray-400" />
                <div className="flex text-sm text-gray-600">
                  <label className="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500">
                    <span>Upload a file</span>
                    <input
                      type="file"
                      className="sr-only"
                      onChange={handleFileChange}
                      accept=".txt,.pdf,.docx"
                    />
                  </label>
                  <p className="pl-1">or drag and drop</p>
                </div>
                <p className="text-xs text-gray-500">
                  TXT, PDF, DOCX up to 10MB
                </p>
              </div>
            </div>
            {file && (
              <div className="mt-2 flex items-center text-sm text-gray-600">
                <FileText className="h-4 w-4 mr-2" />
                {file.name}
              </div>
            )}
          </div>

          {/* Language Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Document Language
            </label>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
            >
              <option value="en">English</option>
              <option value="ar">Arabic (العربية)</option>
              <option value="es">Spanish (Español)</option>
            </select>
          </div>

          {/* Upload Button */}
          <button
            onClick={handleUpload}
            disabled={!file || uploading}
            className="w-full flex justify-center items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {uploading ? (
              <>
                <Loader2 className="animate-spin h-4 w-4 mr-2" />
                Processing...
              </>
            ) : (
              <>
                <Upload className="h-4 w-4 mr-2" />
                Upload & Process
              </>
            )}
          </button>
        </div>

        {/* Progress Bar */}
        {uploading && (
          <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <Loader2 className="animate-spin h-4 w-4 text-blue-600 mr-2" />
                  <span className="text-sm font-medium text-blue-900">{progress.stage}</span>
                </div>
                <div className="flex items-center text-xs text-blue-600">
                  <Clock className="h-3 w-3 mr-1" />
                  {(elapsedTime / 1000).toFixed(1)}s
                </div>
              </div>
              
              {/* Progress bar */}
              <div className="w-full bg-blue-100 rounded-full h-2.5">
                <div
                  className="bg-blue-600 h-2.5 rounded-full transition-all duration-300 ease-out"
                  style={{ width: `${progress.percent}%` }}
                ></div>
              </div>
              
              <div className="flex justify-between text-xs text-blue-700">
                <span>{progress.percent}% complete</span>
                <span>Please wait...</span>
              </div>
            </div>
          </div>
        )}

        {/* Success Message */}
        {result && (
          <div className="mt-6 bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-start">
              <CheckCircle className="h-5 w-5 text-green-400 mt-0.5" />
              <div className="ml-3">
                <h3 className="text-sm font-medium text-green-800">
                  Document Processed Successfully
                </h3>
                <div className="mt-2 text-sm text-green-700">
                  <ul className="list-disc list-inside space-y-1">
                    <li>Document ID: {result.document_id}</li>
                    <li>Chunks created: {result.chunks_created}</li>
                    <li>Entities extracted: {result.entities_extracted}</li>
                    <li>Processing time: {result.processing_time_ms.toFixed(2)}ms</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="mt-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex">
              <div className="text-sm text-red-700">{error}</div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

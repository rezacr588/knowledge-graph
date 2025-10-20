import { useState } from 'react'
import { Upload, FileText, CheckCircle, Loader2 } from 'lucide-react'
import axios from 'axios'

export default function DocumentUpload() {
  const [file, setFile] = useState(null)
  const [language, setLanguage] = useState('en')
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleFileChange = (e) => {
    setFile(e.target.files[0])
    setResult(null)
    setError(null)
  }

  const handleUpload = async () => {
    if (!file) return

    setUploading(true)
    setError(null)
    setResult(null)

    const formData = new FormData()
    formData.append('file', file)
    formData.append('language', language)

    try {
      const response = await axios.post('/api/ingest', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      setResult(response.data)
      setFile(null)
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed')
    } finally {
      setUploading(false)
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
            <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-lg hover:border-gray-400 transition-colors">
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

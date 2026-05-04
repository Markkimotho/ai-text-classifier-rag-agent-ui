import { useState, useEffect, useCallback } from 'react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export function useDocuments() {
  const [documents, setDocuments] = useState([])
  const [uploading, setUploading] = useState(false)
  const [uploadError, setUploadError] = useState(null)
  const [uploadSuccess, setUploadSuccess] = useState(null)

  const fetchDocuments = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/documents`)
      const data = await res.json()
      setDocuments(data.documents)
    } catch {
      // silently ignore fetch errors for the polling case
    }
  }, [])

  useEffect(() => {
    fetchDocuments()
  }, [fetchDocuments])

  const uploadFile = useCallback(async (file) => {
    setUploading(true)
    setUploadError(null)
    setUploadSuccess(null)

    const form = new FormData()
    form.append('file', file)

    try {
      const res = await fetch(`${API_URL}/upload`, { method: 'POST', body: form })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'Upload failed')
      }
      const data = await res.json()
      setUploadSuccess(`${data.filename} uploaded (${data.chunks_stored} chunks)`)
      await fetchDocuments()
    } catch (e) {
      setUploadError(e.message)
    } finally {
      setUploading(false)
    }
  }, [fetchDocuments])

  const clearToast = useCallback(() => {
    setUploadError(null)
    setUploadSuccess(null)
  }, [])

  return { documents, uploading, uploadError, uploadSuccess, uploadFile, clearToast }
}

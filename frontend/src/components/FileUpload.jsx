import { useRef, useEffect } from 'react'

export default function FileUpload({ onUpload, uploading, error, success, onClearToast }) {
  const inputRef = useRef(null)

  useEffect(() => {
    if (!error && !success) return
    const t = setTimeout(onClearToast, 4000)
    return () => clearTimeout(t)
  }, [error, success, onClearToast])

  const handleChange = (e) => {
    const file = e.target.files?.[0]
    if (file) {
      onUpload(file)
      e.target.value = ''
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    const file = e.dataTransfer.files?.[0]
    if (file) onUpload(file)
  }

  return (
    <div className="p-3 border-b border-gray-100">
      <div
        onDrop={handleDrop}
        onDragOver={e => e.preventDefault()}
        onClick={() => inputRef.current?.click()}
        className="border-2 border-dashed border-gray-200 hover:border-blue-300 rounded-xl p-4 text-center cursor-pointer transition"
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.txt"
          onChange={handleChange}
          className="hidden"
        />
        <p className="text-xs text-gray-400">
          {uploading ? 'Uploading...' : 'Click or drag .pdf / .txt'}
        </p>
      </div>

      {success && (
        <p className="mt-2 text-xs text-green-600 bg-green-50 rounded-lg px-3 py-1.5">
          {success}
        </p>
      )}
      {error && (
        <p className="mt-2 text-xs text-red-600 bg-red-50 rounded-lg px-3 py-1.5">
          {error}
        </p>
      )}
    </div>
  )
}

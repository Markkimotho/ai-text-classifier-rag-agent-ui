import FileUpload from './FileUpload'

export default function DocumentsSidebar({ documents, uploading, uploadError, uploadSuccess, onUpload, onClearToast }) {
  return (
    <aside className="w-64 shrink-0 bg-white border-r border-gray-200 flex flex-col">
      <div className="px-4 py-3 border-b border-gray-100">
        <h2 className="text-sm font-semibold text-gray-700">Documents</h2>
      </div>

      <FileUpload
        onUpload={onUpload}
        uploading={uploading}
        error={uploadError}
        success={uploadSuccess}
        onClearToast={onClearToast}
      />

      <div className="flex-1 overflow-y-auto p-3">
        {documents.length === 0 ? (
          <p className="text-xs text-gray-400 text-center mt-4">No documents uploaded yet.</p>
        ) : (
          <ul className="space-y-1">
            {documents.map((doc, i) => (
              <li
                key={i}
                className="text-xs text-gray-600 bg-gray-50 rounded-lg px-3 py-2 flex items-center gap-2 truncate"
                title={doc}
              >
                <span className="shrink-0 text-gray-400">
                  {doc.endsWith('.pdf') ? '📄' : '📝'}
                </span>
                <span className="truncate">{doc}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </aside>
  )
}

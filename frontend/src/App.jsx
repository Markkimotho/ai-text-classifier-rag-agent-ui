import ChatWindow from './components/ChatWindow'
import InputBox from './components/InputBox'
import DocumentsSidebar from './components/DocumentsSidebar'
import { useChat } from './hooks/useChat'
import { useDocuments } from './hooks/useDocuments'

export default function App() {
  const { messages, loading, sendMessage } = useChat()
  const { documents, uploading, uploadError, uploadSuccess, uploadFile, clearToast } = useDocuments()

  return (
    <div className="flex h-screen bg-slate-100">
      <DocumentsSidebar
        documents={documents}
        uploading={uploading}
        uploadError={uploadError}
        uploadSuccess={uploadSuccess}
        onUpload={uploadFile}
        onClearToast={clearToast}
      />

      <main className="flex-1 flex flex-col min-w-0">
        <header className="bg-white border-b border-gray-200 px-6 py-3 flex items-center gap-3">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <span className="text-white text-xs font-bold">AI</span>
          </div>
          <div>
            <h1 className="text-sm font-semibold text-gray-900">AI Document Assistant</h1>
            <p className="text-xs text-gray-400">Powered by RAG + LangChain</p>
          </div>
        </header>

        <ChatWindow messages={messages} loading={loading} />
        <InputBox onSend={sendMessage} disabled={loading} />
      </main>
    </div>
  )
}

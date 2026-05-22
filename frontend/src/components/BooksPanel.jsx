import { useStore } from '../store/store';

export default function BooksPanel() {
  const { books, booksLoading, indexingProgress, isIndexing, fetchBooksStatus, indexBooks } = useStore()

  const handleIndex = () => {
    indexBooks().then(() => fetchBooksStatus())
  }

  return (
    <div className="card space-y-4 relative overflow-hidden">
      {/* Top accent line */}
      <div className="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-transparent via-emerald-500/30 to-transparent rounded-full" />
      
      {/* Ambient background glow */}
      <div className="absolute -right-20 -top-20 w-64 h-64 bg-emerald-500/[0.03] rounded-full blur-3xl pointer-events-none" />
      
      <div className="flex items-center justify-between relative z-10">
        <h3 className="section-title !mb-0">Biblioteca RAG</h3>
        <button
          onClick={handleIndex}
          disabled={isIndexing || indexingProgress > 0}
          className="btn btn-ghost text-[10px] px-3 py-1.5 flex items-center gap-2 relative overflow-hidden group"
        >
          🔄 {isIndexing ? 'Indexando...' : 'Reindexar'}
          <div className="absolute inset-0 bg-emerald-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
        </button>
      </div>

      {booksLoading ? (
        <div className="space-y-2 relative z-10">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="h-12 bg-neutral-800/50 rounded-xl shimmer" />
          ))}
        </div>
      ) : books.length === 0 ? (
        <div className="text-center py-6 relative z-10">
          <div className="w-12 h-12 rounded-xl bg-neutral-800/50 flex items-center justify-center text-xl mx-auto mb-3">📚</div>
          <p className="text-xs text-neutral-500 leading-relaxed">No hay libros indexados.</p>
        </div>
      ) : (
        <div className="space-y-2 relative z-10 stagger">
          {books.map((book, index) => (
            <div 
              key={book.filename} 
              className="group flex items-center gap-3 p-3 rounded-xl bg-white/[0.02] border border-white/[0.06] hover:border-emerald-500/20 hover:bg-white/[0.03] transition-all duration-300 hover:translate-x-1 cursor-default"
              style={{ animationDelay: `${index * 0.05}s` }}
            >
              {/* Hover gradient overlay */}
              <div className="absolute inset-0 bg-gradient-to-r from-emerald-500/[0.02] to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />
              <span className="text-base shrink-0 relative z-10 group-hover:scale-110 transition-transform duration-300">📖</span>
              <div className="flex-1 min-w-0 relative z-10">
                <p className="text-sm text-neutral-300 truncate font-medium group-hover:text-white transition-colors duration-300">{book.filename}</p>
                <p className="text-[10px] text-neutral-600 group-hover:text-neutral-500 transition-colors duration-300">{book.chunks} fragmentos</p>
              </div>
            </div>
          ))}
        </div>
      )}

      {indexingProgress > 0 && indexingProgress < 100 && (
        <div className="pt-2 relative z-10">
          <div className="flex items-center justify-between text-[10px] text-neutral-500 mb-2">
            <span>Progreso</span>
            <span>{indexingProgress}%</span>
          </div>
          <div className="w-full bg-neutral-800 rounded-full h-1.5 overflow-hidden">
            <div
              className="bg-gradient-to-r from-green-500 to-emerald-500 h-full transition-all duration-500 ease-out rounded-full relative"
              style={{ width: `${indexingProgress}%` }}
            >
              {/* Progress shimmer */}
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent" style={{ animation: 'shimmer 2s infinite', backgroundSize: '200% 100%' }} />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

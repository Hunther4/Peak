import { useState } from 'react'
import { useStore } from '../store/store'
import { Modal } from './ui'

export default function ProfileAvatar() {
  const { profile, saveProfile } = useStore()
  const [showMenu, setShowMenu] = useState(false)
  const [editing, setEditing] = useState(false)
  const [name, setName] = useState('')
  const [age, setAge] = useState('')

  if (!profile) return null

  const initial = profile.name?.charAt(0).toUpperCase() || '?'

  const handleEdit = () => {
    setName(profile.name)
    setAge(String(profile.age))
    setEditing(true)
    setShowMenu(false)
  }

  const handleSave = async () => {
    await saveProfile(name.trim(), parseInt(age, 10))
    setEditing(false)
  }

  return (
    <div className="relative">
      <button
        onClick={() => setShowMenu(!showMenu)}
        className="w-9 h-9 rounded-full bg-gradient-to-br from-green-400 to-emerald-600 flex items-center justify-center text-black font-bold text-sm shadow-lg shadow-green-500/20 hover:shadow-green-500/40 transition-all duration-300 hover:scale-105"
        title={profile.name}
      >
        {initial}
      </button>

      {/* Dropdown menu */}
      {showMenu && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setShowMenu(false)} />
          <div className="absolute right-0 top-full mt-2 z-50 min-w-[160px] bg-neutral-900 border border-white/[0.08] rounded-xl p-2 shadow-2xl" style={{ animation: 'fadeInUp 0.15s ease-out' }}>
            <div className="px-3 py-2 text-sm text-neutral-300 border-b border-white/[0.06] mb-1">
              {profile.name} · {profile.age} años
            </div>
            <button
              onClick={handleEdit}
              className="w-full text-left px-3 py-2 text-sm text-neutral-400 hover:text-white hover:bg-white/[0.04] rounded-lg transition-colors"
            >
              Editar perfil
            </button>
          </div>
        </>
      )}

      {/* Edit modal */}
      {editing && (
        <Modal
          isOpen={editing}
          onClose={() => setEditing(false)}
          title="Editar perfil"
          onConfirm={handleSave}
          confirmText="Guardar"
        >
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-neutral-400 mb-1">Nombre</label>
              <input
                type="text"
                value={name}
                onChange={e => setName(e.target.value)}
                className="input"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-neutral-400 mb-1">Edad</label>
              <input
                type="number"
                value={age}
                onChange={e => setAge(e.target.value)}
                className="input"
                min={1}
                max={150}
                required
              />
            </div>
          </div>
        </Modal>
      )}
    </div>
  )
}

import { useState } from 'react'
import { useStore } from '../store/store'
import { Modal } from './ui'

export default function ProfileAvatar() {
  const { profile, saveProfile } = useStore()
  const [showProfile, setShowProfile] = useState(false)
  const [editing, setEditing] = useState(false)
  const [name, setName] = useState('')
  const [age, setAge] = useState('')

  if (!profile) return null

  const initial = profile.name?.charAt(0).toUpperCase() || '?'

  const openEdit = () => {
    setName(profile.name)
    setAge(String(profile.age))
    setEditing(true)
    setShowProfile(false)
  }

  const handleSave = async () => {
    await saveProfile(name.trim(), parseInt(age, 10))
    setEditing(false)
  }

  return (
    <>
      {/* Avatar button — far right corner */}
      <button
        onClick={() => setShowProfile(true)}
        className="w-9 h-9 rounded-full bg-gradient-to-br from-green-400 to-emerald-600 flex items-center justify-center text-black font-bold text-sm shadow-lg shadow-green-500/20 hover:shadow-green-500/40 hover:scale-105 transition-all duration-300 shrink-0"
        title={profile.name}
      >
        {initial}
      </button>

      {/* Profile modal — centered */}
      <Modal
        isOpen={showProfile}
        onClose={() => setShowProfile(false)}
        title={profile.name}
      >
        <div className="space-y-6">
          {/* Avatar grande */}
          <div className="flex justify-center">
            <div className="w-20 h-20 rounded-full bg-gradient-to-br from-green-400 to-emerald-600 flex items-center justify-center text-black font-black text-3xl shadow-xl shadow-green-500/30">
              {initial}
            </div>
          </div>

          {/* Info */}
          <div className="text-center">
            <p className="text-lg font-bold text-white">{profile.name}</p>
            <p className="text-sm text-neutral-400">{profile.age} años</p>
          </div>

          {/* Edit button */}
          <button
            onClick={openEdit}
            className="btn btn-ghost w-full text-xs"
          >
            Editar perfil
          </button>
        </div>
      </Modal>

      {/* Edit modal */}
      <Modal
        isOpen={editing}
        onClose={() => setEditing(false)}
        title="Editar perfil"
        onConfirm={handleSave}
        confirmText="Guardar"
      >
        <div className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-neutral-400 mb-1 uppercase tracking-wider">
              Nombre
            </label>
            <input
              type="text"
              value={name}
              onChange={e => setName(e.target.value)}
              className="input"
              required
              autoFocus
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-neutral-400 mb-1 uppercase tracking-wider">
              Edad
            </label>
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
    </>
  )
}

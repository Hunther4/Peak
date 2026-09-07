import { useState, useRef } from 'react'
import { useStore } from '../store/store'
import { Modal } from './ui'

export default function ProfileAvatar() {
  const { profile, saveProfile, uploadAvatar } = useStore()
  const [showProfile, setShowProfile] = useState(false)
  const [editing, setEditing] = useState(false)
  const [name, setName] = useState('')
  const [age, setAge] = useState('')
  const [avatarFile, setAvatarFile] = useState(null)
  const [avatarPreview, setAvatarPreview] = useState(null)
  const [uploading, setUploading] = useState(false)
  const fileInputRef = useRef(null)

  if (!profile) return null

  const initial = profile.name?.charAt(0).toUpperCase() || '?'
  const apiBase = (import.meta.env.VITE_API_URL || "http://localhost:8000/api").replace(/\/api\/?$/, '')
  const avatarSrc = profile.avatar_url ? `${apiBase}${profile.avatar_url}` : null

  const openEdit = () => {
    setName(profile.name)
    setAge(String(profile.age))
    setAvatarFile(null)
    setAvatarPreview(null)
    setEditing(true)
    setShowProfile(false)
  }

  const handleFileSelect = (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    setAvatarFile(file)
    const reader = new FileReader()
    reader.onload = (ev) => setAvatarPreview(ev.target.result)
    reader.readAsDataURL(file)
  }

  const handleUpload = async () => {
    if (!avatarFile) return
    setUploading(true)
    try {
      await uploadAvatar(avatarFile)
      setAvatarFile(null)
      setAvatarPreview(null)
      setEditing(false)
    } catch (e) {
      console.error("Upload failed:", e)
    } finally {
      setUploading(false)
    }
  }

  const handleSave = async () => {
    await saveProfile(name.trim(), parseInt(age, 10))
    setEditing(false)
  }

  return (
    <>
      {/* Avatar button — far right corner */}
      <div className="flex items-center py-2.5">
        <button
          onClick={() => setShowProfile(true)}
          className="w-9 h-9 rounded-full bg-gradient-to-br from-green-400 to-emerald-600 flex items-center justify-center text-black font-bold text-sm shadow-lg shadow-green-500/20 hover:shadow-green-500/40 hover:scale-105 transition-all duration-300 shrink-0 overflow-hidden"
          title={profile.name}
        >
          {avatarSrc ? (
            <img src={avatarSrc} alt={profile.name} className="w-full h-full object-cover" />
          ) : (
            initial
          )}
        </button>
      </div>

      {/* Profile modal — centered */}
      <Modal
        isOpen={showProfile}
        onClose={() => setShowProfile(false)}
        title={profile.name}
      >
        <div className="space-y-6">
          {/* Avatar grande */}
          <div className="flex justify-center">
            <div className="w-20 h-20 rounded-full bg-gradient-to-br from-green-400 to-emerald-600 flex items-center justify-center text-black font-black text-3xl shadow-xl shadow-green-500/30 overflow-hidden">
              {avatarSrc ? (
                <img src={avatarSrc} alt={profile.name} className="w-full h-full object-cover" />
              ) : (
                initial
              )}
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

          <div>
            <label className="block text-xs font-medium text-neutral-400 mb-1 uppercase tracking-wider">
              Avatar
            </label>
            <div className="flex items-center gap-3">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-green-400 to-emerald-600 flex items-center justify-center text-black font-black text-xl shrink-0 overflow-hidden">
                {avatarPreview ? (
                  <img src={avatarPreview} alt="Preview" className="w-full h-full object-cover" />
                ) : avatarSrc ? (
                  <img src={avatarSrc} alt={profile.name} className="w-full h-full object-cover" />
                ) : (
                  initial
                )}
              </div>
              <div className="flex flex-col gap-2">
                <input
                  type="file"
                  ref={fileInputRef}
                  accept="image/*"
                  onChange={handleFileSelect}
                  className="hidden"
                />
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="btn btn-ghost text-xs"
                  disabled={uploading}
                >
                  {avatarFile ? 'Cambiar archivo' : 'Seleccionar imagen'}
                </button>
                {avatarFile && (
                  <button
                    onClick={handleUpload}
                    className="btn btn-primary text-xs"
                    disabled={uploading}
                  >
                    {uploading ? 'Subiendo...' : 'Subir avatar'}
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      </Modal>
    </>
  )
}

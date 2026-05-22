import { useState } from 'react';
import { useStore } from '../store/store';
import { useToast, Spinner } from './ui';

const DURATION_PRESETS = [15, 25, 45, 60, 90];

export default function SessionForm() {
  const { skills, createSession, loading } = useStore();
  const toast = useToast();
  const [entryMode, setEntryMode] = useState('quick');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isFocused, setIsFocused] = useState(null);
  const [formData, setFormData] = useState({
    skill_id: '',
    duration_minutes: 45,
    what_i_practiced: '',
    difficulty: 3,
    micro_error_found: '',
    correction_applied: '',
    hypothesis_tomorrow: '',
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      if (!formData.skill_id) {
        toast.warning('Elegí una skill antes de guardar.');
        return;
      }
      if (!formData.what_i_practiced.trim()) {
        toast.warning('¿Qué practicaste? No puede estar vacío.');
        return;
      }
      if (!formData.micro_error_found.trim()) {
        toast.warning('¿Qué micro-error encontraste? Es obligatorio.');
        return;
      }

      const payload = {
        skill_id: parseInt(formData.skill_id),
        duration_minutes: formData.duration_minutes,
        what_i_practiced: formData.what_i_practiced.trim(),
        micro_error_found: formData.micro_error_found.trim(),
        difficulty: formData.difficulty,
        entry_mode: entryMode,
      };

      if (entryMode === 'full') {
        const missing = [];
        if (!formData.correction_applied.trim()) missing.push('corrección aplicada');
        if (!formData.hypothesis_tomorrow.trim()) missing.push('hipótesis para mañana');
        if (missing.length) {
          toast.warning(`Completá: ${missing.join(' y ')}.`);
          return;
        }
        payload.correction_applied = formData.correction_applied;
        payload.hypothesis_tomorrow = formData.hypothesis_tomorrow;
      }

      await createSession(payload);
      toast.success('Sesión registrada. La IA está auditando...');
      setFormData(prev => ({
        ...prev,
        what_i_practiced: '',
        micro_error_found: '',
        correction_applied: '',
        hypothesis_tomorrow: '',
        difficulty: 3,
      }));
    } catch (err) {
      toast.error('Error: ' + err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const difficultyLabels = ['Trivial', 'Fácil', 'Medio', 'Difícil', 'Límite'];
  const difficultyColors = [
    'text-blue-400 border-blue-500/30 bg-blue-500/10',
    'text-cyan-400 border-cyan-500/30 bg-cyan-500/10',
    'text-yellow-400 border-yellow-500/30 bg-yellow-500/10',
    'text-orange-400 border-orange-500/30 bg-orange-500/10',
    'text-red-400 border-red-500/30 bg-red-500/10',
  ];

  return (
    <form onSubmit={handleSubmit} className="card space-y-6">
      {/* Animated border glow effect */}
      <div className="absolute inset-0 rounded-2xl overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-transparent via-green-500/30 to-transparent" />
        <div className="absolute bottom-0 left-0 w-full h-[2px] bg-gradient-to-r from-transparent via-green-500/10 to-transparent" />
      </div>

      {/* Mode Selector */}
      <div className="relative p-4 bg-white/[0.02] rounded-xl border border-white/[0.06] transition-all duration-300 hover:bg-white/[0.03] hover:border-white/[0.08]">
        <div className="flex items-center justify-between">
          <div className="flex bg-white/[0.04] rounded-xl p-1 border border-white/[0.06]">
            <button
              type="button"
              onClick={() => setEntryMode('quick')}
              className={`px-4 py-2.5 text-xs font-bold uppercase tracking-wider rounded-lg transition-all duration-300 relative overflow-hidden ${
                entryMode === 'quick'
                  ? 'bg-gradient-to-r from-green-500 to-emerald-500 text-black shadow-lg shadow-green-500/20'
                  : 'text-neutral-500 hover:text-neutral-300'
              }`}
            >
              ⚡ Rápido
            </button>
            <button
              type="button"
              onClick={() => setEntryMode('full')}
              className={`px-4 py-2.5 text-xs font-bold uppercase tracking-wider rounded-lg transition-all duration-300 relative overflow-hidden ${
                entryMode === 'full'
                  ? 'bg-gradient-to-r from-green-500 to-emerald-500 text-black shadow-lg shadow-green-500/20'
                  : 'text-neutral-500 hover:text-neutral-300'
              }`}
            >
              📋 Completo
            </button>
          </div>
          <div className="text-right">
            <span className="text-[10px] text-neutral-500 uppercase tracking-wider transition-colors duration-300 hover:text-neutral-400">
              {entryMode === 'quick' ? '🤖 IA completa' : '✍️ Manual'}
            </span>
          </div>
        </div>
      </div>

      {/* Skill + Duration */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="space-y-2">
          <label className="text-[10px] text-neutral-400 uppercase tracking-[0.15em] font-bold">Skill</label>
          <select
            className="input"
            value={formData.skill_id}
            onChange={e => setFormData({...formData, skill_id: e.target.value})}
            onFocus={() => setIsFocused('skill')}
            onBlur={() => setIsFocused(null)}
            required
          >
            <option value="">Seleccionar...</option>
            {skills?.map(s => (
              <option key={s.id} value={s.id}>{s.name}</option>
            ))}
          </select>
        </div>

        <div className="space-y-2">
          <label className="text-[10px] text-neutral-400 uppercase tracking-[0.15em] font-bold">Duración</label>
          <div className="flex gap-1.5">
            {DURATION_PRESETS.map(m => (
              <button
                key={m}
                type="button"
                onClick={() => setFormData({...formData, duration_minutes: m})}
                className={`flex-1 py-2.5 text-xs font-bold rounded-lg border transition-all duration-300 hover:scale-105 active:scale-95 ${
                  formData.duration_minutes === m
                    ? 'bg-green-500/15 text-green-400 border-green-500/30 shadow-sm shadow-green-500/10'
                    : 'bg-white/[0.02] text-neutral-500 border-white/[0.06] hover:border-white/[0.12] hover:text-neutral-300'
                }`}
              >
                {m}′
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* What I Practiced + Micro-error */}
      <div className="relative space-y-4 p-4 bg-white/[0.02] rounded-xl border border-white/[0.04] transition-all duration-300 hover:bg-white/[0.03] hover:border-white/[0.06]">
        {/* Top accent line */}
        <div className="absolute top-0 left-4 right-4 h-[2px] bg-gradient-to-r from-transparent via-green-500/20 to-transparent rounded-full" />
        
        <div className="flex items-center gap-2 mb-2">
          <span className="text-sm">🎯</span>
          <h3 className="text-xs font-bold text-neutral-300 uppercase tracking-wider">Detalle de Práctica</h3>
        </div>
        <div className="space-y-2">
          <label className="text-[10px] text-neutral-500 uppercase tracking-[0.15em] font-bold">
            ¿Qué practicaste exactamente?
          </label>
          <input
            type="text"
            className="input"
            placeholder="Ej: Transición del compás 12 al 15 mano izquierda"
            value={formData.what_i_practiced}
            onChange={e => setFormData({...formData, what_i_practiced: e.target.value})}
            onFocus={() => setIsFocused('practice')}
            onBlur={() => setIsFocused(null)}
            required
          />
        </div>

        <div className="space-y-2">
          <label className="text-[10px] text-neutral-500 uppercase tracking-[0.15em] font-bold">
            Micro-error detectado
          </label>
          <input
            type="text"
            className="input"
            placeholder="Ej: El pulgar llegaba tarde a la nota sol"
            value={formData.micro_error_found}
            onChange={e => setFormData({...formData, micro_error_found: e.target.value})}
            onFocus={() => setIsFocused('error')}
            onBlur={() => setIsFocused(null)}
            required
          />
        </div>
      </div>

      {/* Difficulty */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <label className="text-[10px] text-neutral-500 uppercase tracking-[0.15em] font-bold">Dificultad</label>
          <span className={`text-xs font-bold px-2.5 py-1 rounded-md transition-all duration-300 ${difficultyColors[formData.difficulty - 1]}`}>
            {difficultyLabels[formData.difficulty - 1]}
          </span>
        </div>
        <div className="flex gap-2">
          {[1, 2, 3, 4, 5].map(n => (
            <button
              key={n}
              type="button"
              onClick={() => setFormData({...formData, difficulty: n})}
              className={`flex-1 py-3 text-sm font-bold rounded-xl border transition-all duration-300 hover:scale-105 active:scale-95 ${
                formData.difficulty === n
                  ? difficultyColors[n - 1]
                  : 'bg-white/[0.02] text-neutral-600 border-white/[0.06] hover:border-white/[0.12] hover:text-neutral-400'
              }`}
            >
              {n}
            </button>
          ))}
        </div>
      </div>

      {/* Full Mode Fields */}
      {entryMode === 'full' && (
        <div className="space-y-4 pt-4 border-t border-white/[0.06]" style={{ animation: 'fadeInUp 0.3s ease-out' }}>
          <div className="flex items-center gap-2 mb-3">
            <span className="text-sm">📝</span>
            <h3 className="text-xs font-bold text-neutral-300 uppercase tracking-wider">Análisis Post-Sesión</h3>
          </div>
          <div className="space-y-2">
            <label className="text-[10px] text-neutral-500 uppercase tracking-[0.15em] font-bold">
              Corrección aplicada
            </label>
            <textarea
              className="input min-h-[80px] resize-none"
              placeholder="¿Cómo corregiste ese error en el momento?"
              value={formData.correction_applied}
              onChange={e => setFormData({...formData, correction_applied: e.target.value})}
              onFocus={() => setIsFocused('correction')}
              onBlur={() => setIsFocused(null)}
              required
            />
          </div>

          <div className="space-y-2">
            <label className="text-[10px] text-neutral-500 uppercase tracking-[0.15em] font-bold">
              Hipótesis para mañana
            </label>
            <textarea
              className="input min-h-[80px] resize-none"
              placeholder="¿Qué vas a probar en la próxima sesión?"
              value={formData.hypothesis_tomorrow}
              onChange={e => setFormData({...formData, hypothesis_tomorrow: e.target.value})}
              onFocus={() => setIsFocused('hypothesis')}
              onBlur={() => setIsFocused(null)}
              required
            />
          </div>
        </div>
      )}

      {/* Submit */}
      <button
        type="submit"
        disabled={loading || isSubmitting}
        className="btn btn-primary w-full flex justify-center items-center h-14 text-sm font-bold rounded-xl transition-all duration-300 hover:shadow-green-500/40 hover:-translate-y-0.5 active:translate-y-0"
      >
        {isSubmitting ? (
          <Spinner size="md" className="!border-black/30 !border-t-black" />
        ) : (
          <span className="flex items-center gap-2">
            {entryMode === 'quick' ? '⚡ Guardar · IA completa' : '📋 Guardar y Auditar'}
          </span>
        )}
      </button>
    </form>
  );
}

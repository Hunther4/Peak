import { useState } from 'react';
import { useStore } from '../store/store';
import { useToast, Spinner } from './ui';

const DURATION_PRESETS = [15, 25, 45, 60, 90];

export default function SessionForm() {
  const { skills, createSession, loading } = useStore();
  const toast = useToast();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showDetail, setShowDetail] = useState(false);
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

      const payload = {
        skill_id: parseInt(formData.skill_id),
        duration_minutes: formData.duration_minutes,
        what_i_practiced: formData.what_i_practiced.trim() || 'Práctica general',
        difficulty: formData.difficulty,
        entry_mode: 'quick',
      };

      if (formData.micro_error_found.trim()) {
        payload.micro_error_found = formData.micro_error_found.trim();
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
    <form onSubmit={handleSubmit} className="card p-5 space-y-3">
      <h2 className="text-sm font-bold text-white/90 tracking-tight mb-2">Nueva sesión</h2>
      {/* Skill + Duration — row */}
      <div className="flex items-stretch gap-2">
        <div className="flex-1">
          <select
            className="input h-11 text-sm"
            value={formData.skill_id}
            onChange={e => setFormData({...formData, skill_id: e.target.value})}
            required
          >
            <option value="">Skill</option>
            {skills?.map(s => (
              <option key={s.id} value={s.id}>{s.name}</option>
            ))}
          </select>
        </div>
        <div className="flex gap-1">
          {DURATION_PRESETS.map(m => (
            <button
              key={m}
              type="button"
              onClick={() => setFormData({...formData, duration_minutes: m})}
              className={`h-11 px-3 text-xs font-bold rounded-lg border transition-all ${
                formData.duration_minutes === m
                  ? 'bg-green-500/15 text-green-400 border-green-500/30'
                  : 'bg-white/[0.02] text-neutral-500 border-white/[0.06] hover:border-white/[0.12] hover:text-neutral-300'
              }`}
            >
              {m}′
            </button>
          ))}
        </div>
      </div>

      {/* Difficulty — inline */}
      <div className="flex gap-1.5">
        {[1, 2, 3, 4, 5].map(n => (
          <button
            key={n}
            type="button"
            onClick={() => setFormData({...formData, difficulty: n})}
            className={`flex-1 h-9 text-xs font-bold rounded-lg border transition-all ${
              formData.difficulty === n
                ? difficultyColors[n - 1]
                : 'bg-white/[0.02] text-neutral-600 border-white/[0.06] hover:text-neutral-400'
            }`}
          >
            {n} {difficultyLabels[n - 1]}
          </button>
        ))}
      </div>

      {/* Detail toggle */}
      <button
        type="button"
        onClick={() => setShowDetail(!showDetail)}
        className="w-full flex items-center justify-center gap-1.5 py-2 text-[11px] text-neutral-500 hover:text-neutral-300 transition-colors uppercase tracking-wider"
      >
        <span className={`transition-transform ${showDetail ? 'rotate-180' : ''}`}>▾</span>
        {showDetail ? 'Ocultar detalle' : 'Agregar detalle'}
      </button>

      {/* Optional detail fields */}
      {showDetail && (
        <div className="space-y-2 p-3 bg-white/[0.02] rounded-xl border border-white/[0.04]" style={{ animation: 'fadeInUp 0.2s ease-out' }}>
          <input
            type="text"
            className="input text-sm"
            placeholder="¿Qué practicaste?"
            value={formData.what_i_practiced}
            onChange={e => setFormData({...formData, what_i_practiced: e.target.value})}
          />
          <input
            type="text"
            className="input text-sm"
            placeholder="Micro-error (opcional)"
            value={formData.micro_error_found}
            onChange={e => setFormData({...formData, micro_error_found: e.target.value})}
          />
        </div>
      )}

      {/* Submit */}
      <button
        type="submit"
        disabled={loading || isSubmitting}
        className="btn btn-primary w-full flex justify-center items-center h-11 text-sm font-bold rounded-xl transition-all"
      >
        {isSubmitting ? (
          <Spinner size="md" className="!border-black/30 !border-t-black" />
        ) : (
          'Registrar sesión'
        )}
      </button>
    </form>
  );
}

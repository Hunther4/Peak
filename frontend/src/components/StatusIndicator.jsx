import { useEffect, useState } from 'react';
import { api } from '../api/client';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const StatusDot = ({ status }) => {
  const colors = {
    ok: 'bg-green-500',
    local: 'bg-blue-400',
    checking: 'bg-yellow-500',
    error: 'bg-red-500',
    slow: 'bg-orange-500'
  };
  const color = colors[status] || colors.checking;

  return (
    <div className="relative flex items-center justify-center">
      <div className={`w-2.5 h-2.5 rounded-full ${color} z-10`} />
      {status !== 'error' && (
        <>
          <div className={`absolute w-5 h-5 rounded-full ${color} opacity-20 animate-ping`} style={{ animationDuration: '2s' }} />
          <div className={`absolute w-5 h-5 rounded-full ${color} opacity-10 animate-ping`} style={{ animationDuration: '2s', animationDelay: '0.5s' }} />
        </>
      )}
    </div>
  );
};

// Fetch with timeout to prevent hanging
async function fetchWithTimeout(url, opts = {}, timeoutMs = 3000) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(url, { ...opts, signal: controller.signal });
    return res;
  } finally {
    clearTimeout(timer);
  }
}

export const StatusIndicator = ({ compact = false }) => {
  const [status, setStatus] = useState({
    backend: 'checking',
    ai: 'checking',
    latency: 0
  });

  useEffect(() => {
    let cancelled = false;

    const checkStatus = async () => {
      const start = Date.now();
      let backendStatus = 'error';
      let latency = 0;

      try {
        const res = await fetchWithTimeout(`${BASE_URL}/health`);
        if (res.ok) {
          latency = Date.now() - start;
          backendStatus = latency > 500 ? 'slow' : 'ok';
        }
      } catch {
        backendStatus = 'error';
      }

      let aiStatus = 'checking';
      try {
        const data = await api.models.getStatus();
        aiStatus = data.mode === 'api' ? 'ok' : 'local';
      } catch {
        aiStatus = 'error';
      }

      if (!cancelled) {
        setStatus({ backend: backendStatus, ai: aiStatus, latency });
      }
    };

    checkStatus();
    const interval = setInterval(checkStatus, 8000);
    return () => { cancelled = true; clearInterval(interval); };
  }, []);

  if (compact) {
    return (
      <div
        className="flex flex-col items-center gap-1.5 py-2 px-1 rounded-xl bg-white/[0.03] border border-white/[0.06] hover:bg-white/[0.08] transition-all cursor-help w-12"
        title={`Servidor: ${status.backend === 'ok' ? `OK (${status.latency}ms)` : status.backend} | IA: ${status.ai === 'local' ? 'LM Studio (Local)' : status.ai === 'ok' ? 'Cloud (Groq)' : status.ai}`}
      >
        <div className="flex items-center justify-center gap-1">
          <StatusDot status={status.backend} />
          <span className="text-[8px] font-mono text-neutral-400 uppercase">API</span>
        </div>
        <div className="w-6 h-px bg-white/[0.06]" />
        <div className="flex items-center justify-center gap-1">
          <StatusDot status={status.ai} />
          <span className="text-[8px] font-mono text-neutral-400 uppercase">{status.ai === 'local' ? 'LOC' : 'CLD'}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-4 px-4 py-2.5 bg-white/[0.03] rounded-xl border border-white/[0.06] backdrop-blur-sm transition-all duration-300 hover:bg-white/[0.05] hover:border-white/[0.1] hover:shadow-lg hover:shadow-black/20">
      <div className="flex items-center gap-2 cursor-help" title="Estado del servidor Peak">
        <StatusDot status={status.backend} />
        <span className={`text-[10px] font-semibold tracking-wider uppercase transition-colors duration-300 ${status.backend === 'error' ? 'text-red-400' : 'text-neutral-400'}`}>
          Server
        </span>
        {status.backend === 'ok' && (
          <span className="text-[9px] text-neutral-600 font-mono">{status.latency}ms</span>
        )}
      </div>

      <div className="w-px h-4 bg-white/[0.08]" />

      <div className="flex items-center gap-2 cursor-help" title={status.ai === 'local' ? 'LM Studio (Tu PC)' : 'Groq/OpenRouter'}>
        <StatusDot status={status.ai} />
        <span className={`text-[10px] font-semibold tracking-wider uppercase transition-colors duration-300 ${status.ai === 'error' ? 'text-red-400' : 'text-neutral-400'}`}>
          {status.ai === 'local' ? 'GPU 🖥' : status.ai === 'ok' ? 'Cloud ☁' : status.ai === 'checking' ? 'Checking...' : 'Offline'}
        </span>
      </div>
    </div>
  );
};

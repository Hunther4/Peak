import { useEffect, useState } from 'react';

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

export const StatusIndicator = () => {
  const [status, setStatus] = useState({
    backend: 'checking',
    ai: 'checking',
    latency: 0
  });

  useEffect(() => {
    const checkStatus = async () => {
      const start = Date.now();
      let backendStatus = 'error';
      let latency = 0;

      try {
        const res = await fetch(`${BASE_URL}/health`);
        if (res.ok) {
          latency = Date.now() - start;
          backendStatus = latency > 500 ? 'slow' : 'ok';
        }
      } catch {
        backendStatus = 'error';
      }

      let aiStatus = 'checking';
      try {
        const res = await fetch(`${BASE_URL}/models/status`);
        if (res.ok) {
          const data = await res.json();
          aiStatus = data.mode === 'api' ? 'ok' : 'local';
        } else {
          aiStatus = 'error';
        }
      } catch {
        aiStatus = 'error';
      }

      setStatus({ backend: backendStatus, ai: aiStatus, latency });
    };

    checkStatus();
    const interval = setInterval(checkStatus, 5000);
    return () => clearInterval(interval);
  }, []);

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
          {status.ai === 'local' ? 'GPU 🖥' : 'Cloud ☁'}
        </span>
      </div>
    </div>
  );
};

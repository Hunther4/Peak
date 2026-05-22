import { useState, useEffect, useCallback, useRef } from "react";
import { useStore } from "../store/store";

export default function DualNBackGame() {
  const [n, setN] = useState(2);
  const [sessionStarted, setSessionStarted] = useState(false);
  const [results, setResults] = useState([]);
  const startTime = useRef(null);

  const handleKeyPress = useCallback((e) => {
    if (!sessionStarted) return;
    const reactionTime = performance.now() - startTime.current;
    console.log(`Key pressed: ${e.key}, Reaction: ${reactionTime.toFixed(2)}ms`);
    // Aquí iría la lógica de registro de telemetría
  }, [sessionStarted]);

  useEffect(() => {
    window.addEventListener("keydown", handleKeyPress);
    return () => window.removeEventListener("keydown", handleKeyPress);
  }, [handleKeyPress]);

  return (
    <div className="card p-5">
      <h2 className="text-sm font-bold text-white mb-4">Dual N-Back (Telemetría Cognitiva)</h2>
      <button className="btn btn-primary" onClick={() => setSessionStarted(true)}>
        Iniciar Sesión
      </button>
    </div>
  );
}
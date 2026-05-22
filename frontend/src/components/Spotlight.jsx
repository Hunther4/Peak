import { useEffect, useRef } from 'react';

export default function Spotlight() {
  const spotlightRef = useRef(null);

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!spotlightRef.current) return;
      const x = e.clientX;
      const y = e.clientY;
      spotlightRef.current.style.background = `radial-gradient(600px circle at ${x}px ${y}px, rgba(34, 197, 94, 0.04), transparent 40%)`;
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  return (
    <div
      ref={spotlightRef}
      className="fixed inset-0 pointer-events-none z-[1]"
      style={{ transition: 'background 0.1s ease' }}
    />
  );
}

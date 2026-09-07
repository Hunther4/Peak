import { useEffect, useState, memo } from 'react';

const Particle = memo(({ x, y, size, duration, delay, opacity }) => (
  <div
    className="absolute rounded-full"
    style={{
      left: `${x}%`,
      top: `${y}%`,
      width: size,
      height: size,
      background: `radial-gradient(circle, rgba(34, 197, 94, ${opacity}), transparent 70%)`,
      animation: `twinkle ${duration}s ${delay}s ease-in-out infinite`,
    }}
  />
));

export default function AmbientParticles() {
  const [particles, setParticles] = useState([]);
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
    const generated = Array.from({ length: 40 }, (_, i) => ({
      id: i,
      x: Math.random() * 100,
      y: Math.random() * 100,
      size: 1 + Math.random() * 3,
      duration: 2 + Math.random() * 4,
      delay: Math.random() * 3,
      opacity: 0.3 + Math.random() * 0.3,
    }));
    setParticles(generated);
  }, []);

  if (!isClient) return null;

  return (
    <div className="particles">
      {particles.map(p => (
        <Particle key={p.id} {...p} />
      ))}
    </div>
  );
}

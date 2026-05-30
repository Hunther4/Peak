/**
 * AmbientBackground — The 4 blur blobs extracted once.
 * Used by App.jsx and GameShell to provide consistent ambient background.
 */
export function AmbientBackground() {
  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden">
      <div
        className="absolute -top-[40%] -left-[20%] w-[60%] h-[60%] bg-green-500/[0.03] rounded-full blur-[120px]"
        style={{ animation: "mesh-shift 15s ease-in-out infinite" }}
      />
      <div
        className="absolute -bottom-[30%] -right-[15%] w-[50%] h-[50%] bg-emerald-600/[0.02] rounded-full blur-[100px]"
        style={{ animation: "mesh-shift 20s ease-in-out infinite reverse" }}
      />
      <div
        className="absolute top-[20%] right-[10%] w-[30%] h-[30%] bg-blue-500/[0.02] rounded-full blur-[80px]"
        style={{ animation: "mesh-shift 18s ease-in-out infinite" }}
      />
      <div
        className="absolute bottom-[10%] left-[5%] w-[25%] h-[25%] bg-purple-500/[0.015] rounded-full blur-[90px]"
        style={{ animation: "mesh-shift 22s ease-in-out infinite reverse" }}
      />
    </div>
  )
}
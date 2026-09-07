import { memo } from "react"

// Skeleton base pulse animation
const Skeleton = memo(function Skeleton({ className = "", ...props }) {
  return (
    <div
      className={`animate-pulse bg-white/[0.04] rounded-xl ${className}`}
      {...props}
    />
  )
})

// Pre-built skeleton shapes
export const SkeletonCard = memo(function SkeletonCard({ className = "" }) {
  return (
    <div className={`card p-6 space-y-4 ${className}`}>
      <div className="flex items-start gap-4">
        <Skeleton className="w-16 h-16 rounded-full shrink-0" />
        <div className="flex-1 space-y-3">
          <Skeleton className="h-4 w-2/3" />
          <Skeleton className="h-3 w-1/3" />
          <div className="flex gap-3 mt-2">
            <Skeleton className="h-3 w-16" />
            <Skeleton className="h-3 w-16" />
            <Skeleton className="h-3 w-16" />
          </div>
        </div>
      </div>
    </div>
  )
})

export const SkeletonHero = memo(function SkeletonHero({ className = "" }) {
  return (
    <div className={`grid grid-cols-2 lg:grid-cols-4 gap-4 ${className}`}>
      {[...Array(4)].map((_, i) => (
        <div key={i} className="rounded-2xl bg-white/[0.02] border border-white/[0.04] p-5 space-y-3">
          <Skeleton className="w-8 h-8 rounded-lg" />
          <Skeleton className="h-8 w-16" />
          <Skeleton className="h-3 w-20" />
        </div>
      ))}
    </div>
  )
})

export const SkeletonTimeline = memo(function SkeletonTimeline({ rows = 3, className = "" }) {
  return (
    <div className={`space-y-4 ${className}`}>
      {[...Array(rows)].map((_, i) => (
        <div key={i} className="flex items-center gap-4 p-4 rounded-xl bg-white/[0.02]">
          <Skeleton className="w-10 h-10 rounded-lg shrink-0" />
          <div className="flex-1 space-y-2">
            <Skeleton className="h-3.5 w-1/2" />
            <Skeleton className="h-3 w-1/3" />
          </div>
          <Skeleton className="h-6 w-12 rounded-md" />
        </div>
      ))}
    </div>
  )
})

export default Skeleton

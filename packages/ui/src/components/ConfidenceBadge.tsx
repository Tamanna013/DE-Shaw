import { cn } from "./utils"
import { ShieldAlert, ShieldCheck, Shield } from "lucide-react"

export interface ConfidenceBadgeProps {
  score: number
  className?: string
}

export function ConfidenceBadge({ score, className }: ConfidenceBadgeProps) {
  // Enforce explicit variant mapping logic
  let variant = "low"
  let label = "Low Confidence"
  let Icon = ShieldAlert
  
  if (score >= 0.7) {
    variant = "high"
    label = "High Confidence"
    Icon = ShieldCheck
  } else if (score >= 0.4) {
    variant = "medium"
    label = "Medium Confidence"
    Icon = Shield
  }
  
  return (
    <div className={cn(
      "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none",
      {
        "bg-blue-100 text-blue-900 border-blue-200": variant === "high",
        "bg-orange-100 text-orange-900 border-orange-200": variant === "medium",
        "bg-gray-100 text-gray-900 border-gray-200": variant === "low",
      },
      className
    )}
    role="status"
    aria-label={`${label}, score: ${Math.round(score * 100)}%`}
    >
      <Icon className="w-3 h-3 mr-1.5" aria-hidden="true" />
      <span>{label} ({Math.round(score * 100)}%)</span>
    </div>
  )
}

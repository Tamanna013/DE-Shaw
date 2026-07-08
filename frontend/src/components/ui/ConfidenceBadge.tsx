import { cn } from "./Button"

export function ConfidenceBadge({ score, className }: { score: number, className?: string }) {
  // Score is 0.0 to 1.0
  let variant = "low";
  let label = "Low Confidence";
  
  if (score >= 0.7) {
    variant = "high";
    label = "High Confidence";
  } else if (score >= 0.4) {
    variant = "medium";
    label = "Medium Confidence";
  }
  
  return (
    <div className={cn(
      "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
      {
        "bg-confidence-high/10 text-confidence-high border-confidence-high/20": variant === "high",
        "bg-confidence-medium/10 text-confidence-medium border-confidence-medium/20": variant === "medium",
        "bg-confidence-low/10 text-confidence-low border-confidence-low/20": variant === "low",
      },
      className
    )}>
      {label} ({Math.round(score * 100)}%)
    </div>
  )
}

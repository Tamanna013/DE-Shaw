import { ConfidenceBadge } from '@/components/ui/ConfidenceBadge'
import { EvidenceList } from './EvidenceList'
import { Lightbulb } from 'lucide-react'

export interface Hypothesis {
  id: string
  title: string
  description: string
  confidence_score: number
  evidence: Array<{type: string, value: string}>
  recommendations: string[]
}

export function RootCauseCard({ hypothesis }: { hypothesis: Hypothesis }) {
  return (
    <div className="border rounded-xl bg-card shadow-sm overflow-hidden flex flex-col">
      <div className="px-6 py-4 border-b bg-muted/20 flex items-start justify-between">
        <div>
          <h4 className="font-semibold text-lg">{hypothesis.title}</h4>
        </div>
        <ConfidenceBadge score={hypothesis.confidence_score} />
      </div>
      
      <div className="p-6 space-y-6">
        <p className="text-sm leading-relaxed">{hypothesis.description}</p>
        
        <div className="space-y-3">
          <h5 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Evidence Citing</h5>
          <EvidenceList evidence={hypothesis.evidence} />
        </div>

        <div className="space-y-3">
          <h5 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Recommended Actions</h5>
          <ul className="space-y-2">
            {hypothesis.recommendations.map((rec, i) => (
              <li key={i} className="flex items-start text-sm bg-blue-50/50 dark:bg-blue-950/20 border border-blue-100 dark:border-blue-900 rounded-md p-3">
                <Lightbulb className="w-5 h-5 text-blue-500 mr-3 flex-shrink-0 mt-0.5" />
                <span>{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  )
}

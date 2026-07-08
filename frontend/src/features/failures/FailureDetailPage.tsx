import { useParams, Link } from 'react-router-dom'
import { useState } from 'react'
import { RootCauseCard } from './RootCauseCard'
import { Button } from '@/components/ui/Button'
import { ArrowLeft, CheckCircle2 } from 'lucide-react'

// Normally fetched via useQuery, but stubbed here since we don't have the backend API running
const MOCK_REPORT = {
  id: "report-123",
  test_name: "test_checkout_concurrency",
  status: "analyzed",
  hypotheses: [
    {
      id: "hyp-1",
      title: "Database Deadlock on Accounts Table",
      description: "The stack trace indicates a deadlock error during concurrent row updates. This heavily overlaps with a recent commit changing isolation levels.",
      confidence_score: 0.85,
      evidence: [
        { type: "commit", value: "commit abc1234 modifies db/accounts.py" },
        { type: "log", value: "psycopg2.errors.DeadlockDetected in trace" }
      ],
      recommendations: ["Revert commit abc1234 or apply explicit row locking in checkout_service"]
    },
    {
      id: "hyp-2",
      title: "Network Timeout to Payment Gateway",
      description: "A secondary possibility is that the external payment gateway took too long to respond, holding the DB transaction open.",
      confidence_score: 0.35,
      evidence: [
        { type: "log", value: "ReadTimeoutError on stripe.com/charge" }
      ],
      recommendations: ["Increase timeout to 5000ms"]
    }
  ]
}

export default function FailureDetailPage() {
  const { id } = useParams()
  const [resolved, setResolved] = useState(false)
  const report = MOCK_REPORT // Would be data from useQuery

  const handleResolve = () => {
    // In reality, this fires a mutation to POST /api/v1/failures/:id/resolve
    setResolved(true)
  }

  return (
    <div className="space-y-6 max-w-4xl mx-auto animate-in fade-in duration-500">
      <div className="flex items-center space-x-4 mb-8">
        <Link to="/dashboard" className="text-muted-foreground hover:text-foreground transition-colors">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div>
          <div className="flex items-center space-x-3">
            <h2 className="text-2xl font-bold tracking-tight">Failure Analysis</h2>
            {resolved && (
              <span className="inline-flex items-center text-sm text-green-600 bg-green-50 px-2 py-1 rounded-md border border-green-200">
                <CheckCircle2 className="w-4 h-4 mr-1" />
                Resolved
              </span>
            )}
          </div>
          <p className="text-muted-foreground text-sm font-mono mt-1">{report.test_name}</p>
        </div>
        <div className="flex-1" />
        {!resolved && (
          <Button onClick={handleResolve}>Mark Resolved</Button>
        )}
      </div>

      <div className="space-y-6">
        <h3 className="text-xl font-semibold border-b pb-2">Root Cause Hypotheses</h3>
        <p className="text-sm text-muted-foreground">
          The AI Reasoning Engine has analyzed logs, stack traces, and recent commits to produce these hypotheses.
        </p>

        {report.hypotheses.sort((a, b) => b.confidence_score - a.confidence_score).map(hyp => (
          <RootCauseCard key={hyp.id} hypothesis={hyp} />
        ))}
      </div>
    </div>
  )
}

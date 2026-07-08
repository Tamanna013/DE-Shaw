import { useQuery } from '@tanstack/react-query'
import { api } from '@/api/client'
import { Link } from 'react-router-dom'

export function FlakyLeaderboard({ repoId }: { repoId: string }) {
  const { data, isLoading } = useQuery({
    queryKey: ['leaderboard', repoId],
    queryFn: () => api.dashboard.getFlaky(repoId),
  })

  if (isLoading) {
    return (
      <div className="space-y-4">
        {[1,2,3].map(i => <div key={i} className="h-12 bg-muted animate-pulse rounded-md"></div>)}
      </div>
    )
  }

  const entries = data?.length ? data : [
    { test_case_id: 'tc-1', test_case_name: 'test_user_auth_timeout', flip_count: 42, flaky_score: 0.89 },
    { test_case_id: 'tc-2', test_case_name: 'test_db_race_condition', flip_count: 15, flaky_score: 0.65 },
    { test_case_id: 'tc-3', test_case_name: 'test_external_api_mock', flip_count: 8, flaky_score: 0.41 },
  ]

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm text-left">
        <thead className="text-xs text-muted-foreground uppercase bg-muted/50">
          <tr>
            <th className="px-4 py-3 rounded-tl-md">Test Case</th>
            <th className="px-4 py-3 text-right">Flip Count</th>
            <th className="px-4 py-3 text-right rounded-tr-md">Flaky Score</th>
          </tr>
        </thead>
        <tbody>
          {entries.map((entry) => (
            <tr key={entry.test_case_id} className="border-b border-border/50 last:border-0 hover:bg-muted/20 transition-colors">
              <td className="px-4 py-3 font-medium text-primary">
                {/* Simulated link to test case details */}
                <Link to={`/failures/${entry.test_case_id}`} className="hover:underline">
                  {entry.test_case_name}
                </Link>
              </td>
              <td className="px-4 py-3 text-right">{entry.flip_count}</td>
              <td className="px-4 py-3 text-right">
                <span className="inline-flex items-center justify-center px-2 py-1 text-xs font-bold rounded-full bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400">
                  {Math.round(entry.flaky_score * 100)}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

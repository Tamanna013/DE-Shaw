import { useState } from 'react'
import { FailureTrendChart } from './FailureTrendChart'
import { FlakyLeaderboard } from './FlakyLeaderboard'
import { Button } from '@/components/ui/Button'

export default function DashboardPage() {
  const [repoId, setRepoId] = useState('repo-1')
  
  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
          <p className="text-muted-foreground mt-1">
            Metrics and failure analysis across your repositories.
          </p>
        </div>
        
        <div className="flex space-x-2">
          {/* Simulated Repo Selector */}
          <select 
            className="h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
            value={repoId}
            onChange={(e) => setRepoId(e.target.value)}
            aria-label="Select Repository"
          >
            <option value="repo-1">testlens/backend</option>
            <option value="repo-2">testlens/frontend</option>
          </select>
          <Button variant="outline">Last 30 Days</Button>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {/* Mocked stat cards for UI completeness */}
        <div className="rounded-xl border bg-card text-card-foreground shadow p-6">
          <div className="flex flex-row items-center justify-between space-y-0 pb-2">
            <h3 className="tracking-tight text-sm font-medium">Overall Pass Rate</h3>
          </div>
          <div className="text-2xl font-bold">92.4%</div>
          <p className="text-xs text-muted-foreground">+2.1% from last month</p>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-7">
        <div className="col-span-4 border rounded-xl shadow-sm p-4 bg-card">
          <h3 className="font-semibold mb-4 text-lg">Failure Trend</h3>
          <FailureTrendChart repoId={repoId} />
        </div>
        
        <div className="col-span-3 border rounded-xl shadow-sm p-4 bg-card">
          <h3 className="font-semibold mb-4 text-lg">Flaky Test Leaderboard</h3>
          <FlakyLeaderboard repoId={repoId} />
        </div>
      </div>
    </div>
  )
}

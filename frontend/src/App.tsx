import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { lazy, Suspense } from 'react'

const DashboardPage = lazy(() => import('./features/dashboard/DashboardPage'))
const FailureDetailPage = lazy(() => import('./features/failures/FailureDetailPage'))

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-background text-foreground flex flex-col">
        <header className="border-b px-6 py-4 flex items-center justify-between">
          <h1 className="text-xl font-bold bg-gradient-to-r from-blue-500 to-indigo-500 bg-clip-text text-transparent">
            TestLens
          </h1>
          {/* Theme toggle could go here */}
        </header>
        
        <main className="flex-1 p-6 max-w-7xl mx-auto w-full">
          <Suspense fallback={<div className="animate-pulse flex space-x-4">Loading application...</div>}>
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/failures/:id" element={<FailureDetailPage />} />
            </Routes>
          </Suspense>
        </main>
      </div>
    </BrowserRouter>
  )
}

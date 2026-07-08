import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import FailureDetailPage from '../features/failures/FailureDetailPage'
import { BrowserRouter } from 'react-router-dom'

// Mock the Recharts library so it doesn't crash in JSDOM
vi.mock('recharts', () => {
  return {
    ResponsiveContainer: ({ children }: any) => <div>{children}</div>,
    AreaChart: () => <div>AreaChart</div>,
    Area: () => null,
    XAxis: () => null,
    YAxis: () => null,
    CartesianGrid: () => null,
    Tooltip: () => null,
  }
})

describe('FailureDetailPage', () => {
  it('renders root cause hypotheses ordered by confidence score descending', () => {
    render(
      <BrowserRouter>
        <FailureDetailPage />
      </BrowserRouter>
    )
    
    // Grab all elements that represent a hypothesis title
    const headings = screen.getAllByRole('heading', { level: 4 })
    
    // The mock data has 0.85 (Deadlock) and 0.35 (Timeout). 
    // Deadlock MUST be first.
    expect(headings[0].textContent).toBe('Database Deadlock on Accounts Table')
    expect(headings[1].textContent).toBe('Network Timeout to Payment Gateway')
  })

  it('allows marking a failure as resolved', () => {
    render(
      <BrowserRouter>
        <FailureDetailPage />
      </BrowserRouter>
    )
    
    const resolveBtn = screen.getByText('Mark Resolved')
    expect(resolveBtn).toBeDefined()
    
    // Click it
    fireEvent.click(resolveBtn)
    
    // The button should disappear, and "Resolved" badge should appear
    expect(screen.queryByText('Mark Resolved')).toBeNull()
    expect(screen.getByText('Resolved')).toBeDefined()
  })
})

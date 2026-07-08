import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { ErrorBoundary } from './ErrorBoundary'

const Bomb = ({ shouldThrow }: { shouldThrow?: boolean }) => {
  if (shouldThrow) {
    throw new Error('Boom!')
  }
  return <div>Safe</div>
}

describe('ErrorBoundary', () => {
  // Suppress React's error logging in tests so the console stays clean
  const originalError = console.error
  beforeAll(() => {
    console.error = vi.fn()
  })
  afterAll(() => {
    console.error = originalError
  })

  it('renders children when no error', () => {
    render(
      <ErrorBoundary>
        <Bomb />
      </ErrorBoundary>
    )
    expect(screen.getByText('Safe')).toBeDefined()
  })

  it('renders fallback UI when error thrown', () => {
    render(
      <ErrorBoundary>
        <Bomb shouldThrow />
      </ErrorBoundary>
    )
    expect(screen.getByText('Something went wrong')).toBeDefined()
    expect(screen.getByText('Boom!')).toBeDefined()
  })

  it('calls reporter callback if provided', () => {
    const reporter = vi.fn()
    render(
      <ErrorBoundary reporter={reporter}>
        <Bomb shouldThrow />
      </ErrorBoundary>
    )
    expect(reporter).toHaveBeenCalledTimes(1)
    expect(reporter.mock.calls[0][0].message).toBe('Boom!')
  })
})

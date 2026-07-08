import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { Badge } from './Badge'

describe('Badge', () => {
  it('renders default badge', () => {
    render(<Badge>New</Badge>)
    const badge = screen.getByText('New')
    expect(badge).toBeDefined()
    expect(badge.className).toContain('bg-blue-100')
  })

  it('renders destructive variant', () => {
    render(<Badge variant="destructive">Error</Badge>)
    const badge = screen.getByText('Error')
    expect(badge.className).toContain('bg-red-100')
  })
})

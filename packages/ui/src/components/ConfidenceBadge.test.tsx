import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { ConfidenceBadge } from './ConfidenceBadge'

describe('ConfidenceBadge', () => {
  it('renders high confidence for scores >= 0.7', () => {
    render(<ConfidenceBadge score={0.85} />)
    const badge = screen.getByText('High Confidence (85%)')
    expect(badge).toBeDefined()
    // Explicitly test for colorblind-safe text inclusion, as per requirements
    expect(badge.textContent).toContain('High Confidence') 
  })

  it('renders medium confidence for scores 0.4-0.69', () => {
    render(<ConfidenceBadge score={0.5} />)
    expect(screen.getByText('Medium Confidence (50%)')).toBeDefined()
  })

  it('renders low confidence for scores < 0.4', () => {
    render(<ConfidenceBadge score={0.2} />)
    expect(screen.getByText('Low Confidence (20%)')).toBeDefined()
  })

  it('never relies on color alone (has semantic text labels)', () => {
    render(<ConfidenceBadge score={0.9} />)
    // The test specifically verifies the text node contains the semantic meaning
    const el = screen.getByRole('status')
    expect(el.textContent).toMatch(/High Confidence/)
  })
})

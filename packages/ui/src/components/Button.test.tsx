import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { Button } from './Button'

describe('Button', () => {
  it('renders default button', () => {
    render(<Button>Click me</Button>)
    const button = screen.getByRole('button', { name: /click me/i })
    expect(button).toBeDefined()
    expect(button.className).toContain('bg-blue-600')
  })

  it('renders outline variant', () => {
    render(<Button variant="outline">Outline</Button>)
    const button = screen.getByRole('button', { name: /outline/i })
    expect(button.className).toContain('border-gray-200')
  })

  it('respects disabled state', () => {
    render(<Button disabled>Disabled</Button>)
    const button = screen.getByRole('button', { name: /disabled/i })
    expect(button.hasAttribute('disabled')).toBe(true)
    expect(button.className).toContain('disabled:opacity-50')
  })
})

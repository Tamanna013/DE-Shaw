import type { Meta, StoryObj } from '@storybook/react'
import { ErrorBoundary } from './ErrorBoundary'

const meta: Meta<typeof ErrorBoundary> = {
  title: 'Components/ErrorBoundary',
  component: ErrorBoundary,
  tags: ['autodocs'],
}

export default meta
type Story = StoryObj<typeof ErrorBoundary>

const Bomb = () => {
  throw new Error("This is a simulated component crash.")
}

export const Default: Story = {
  render: () => (
    <ErrorBoundary>
      <Bomb />
    </ErrorBoundary>
  ),
}

export const WithCustomFallback: Story = {
  render: () => (
    <ErrorBoundary fallback={<div className="text-red-500 font-bold">Custom Error UI</div>}>
      <Bomb />
    </ErrorBoundary>
  ),
}

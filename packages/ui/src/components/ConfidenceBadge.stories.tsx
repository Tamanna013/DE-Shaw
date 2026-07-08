import type { Meta, StoryObj } from '@storybook/react'
import { ConfidenceBadge } from './ConfidenceBadge'

const meta: Meta<typeof ConfidenceBadge> = {
  title: 'Components/ConfidenceBadge',
  component: ConfidenceBadge,
  tags: ['autodocs'],
  argTypes: {
    score: {
      control: { type: 'range', min: 0, max: 1, step: 0.05 },
    },
  },
}

export default meta
type Story = StoryObj<typeof ConfidenceBadge>

export const High: Story = {
  args: {
    score: 0.85,
  },
}

export const Medium: Story = {
  args: {
    score: 0.5,
  },
}

export const Low: Story = {
  args: {
    score: 0.2,
  },
}

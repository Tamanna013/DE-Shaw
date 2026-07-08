# @testlens/ui

A strict, CVA-driven React Component Library for TestLens frontend applications.

## Design Principles
1. **Explicit Variants**: Components use `class-variance-authority` (cva). We do not accept arbitrary `className` strings injected by consumers for structural logic, preventing visual regressions.
2. **Accessible Confidence Scales**: The AI Reasoning Engine's confidence scores are displayed using the `ConfidenceBadge` component, which maps 0-1 scores into `Low`, `Medium`, and `High` categories. It strictly enforces text labels and semantic icons alongside colors to ensure colorblind users can immediately distinguish confidence levels.
3. **Framework Agnostic Error Boundaries**: The `ErrorBoundary` accepts a generic `reporter` prop. It does not hardcode Sentry, allowing us to swap observability backends without modifying the design system.

## Visual Regression Testing
Storybook stories are written for every component in the `*.stories.tsx` files. In a complete CI/CD pipeline, these stories will automatically be uploaded to **Chromatic** for visual regression diffing on every PR.

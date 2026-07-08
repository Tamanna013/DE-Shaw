import React, { Component, ErrorInfo, ReactNode } from "react"
import { AlertTriangle } from "lucide-react"

export interface ErrorBoundaryProps {
  children: ReactNode
  reporter?: (error: Error, errorInfo: ErrorInfo) => void
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, State> {
  public state: State = {
    hasError: false,
    error: null
  }

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    if (this.props.reporter) {
      this.props.reporter(error, errorInfo)
    }
  }

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      return (
        <div className="p-6 border border-red-200 bg-red-50 rounded-lg flex items-start space-x-4">
          <AlertTriangle className="w-6 h-6 text-red-500 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="text-lg font-semibold text-red-900">Something went wrong</h3>
            <p className="text-sm text-red-700 mt-1">
              A UI component crashed. The error has been logged automatically.
            </p>
            {this.state.error && (
              <pre className="mt-4 p-3 bg-red-100 text-red-900 rounded text-xs overflow-auto max-w-full">
                {this.state.error.message}
              </pre>
            )}
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

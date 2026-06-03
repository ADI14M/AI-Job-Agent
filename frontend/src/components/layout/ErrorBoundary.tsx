import React, { Component, ErrorInfo, ReactNode } from "react"
import { AlertCircle } from "lucide-react"

interface Props {
  children?: ReactNode
}

interface State {
  hasError: boolean
  errorMsg: string
}

export default class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    errorMsg: ""
  }

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, errorMsg: error.message }
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Uncaught error:", error, errorInfo)
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-slate-50 text-slate-900 p-4">
          <AlertCircle className="h-16 w-16 text-red-500 mb-4" />
          <h1 className="text-2xl font-bold mb-2">Something went wrong.</h1>
          <p className="text-muted-foreground mb-6 text-center max-w-md">
            The application encountered an unexpected error. Please try refreshing the page.
          </p>
          <pre className="bg-slate-100 p-4 rounded text-xs text-red-800 max-w-2xl overflow-auto border border-red-200">
            {this.state.errorMsg}
          </pre>
          <button 
            className="mt-6 bg-slate-900 text-white px-4 py-2 rounded shadow hover:bg-slate-800"
            onClick={() => window.location.reload()}
          >
            Reload Page
          </button>
        </div>
      )
    }

    return this.props.children
  }
}

import { Outlet } from "react-router-dom"
import { Bot } from "lucide-react"

export default function AuthLayout() {
  return (
    <div className="flex min-h-screen bg-muted/30">
      <div className="flex flex-1 flex-col justify-center px-4 py-12 sm:px-6 lg:flex-none lg:px-20 xl:px-24">
        <div className="mx-auto w-full max-w-sm lg:w-96">
          <div className="flex items-center gap-2 text-primary mb-8">
            <Bot className="h-10 w-10" />
            <span className="text-2xl font-bold tracking-tight">AI Job Agent</span>
          </div>
          <Outlet />
        </div>
      </div>
      <div className="relative hidden w-0 flex-1 lg:block bg-slate-900">
        <div className="absolute inset-0 h-full w-full bg-gradient-to-br from-indigo-600 to-purple-800 opacity-90" />
        <div className="absolute inset-0 flex items-center justify-center p-12">
          <div className="max-w-2xl text-center text-white space-y-6">
            <h2 className="text-4xl font-bold tracking-tight">Your Autonomous Job Search Platform</h2>
            <p className="text-lg text-indigo-100">
              Upload your resume, and let our AI agents discover, evaluate, optimize, and apply to the best matching jobs while you sleep.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

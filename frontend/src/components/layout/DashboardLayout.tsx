import { Outlet, Link, useNavigate, useLocation } from "react-router-dom"
import { useAuthStore } from "@/store/useAuthStore"
import { Button } from "@/components/ui/button"
import {
  LayoutDashboard,
  FileText,
  Search,
  Briefcase,
  Settings,
  LogOut,
  Sparkles,
  Bot
} from "lucide-react"

export default function DashboardLayout() {
  const logout = useAuthStore((state) => state.logout)
  const navigate = useNavigate()
  const location = useLocation()

  const handleLogout = () => {
    logout()
    navigate("/login")
  }

  const navigation = [
    { name: "Dashboard", href: "/", icon: LayoutDashboard },
    { name: "Resumes & Docs", href: "/resumes", icon: FileText },
    { name: "Job Discovery", href: "/jobs", icon: Search },
    { name: "Applications", href: "/applications", icon: Briefcase },
    { name: "Settings", href: "/settings", icon: Settings },
  ]

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <div className="w-64 border-r bg-card px-4 py-6 flex flex-col justify-between">
        <div>
          <div className="flex items-center gap-2 px-2 mb-8 text-primary">
            <Bot className="h-8 w-8" />
            <span className="text-xl font-bold tracking-tight">AI Job Agent</span>
          </div>
          
          <nav className="space-y-1">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href
              return (
                <Link key={item.name} to={item.href}>
                  <Button
                    variant={isActive ? "secondary" : "ghost"}
                    className="w-full justify-start"
                  >
                    <item.icon className="mr-3 h-5 w-5" />
                    {item.name}
                  </Button>
                </Link>
              )
            })}
          </nav>
        </div>
        
        <div className="space-y-4">
          <div className="rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 p-4 text-white shadow-lg">
            <div className="flex items-center gap-2 font-semibold mb-1">
              <Sparkles className="h-4 w-4" />
              Agent Active
            </div>
            <p className="text-xs opacity-90">Your autonomous orchestrator is standing by.</p>
          </div>
          <Button variant="ghost" className="w-full justify-start text-muted-foreground" onClick={handleLogout}>
            <LogOut className="mr-3 h-5 w-5" />
            Logout
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto bg-muted/30 p-8">
        <div className="mx-auto max-w-7xl">
          <Outlet />
        </div>
      </main>
    </div>
  )
}

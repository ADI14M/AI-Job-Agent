import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { Toaster } from "sonner"

import AuthLayout from "@/components/layout/AuthLayout"
import DashboardLayout from "@/components/layout/DashboardLayout"
import ProtectedRoute from "@/components/layout/ProtectedRoute"

import Login from "@/pages/Login"
import Register from "@/pages/Register"
import Dashboard from "@/pages/Dashboard"
import Resumes from "@/pages/Resumes"
import JobDiscovery from "@/pages/JobDiscovery"
import Applications from "@/pages/Applications"
import Settings from "@/pages/Settings"

const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Routes>
          <Route element={<AuthLayout />}>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
          </Route>
          
          <Route element={<ProtectedRoute />}>
            <Route element={<DashboardLayout />}>
              <Route path="/" element={<Dashboard />} />
              <Route path="/resumes" element={<Resumes />} />
              <Route path="/jobs" element={<JobDiscovery />} />
              <Route path="/applications" element={<Applications />} />
              <Route path="/settings" element={<Settings />} />
            </Route>
          </Route>
          
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
      <Toaster position="top-right" richColors />
    </QueryClientProvider>
  )
}

export default App

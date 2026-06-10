import { Navigate, Outlet } from "react-router-dom"
import { useAuthStore } from "@/store/useAuthStore"

export default function ProtectedRoute() {
  // TEST MODE: Hardcoded to true to bypass login page
  const isAuthenticated = true

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return <Outlet />
}

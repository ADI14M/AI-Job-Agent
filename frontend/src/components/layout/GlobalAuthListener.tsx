import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/store/useAuthStore'
import { toast } from 'sonner'

export default function GlobalAuthListener() {
  const navigate = useNavigate()
  const logout = useAuthStore((state) => state.logout)

  useEffect(() => {
    const handleUnauthorized = () => {
      logout()
      toast.error('Session expired. Please log in again.')
      // TEST MODE: Disabled auto-redirect to login
      // navigate('/login')
    }

    window.addEventListener('auth:unauthorized', handleUnauthorized)
    return () => {
      window.removeEventListener('auth:unauthorized', handleUnauthorized)
    }
  }, [logout, navigate])

  return null
}

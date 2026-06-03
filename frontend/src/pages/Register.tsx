import { useState } from "react"
import { useNavigate, Link } from "react-router-dom"
import { apiClient } from "@/api/client"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { toast } from "sonner"

export default function Register() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const navigate = useNavigate()

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      await apiClient.post("/auth/register", {
        email,
        password
      })
      
      toast.success("Account created! Please log in.")
      navigate("/login")
    } catch (error) {
      toast.error("Failed to register. User may already exist.")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div>
      <h2 className="mt-8 text-2xl font-bold leading-9 tracking-tight text-foreground">
        Create an account
      </h2>
      <p className="mt-2 text-sm leading-6 text-muted-foreground">
        Already have an account?{" "}
        <Link to="/login" className="font-semibold text-primary hover:text-primary/80">
          Sign in here
        </Link>
      </p>

      <div className="mt-10">
        <form onSubmit={handleRegister} className="space-y-6">
          <div>
            <Label htmlFor="email">Email address</Label>
            <div className="mt-2">
              <Input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
          </div>

          <div>
            <Label htmlFor="password">Password</Label>
            <div className="mt-2">
              <Input
                id="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>

          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading ? "Creating account..." : "Create account"}
          </Button>
        </form>
      </div>
    </div>
  )
}

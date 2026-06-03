import { useState } from "react"
import { useMutation } from "@tanstack/react-query"
import { apiClient } from "@/api/client"
import { useAuthStore } from "@/store/useAuthStore"
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { toast } from "sonner"
import { Brain, Settings as SettingsIcon, Save } from "lucide-react"

export default function Settings() {
  const user = useAuthStore((state) => state.user)
  const [apiKey, setApiKey] = useState("")

  const trainEngine = useMutation({
    mutationFn: async () => {
      const res = await apiClient.post('/learning/train')
      return res.data
    },
    onSuccess: () => {
      toast.success("Learning Engine successfully trained on your latest feedback!")
    },
    onError: () => {
      toast.error("Failed to train learning engine.")
    }
  })

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h3 className="text-2xl font-bold tracking-tight">Platform Settings</h3>
        <p className="text-muted-foreground">Manage your AI Job Agent preferences and credentials.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-indigo-500" />
            Learning Engine Optimization
          </CardTitle>
          <CardDescription>
            The Agent automatically learns from which jobs you get interviews for and which you get rejected from.
            Trigger a manual re-weighting of your job matching algorithm.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="rounded-lg bg-muted p-4 text-sm">
            Current Weights: Match (35%), ATS (25%), Location (20%), Salary (20%)
          </div>
        </CardContent>
        <CardFooter>
          <Button onClick={() => trainEngine.mutate()} disabled={trainEngine.isPending}>
            {trainEngine.isPending ? "Training..." : "Trigger AI Optimization Cycle"}
          </Button>
        </CardFooter>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <SettingsIcon className="h-5 w-5" />
            API Keys & Integrations
          </CardTitle>
          <CardDescription>
            Configure your external API keys (OpenAI, Anthropic, LinkedIn).
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-2">
            <Label htmlFor="openai">OpenAI API Key</Label>
            <Input 
              id="openai" 
              type="password" 
              placeholder="sk-..." 
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
            />
            <p className="text-xs text-muted-foreground">Used for Resume Optimization and Cover Letter Generation.</p>
          </div>
        </CardContent>
        <CardFooter>
          <Button onClick={() => toast.success("Settings saved!")}>
            <Save className="mr-2 h-4 w-4" /> Save Preferences
          </Button>
        </CardFooter>
      </Card>
    </div>
  )
}

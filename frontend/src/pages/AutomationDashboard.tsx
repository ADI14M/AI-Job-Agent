import { useState } from "react"
import { useQuery, useMutation } from "@tanstack/react-query"
import { apiClient } from "@/api/client"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Play, Pause, Settings, Activity, CheckCircle, XCircle, Clock } from "lucide-react"
import { toast } from "sonner"

export default function AutomationDashboard() {
  const [activeTab, setActiveTab] = useState("queue")

  const { data: states, refetch } = useQuery({
    queryKey: ['agent-states'],
    queryFn: async () => {
      const res = await apiClient.get('/agent/states')
      return res.data.data
    },
    refetchInterval: 5000 // Poll every 5s for live updates
  })

  const processMutation = useMutation({
    mutationFn: async ({ id, action }: { id: number, action: string }) => {
      const res = await apiClient.post('/agent/process', { agent_state_id: id, action })
      return res.data
    },
    onSuccess: (data) => {
      toast.success(data.message)
      refetch()
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to process")
    }
  })

  const scheduleMutation = useMutation({
    mutationFn: async () => {
      const res = await apiClient.post('/agent/schedule', { interval_hours: 1 })
      return res.data
    },
    onSuccess: (data) => {
      toast.success(data.message)
    }
  })

  const needsReview = states?.filter((s: any) => s.current_state === "READY_FOR_REVIEW") || []
  const activeQueue = states?.filter((s: any) => !["READY_FOR_REVIEW", "SUBMITTED", "FAILED", "REJECTED", "WITHDRAWN", "OFFER"].includes(s.current_state)) || []
  const completed = states?.filter((s: any) => ["SUBMITTED", "FAILED", "REJECTED", "WITHDRAWN", "OFFER"].includes(s.current_state)) || []

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-2xl font-bold tracking-tight">AI Agent Automation</h3>
          <p className="text-muted-foreground">Manage your fully autonomous application pipelines.</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => scheduleMutation.mutate()}>
            <Settings className="w-4 h-4 mr-2" /> Start Hourly Planner
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm text-muted-foreground">Active Pipelines</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-bold">{activeQueue.length}</div></CardContent>
        </Card>
        <Card className={needsReview.length > 0 ? "border-yellow-400 bg-yellow-50/10" : ""}>
          <CardHeader className="pb-2"><CardTitle className="text-sm text-muted-foreground flex items-center"><Activity className="w-4 h-4 mr-1"/> Action Required</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-bold text-yellow-600">{needsReview.length}</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm text-muted-foreground">Successfully Submitted</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-bold text-green-600">{states?.filter((s: any) => s.current_state === "SUBMITTED").length || 0}</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm text-muted-foreground">Failed Executions</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-bold text-red-600">{states?.filter((s: any) => s.current_state === "FAILED").length || 0}</div></CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="queue">Active Queue ({activeQueue.length})</TabsTrigger>
          <TabsTrigger value="review" className={needsReview.length > 0 ? "text-yellow-600 font-semibold" : ""}>
            Human Review ({needsReview.length})
          </TabsTrigger>
          <TabsTrigger value="history">Execution History</TabsTrigger>
        </TabsList>

        <TabsContent value="queue" className="space-y-4 mt-4">
          {activeQueue.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">No active applications currently processing.</div>
          ) : (
            activeQueue.map((s: any) => (
              <Card key={s.id}>
                <CardContent className="flex items-center justify-between p-4">
                  <div>
                    <div className="font-semibold">Application Pipeline #{s.id} (Job ID: {s.job_id})</div>
                    <div className="text-sm text-muted-foreground">Provider: {s.provider || "Auto-detecting..."}</div>
                  </div>
                  <div className="flex items-center gap-4">
                    <Badge variant="outline" className="animate-pulse bg-indigo-50">{s.current_state}</Badge>
                    <Clock className="w-4 h-4 text-muted-foreground" />
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </TabsContent>

        <TabsContent value="review" className="space-y-4 mt-4">
          {needsReview.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">No applications currently await your review.</div>
          ) : (
            needsReview.map((s: any) => (
              <Card key={s.id} className="border-yellow-200">
                <CardHeader className="bg-yellow-50/50 pb-4">
                  <div className="flex justify-between items-center">
                    <CardTitle className="text-lg">Review Required: Job #{s.job_id}</CardTitle>
                    <Badge variant="destructive">Needs Approval</Badge>
                  </div>
                </CardHeader>
                <CardContent className="pt-4">
                  <p className="text-sm text-muted-foreground mb-4">
                    The AI Planner has prepared the application package but requires human confirmation before interacting with the browser.
                  </p>
                  <div className="flex gap-2">
                    <Button 
                      className="bg-green-600 hover:bg-green-700"
                      onClick={() => processMutation.mutate({ id: s.id, action: "APPROVE" })}
                      disabled={processMutation.isPending}
                    >
                      <CheckCircle className="w-4 h-4 mr-2" /> Approve & Submit
                    </Button>
                      <Button variant="outline" className="border-destructive text-destructive hover:bg-destructive/10">
                        <XCircle className="w-4 h-4 mr-2" /> Reject & Cancel
                      </Button>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </TabsContent>

        <TabsContent value="history" className="space-y-4 mt-4">
          {completed.map((s: any) => (
            <Card key={s.id}>
              <CardContent className="flex flex-col gap-2 p-4">
                <div className="flex justify-between items-center">
                  <div className="font-semibold">Pipeline #{s.id} (Job ID: {s.job_id})</div>
                  <Badge className={s.current_state === "SUBMITTED" ? "bg-green-500" : "bg-red-500"}>
                    {s.current_state}
                  </Badge>
                </div>
                {s.last_error && (
                  <div className="text-sm text-red-600 bg-red-50 p-2 rounded mt-2">
                    <strong>Error:</strong> {s.last_error}
                  </div>
                )}
                {s.logs && s.logs.length > 0 && (
                  <details className="mt-2 text-xs">
                    <summary className="cursor-pointer text-muted-foreground hover:text-indigo-600">View Execution Logs</summary>
                    <div className="mt-2 space-y-1 bg-muted/30 p-2 rounded font-mono text-[10px]">
                      {s.logs.map((log: string, idx: number) => (
                        <div key={idx}>{log}</div>
                      ))}
                    </div>
                  </details>
                )}
              </CardContent>
            </Card>
          ))}
        </TabsContent>
      </Tabs>
    </div>
  )
}

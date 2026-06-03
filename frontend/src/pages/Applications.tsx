import { useQuery } from "@tanstack/react-query"
import { apiClient } from "@/api/client"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Building2, MapPin, Calendar, Briefcase } from "lucide-react"

export default function Applications() {
  const { data: applications, isLoading } = useQuery({
    queryKey: ['applications'],
    queryFn: async () => {
      try {
        const res = await apiClient.get('/applications/')
        return res.data
      } catch (e) {
        // Mock data fallback
        return [
          { id: 1, title: "Senior AI Engineer", company: "OpenAI", status: "INTERVIEW", applied_date: "2023-10-15" },
          { id: 2, title: "Backend Engineer", company: "Stripe", status: "APPLIED", applied_date: "2023-10-18" },
          { id: 3, title: "Machine Learning Engineer", company: "Anthropic", status: "SAVED", applied_date: "2023-10-20" },
          { id: 4, title: "Software Engineer", company: "Google", status: "OFFER", applied_date: "2023-10-01" },
        ]
      }
    }
  })

  if (isLoading) {
    return <div className="py-12 text-center text-muted-foreground">Loading applications...</div>
  }

  const columns = [
    { title: "Saved", status: "SAVED", color: "border-slate-200 bg-slate-50" },
    { title: "Applied", status: "APPLIED", color: "border-blue-200 bg-blue-50" },
    { title: "Interview", status: "INTERVIEW", color: "border-purple-200 bg-purple-50" },
    { title: "Offer", status: "OFFER", color: "border-green-200 bg-green-50" },
  ]

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-2xl font-bold tracking-tight">Application Tracker</h3>
          <p className="text-muted-foreground">Track all jobs the AI has applied to on your behalf.</p>
        </div>
      </div>

      <div className="flex flex-col lg:flex-row gap-6 overflow-x-auto pb-4">
        {columns.map((col) => {
          const colApps = applications?.filter((a: any) => a.status === col.status) || []
          
          return (
            <div key={col.status} className={`flex-1 min-w-[300px] rounded-xl border p-4 ${col.color}`}>
              <div className="flex justify-between items-center mb-4">
                <h4 className="font-semibold">{col.title}</h4>
                <Badge variant="secondary">{colApps.length}</Badge>
              </div>
              
              <div className="space-y-3">
                {colApps.map((app: any) => (
                  <Card key={app.id} className="cursor-pointer hover:border-primary/50 transition-colors shadow-sm">
                    <CardHeader className="p-4 pb-2">
                      <CardTitle className="text-sm line-clamp-1">{app.title}</CardTitle>
                      <div className="flex items-center text-xs text-muted-foreground mt-1">
                        <Building2 className="mr-1 h-3 w-3" /> {app.company}
                      </div>
                    </CardHeader>
                    <CardContent className="p-4 pt-0 text-xs">
                      <div className="flex items-center justify-between text-muted-foreground mt-2">
                        <div className="flex items-center">
                          <Calendar className="mr-1 h-3 w-3" />
                          {app.applied_date}
                        </div>
                        <div className="flex items-center">
                          <Briefcase className="mr-1 h-3 w-3" />
                          Details
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
                
                {colApps.length === 0 && (
                  <div className="text-center p-4 text-xs text-muted-foreground border-2 border-dashed rounded-lg">
                    No applications
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

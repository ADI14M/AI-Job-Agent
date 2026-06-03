import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { apiClient } from "@/api/client"
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Search, MapPin, DollarSign, Building2, ExternalLink } from "lucide-react"
import { toast } from "sonner"

export default function JobDiscovery() {
  const queryClient = useQueryClient()

  const { data: jobs, isLoading } = useQuery({
    queryKey: ['discovered-jobs'],
    queryFn: async () => {
      const res = await apiClient.get('/jobs/discovery/results')
      return res.data
    }
  })

  const triggerDiscovery = useMutation({
    mutationFn: async () => {
      const res = await apiClient.post('/jobs/discovery/trigger', {
        roles: ["Software Engineer", "AI Engineer"],
        locations: ["Remote", "New York"],
        platforms: ["linkedin", "wellfound"]
      })
      return res.data
    },
    onSuccess: () => {
      toast.success("Job discovery agents have been dispatched!")
      queryClient.invalidateQueries({ queryKey: ['discovered-jobs'] })
    },
    onError: () => {
      toast.error("Failed to trigger job discovery.")
    }
  })

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-2xl font-bold tracking-tight">Job Discovery</h3>
          <p className="text-muted-foreground">Autonomous agents sourcing the web for top matches.</p>
        </div>
        <Button 
          onClick={() => triggerDiscovery.mutate()} 
          disabled={triggerDiscovery.isPending}
          className="bg-indigo-600 hover:bg-indigo-700"
        >
          <Search className="mr-2 h-4 w-4" />
          {triggerDiscovery.isPending ? "Agents Scraping..." : "Run Autonomous Search"}
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {isLoading ? (
          <div className="col-span-full py-12 text-center text-muted-foreground">Loading discovered jobs...</div>
        ) : jobs && jobs.length > 0 ? (
          jobs.map((job: any) => (
            <Card key={job.id} className="hover:shadow-md transition-shadow">
              <CardHeader>
                <div className="flex justify-between items-start">
                  <Badge variant="secondary" className="mb-2">{job.platform}</Badge>
                  {job.match_score && (
                    <Badge className={job.match_score > 80 ? 'bg-green-500' : 'bg-yellow-500'}>
                      {job.match_score}% Match
                    </Badge>
                  )}
                </div>
                <CardTitle className="text-lg line-clamp-2">{job.title}</CardTitle>
                <div className="flex items-center text-sm text-muted-foreground mt-2">
                  <Building2 className="mr-1 h-4 w-4" /> {job.company}
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center">
                    <MapPin className="mr-2 h-4 w-4 text-muted-foreground" />
                    {job.location || "Remote"}
                  </div>
                  <div className="flex items-center">
                    <DollarSign className="mr-2 h-4 w-4 text-muted-foreground" />
                    {job.salary || "Not Disclosed"}
                  </div>
                </div>
                <div className="mt-4 flex gap-2">
                  <Button variant="outline" className="w-full text-xs" onClick={() => window.open(job.url, '_blank')}>
                    <ExternalLink className="mr-2 h-3 w-3" /> View Post
                  </Button>
                  <Button className="w-full text-xs" variant="secondary">
                    Analyze Fit
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))
        ) : (
          <div className="col-span-full py-12 text-center text-muted-foreground">
            No jobs discovered yet. Click "Run Autonomous Search" to begin.
          </div>
        )}
      </div>
    </div>
  )
}

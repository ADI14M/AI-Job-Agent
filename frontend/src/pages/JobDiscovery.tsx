import { useState } from "react"
import { useMutation } from "@tanstack/react-query"
import { apiClient } from "@/api/client"
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Checkbox } from "@/components/ui/checkbox"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Search, MapPin, DollarSign, Building2, ExternalLink, Calendar, Briefcase, Globe } from "lucide-react"
import { toast } from "sonner"

export default function JobDiscovery() {
  const [keywords, setKeywords] = useState("Software Engineer")
  const [location, setLocation] = useState("San Francisco, CA")
  const [experience, setExperience] = useState("")
  const [salary, setSalary] = useState("")
  const [remote, setRemote] = useState(false)
  const [providers, setProviders] = useState<string[]>(["linkedin", "wellfound"])
  
  const [results, setResults] = useState<any>(null)

  const toggleProvider = (p: string) => {
    setProviders(prev => prev.includes(p) ? prev.filter(x => x !== p) : [...prev, p])
  }

  const triggerDiscovery = useMutation({
    mutationFn: async () => {
      const res = await apiClient.post('/job-discovery/search', {
        keywords,
        location,
        experience,
        salary,
        remote,
        providers
      })
      return res.data
    },
    onSuccess: (data) => {
      toast.success(`Discovered ${data.total_found} jobs! (${data.new_jobs} new, ${data.duplicates_removed} duplicates)`)
      setResults(data)
    },
    onError: () => {
      toast.error("Failed to trigger job discovery.")
    }
  })

  return (
    <div className="space-y-6">
      <div className="flex flex-col space-y-4">
        <div>
          <h3 className="text-2xl font-bold tracking-tight">Job Discovery Engine</h3>
          <p className="text-muted-foreground">Autonomous agents sourcing the web for top matches.</p>
        </div>
        
        {/* Search Form */}
        <Card>
          <CardContent className="pt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label>Keywords</Label>
              <Input value={keywords} onChange={e => setKeywords(e.target.value)} placeholder="e.g. React Developer" />
            </div>
            <div className="space-y-2">
              <Label>Location</Label>
              <Input value={location} onChange={e => setLocation(e.target.value)} placeholder="e.g. New York, NY" />
            </div>
            <div className="space-y-2">
              <Label>Experience</Label>
              <Select value={experience} onValueChange={setExperience}>
                <SelectTrigger><SelectValue placeholder="Select Experience" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="Entry-level">Entry-level</SelectItem>
                  <SelectItem value="Mid-level">Mid-level</SelectItem>
                  <SelectItem value="Senior">Senior</SelectItem>
                  <SelectItem value="Lead">Lead</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Target Salary</Label>
              <Input value={salary} onChange={e => setSalary(e.target.value)} placeholder="e.g. $120k" />
            </div>
            
            <div className="space-y-2 md:col-span-2">
              <Label className="mb-2 block">Providers</Label>
              <div className="flex flex-wrap gap-2">
                {["linkedin", "wellfound", "greenhouse", "indeed"].map(p => (
                  <Badge 
                    key={p} 
                    variant={providers.includes(p) ? "default" : "outline"}
                    className="cursor-pointer capitalize"
                    onClick={() => toggleProvider(p)}
                  >
                    {p}
                  </Badge>
                ))}
              </div>
            </div>

            <div className="flex items-center space-x-2 md:col-span-2">
              <Checkbox id="remote" checked={remote} onCheckedChange={(c) => setRemote(c as boolean)} />
              <Label htmlFor="remote">Remote Only</Label>
            </div>

            <div className="md:col-span-3 flex justify-end">
              <Button 
                onClick={() => triggerDiscovery.mutate()} 
                disabled={triggerDiscovery.isPending || providers.length === 0}
                className="bg-indigo-600 hover:bg-indigo-700"
              >
                <Search className="mr-2 h-4 w-4" />
                {triggerDiscovery.isPending ? "Agents Scraping..." : "Run Autonomous Search"}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {results?.summary && (
        <div className="space-y-4">
          <div className="p-4 bg-muted rounded-md flex justify-between items-center">
            <span className="font-semibold">{results.summary}</span>
            <span className="text-sm text-muted-foreground">Found: {results.total_found} | New: {results.new_jobs} | Duplicates: {results.duplicates_removed}</span>
          </div>
          
          {results.provider_statuses && results.provider_statuses.length > 0 && (
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
              {results.provider_statuses.map((ps: any) => (
                <Card key={ps.provider} className="p-3">
                  <div className="font-semibold text-sm mb-1">{ps.provider}</div>
                  <div className="flex items-center text-sm">
                    {ps.status === "success" ? (
                      <span className="text-green-600 font-medium flex items-center">
                        <span className="mr-2">✔</span> {ps.jobs_found} jobs
                      </span>
                    ) : (
                      <span className="text-red-600 font-medium flex items-center line-clamp-1" title={ps.reason}>
                        <span className="mr-2">✖</span> {ps.reason || "Error"}
                      </span>
                    )}
                  </div>
                </Card>
              ))}
            </div>
          )}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {triggerDiscovery.isPending ? (
          <div className="col-span-full py-12 text-center text-muted-foreground">Scraping and analyzing job boards...</div>
        ) : results?.matched_jobs && results.matched_jobs.length > 0 ? (
          results.matched_jobs.map((job: any) => (
            <Card key={job.id} className="hover:shadow-md transition-shadow flex flex-col">
              <CardHeader className="pb-3">
                <div className="flex justify-between items-start mb-2">
                  <div className="flex items-center gap-2">
                    {job.company_logo ? (
                      <img src={job.company_logo} alt={job.company} className="h-6 w-6 object-contain rounded" />
                    ) : (
                      <Building2 className="h-5 w-5 text-muted-foreground" />
                    )}
                    <span className="font-semibold text-sm">{job.company}</span>
                  </div>
                  {job.match_score > 0 && (
                    <Badge className={job.match_score >= 80 ? 'bg-green-500' : 'bg-yellow-500'}>
                      {job.match_score}% Match
                    </Badge>
                  )}
                </div>
                <CardTitle className="text-lg line-clamp-2 leading-tight">{job.title}</CardTitle>
                <div className="flex gap-2 mt-2">
                  <Badge variant="secondary" className="text-[10px] capitalize">{job.source}</Badge>
                  {job.remote && <Badge variant="outline" className="text-[10px]"><Globe className="mr-1 h-3 w-3"/>Remote</Badge>}
                </div>
              </CardHeader>
              <CardContent className="flex-1 flex flex-col justify-between">
                <div className="space-y-2 text-sm">
                  <div className="flex items-center">
                    <MapPin className="mr-2 h-4 w-4 text-muted-foreground" />
                    {job.location || "Location not specified"}
                  </div>
                  <div className="flex items-center">
                    <DollarSign className="mr-2 h-4 w-4 text-muted-foreground" />
                    {job.salary || "Not Disclosed"}
                  </div>
                  <div className="flex items-center">
                    <Briefcase className="mr-2 h-4 w-4 text-muted-foreground" />
                    {job.experience || job.employment_type || "Experience not specified"}
                  </div>
                  {job.posted_date && (
                    <div className="flex items-center">
                      <Calendar className="mr-2 h-4 w-4 text-muted-foreground" />
                      {new Date(job.posted_date).toLocaleDateString()}
                    </div>
                  )}
                  {job.skills && job.skills.length > 0 && (
                    <div className="mt-3 flex flex-wrap gap-1">
                      {job.skills.slice(0, 4).map((s: string) => (
                        <span key={s} className="px-2 py-0.5 bg-muted text-[10px] rounded-full">{s}</span>
                      ))}
                      {job.skills.length > 4 && <span className="text-[10px] text-muted-foreground">+{job.skills.length - 4}</span>}
                    </div>
                  )}
                </div>
                <div className="mt-6 flex gap-2">
                  <Button className="w-full text-xs" onClick={() => window.open(job.url, '_blank')}>
                    <ExternalLink className="mr-2 h-3 w-3" /> Apply Now
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))
        ) : (
          <div className="col-span-full py-12 text-center text-muted-foreground">
            {results ? "No matching jobs found in this search." : "Ready to discover jobs."}
          </div>
        )}
      </div>
    </div>
  )
}

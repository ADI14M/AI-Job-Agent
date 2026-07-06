import { useState, useEffect } from "react"
import { useQuery, useMutation } from "@tanstack/react-query"
import { apiClient } from "@/api/client"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Brain, Search, Briefcase, Activity, Target, AlertCircle } from "lucide-react"

export default function CareerMemory() {
  const [searchQuery, setSearchQuery] = useState("")
  const [searchResults, setSearchResults] = useState<any[]>([])

  const { data: analytics, isLoading: analyticsLoading } = useQuery({
    queryKey: ['career-analytics'],
    queryFn: async () => {
      const res = await apiClient.get('/memory/analytics')
      return res.data
    }
  })

  const searchMutation = useMutation({
    mutationFn: async () => {
      const res = await apiClient.post('/memory/search', {
        query: searchQuery,
        limit: 5
      })
      return res.data
    },
    onSuccess: (data) => {
      setSearchResults(data)
    }
  })

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-2xl font-bold tracking-tight flex items-center">
          <Brain className="mr-2 h-6 w-6 text-indigo-600" /> AI Career Memory
        </h3>
        <p className="text-muted-foreground">Persistent tracking and semantic search of your entire job hunt journey.</p>
      </div>

      {/* Analytics Overview */}
      {analyticsLoading ? (
        <div className="py-8 text-center text-muted-foreground">Loading Analytics...</div>
      ) : analytics ? (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">App Success Rate</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{analytics.application_success_rate}%</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Interview Rate</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{analytics.interview_rate}%</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Offer Rate</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{analytics.offer_rate}%</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Avg ATS Score</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{analytics.average_ats_score}/100</div>
            </CardContent>
          </Card>
        </div>
      ) : null}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Insights */}
        <div className="space-y-6 lg:col-span-1">
          {analytics && (
            <>
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg flex items-center"><AlertCircle className="w-4 h-4 mr-2"/> Missing Skills</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {analytics.most_common_missing_skills.length > 0 ? (
                      analytics.most_common_missing_skills.map((skill: string) => (
                        <span key={skill} className="px-2 py-1 bg-red-100 text-red-800 text-xs rounded-full">{skill}</span>
                      ))
                    ) : (
                      <span className="text-sm text-muted-foreground">Not enough data.</span>
                    )}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg flex items-center"><Target className="w-4 h-4 mr-2"/> Top Targeted Companies</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2 text-sm">
                    {analytics.most_targeted_companies.length > 0 ? (
                      analytics.most_targeted_companies.map((company: string, idx: number) => (
                        <li key={idx} className="flex items-center"><Briefcase className="w-3 h-3 mr-2 text-muted-foreground"/> {company}</li>
                      ))
                    ) : (
                      <span className="text-muted-foreground">No companies targeted yet.</span>
                    )}
                  </ul>
                </CardContent>
              </Card>
            </>
          )}
        </div>

        {/* Right Column: Semantic Search */}
        <div className="lg:col-span-2 space-y-4">
          <Card className="h-full">
            <CardHeader>
              <CardTitle>Semantic Memory Search</CardTitle>
              <p className="text-sm text-muted-foreground">Ask anything about your past applications, e.g., "Which resume worked best?" or "Show all Nvidia applications."</p>
            </CardHeader>
            <CardContent>
              <div className="flex gap-2 mb-6">
                <Input 
                  value={searchQuery} 
                  onChange={e => setSearchQuery(e.target.value)} 
                  placeholder="Query your career memory..."
                  onKeyDown={e => e.key === 'Enter' && searchMutation.mutate()}
                />
                <Button onClick={() => searchMutation.mutate()} disabled={searchMutation.isPending || !searchQuery}>
                  <Search className="w-4 h-4 mr-2" />
                  Search
                </Button>
              </div>

              <div className="space-y-4">
                {searchMutation.isPending && <div className="text-center py-4 text-muted-foreground">Searching vector database...</div>}
                
                {searchResults.length > 0 ? (
                  searchResults.map((result, idx) => (
                    <div key={idx} className="p-4 border rounded-md bg-muted/20">
                      <div className="flex justify-between items-start mb-2">
                        <span className="font-semibold text-sm text-indigo-600">{result.event_type}</span>
                        <span className="text-xs text-muted-foreground">Sim: {(result.similarity).toFixed(2)}</span>
                      </div>
                      <p className="text-sm">{result.description}</p>
                    </div>
                  ))
                ) : searchMutation.isSuccess ? (
                  <div className="text-center py-4 text-muted-foreground">No relevant memories found.</div>
                ) : (
                  <div className="text-center py-12 text-muted-foreground opacity-50">
                    <Brain className="w-12 h-12 mx-auto mb-4" />
                    Waiting for query...
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

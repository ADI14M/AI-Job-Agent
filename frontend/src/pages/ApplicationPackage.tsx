import { useState } from "react"
import { useMutation } from "@tanstack/react-query"
import { apiClient } from "@/api/client"
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { FileText, Download, Briefcase, Target, CheckCircle2, XCircle } from "lucide-react"
import { toast } from "sonner"
import { Input } from "@/components/ui/input"

export default function ApplicationPackage() {
  const [jobId, setJobId] = useState("1")
  const [resumeId, setResumeId] = useState("1")
  const [results, setResults] = useState<any>(null)

  const triggerEngine = useMutation({
    mutationFn: async () => {
      const res = await apiClient.post('/decision/run', {
        job_id: parseInt(jobId),
        resume_id: parseInt(resumeId)
      })
      return res.data.data
    },
    onSuccess: (data) => {
      toast.success("AI Decision Engine completed analysis.")
      setResults(data)
    },
    onError: () => {
      toast.error("Failed to run Decision Engine.")
    }
  })

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-2xl font-bold tracking-tight">AI Decision Engine</h3>
          <p className="text-muted-foreground">Analyze fit, optimize resume, and generate application packages.</p>
        </div>
      </div>

      <Card>
        <CardContent className="pt-6 flex gap-4 items-end">
          <div className="space-y-2 flex-1">
            <label className="text-sm font-medium">Job ID</label>
            <Input type="number" value={jobId} onChange={e => setJobId(e.target.value)} />
          </div>
          <div className="space-y-2 flex-1">
            <label className="text-sm font-medium">Resume ID</label>
            <Input type="number" value={resumeId} onChange={e => setResumeId(e.target.value)} />
          </div>
          <Button 
            onClick={() => triggerEngine.mutate()} 
            disabled={triggerEngine.isPending}
            className="w-48 bg-indigo-600 hover:bg-indigo-700"
          >
            {triggerEngine.isPending ? "Analyzing..." : "Run Engine"}
          </Button>
        </CardContent>
      </Card>

      {triggerEngine.isPending && (
        <div className="py-12 text-center text-muted-foreground">
          Running Semantic Match, ATS Analysis, Skill Gap, Resume Optimization, and Cover Letter Generation...
        </div>
      )}

      {results && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column: Decision & ATS */}
          <div className="space-y-6 lg:col-span-1">
            <Card className="border-indigo-100 shadow-sm">
              <CardHeader className="bg-indigo-50/50 pb-4">
                <div className="flex justify-between items-center">
                  <CardTitle>Recommendation</CardTitle>
                  <Badge className={
                    results.decision.recommendation === 'Apply' ? 'bg-green-500' :
                    results.decision.recommendation === 'Maybe' ? 'bg-yellow-500' : 'bg-red-500'
                  }>
                    {results.decision.recommendation}
                  </Badge>
                </div>
                <p className="text-sm text-muted-foreground mt-2">{results.decision.reasoning}</p>
              </CardHeader>
              <CardContent className="pt-4 space-y-4">
                <div>
                  <h4 className="text-sm font-semibold flex items-center mb-2"><CheckCircle2 className="w-4 h-4 mr-2 text-green-500"/> Pros</h4>
                  <ul className="text-sm text-muted-foreground list-disc pl-5">
                    {results.decision.pros.map((p: string, i: number) => <li key={i}>{p}</li>)}
                  </ul>
                </div>
                <div>
                  <h4 className="text-sm font-semibold flex items-center mb-2"><XCircle className="w-4 h-4 mr-2 text-red-500"/> Cons</h4>
                  <ul className="text-sm text-muted-foreground list-disc pl-5">
                    {results.decision.cons.map((p: string, i: number) => <li key={i}>{p}</li>)}
                  </ul>
                </div>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="bg-muted p-2 rounded">Interview Prob: {results.decision.estimated_interview_probability}</div>
                  <div className="bg-muted p-2 rounded">Skill Match: {results.decision.estimated_skill_match}</div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex justify-between">
                  ATS Score 
                  <span className={results.ats_evaluation.overall_score >= 80 ? 'text-green-500' : 'text-yellow-500'}>
                    {results.ats_evaluation.overall_score}/100
                  </span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between"><span>Keywords</span><span>{results.ats_evaluation.keywords_score}</span></div>
                  <div className="flex justify-between"><span>Experience</span><span>{results.ats_evaluation.experience_score}</span></div>
                  <div className="flex justify-between"><span>Skills</span><span>{results.ats_evaluation.skills_score}</span></div>
                  <div className="flex justify-between"><span>Formatting</span><span>{results.ats_evaluation.formatting_score}</span></div>
                </div>
                {results.ats_evaluation.deductions.length > 0 && (
                  <div className="mt-4 pt-4 border-t text-sm">
                    <strong>Deductions:</strong>
                    <ul className="list-disc pl-5 text-muted-foreground mt-1">
                      {results.ats_evaluation.deductions.map((d: string, i: number) => <li key={i}>{d}</li>)}
                    </ul>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Skill Gap</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <h4 className="text-sm font-medium mb-1">Missing Skills</h4>
                    <div className="flex flex-wrap gap-1">
                      {results.skill_gap.missing_skills.map((s: string) => (
                        <Badge key={s} variant="destructive">{s}</Badge>
                      ))}
                    </div>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium mb-1">Learning Path ({results.skill_gap.estimated_learning_time})</h4>
                    <ul className="text-xs text-muted-foreground list-disc pl-4">
                      {results.skill_gap.recommended_learning_path.map((p: string, i: number) => <li key={i}>{p}</li>)}
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right Column: Documents */}
          <div className="lg:col-span-2">
            <Card className="h-full flex flex-col">
              <CardHeader>
                <CardTitle className="flex justify-between items-center">
                  Application Package
                  {results.files?.resume_pdf && (
                    <div className="flex gap-2">
                      <Button size="sm" variant="outline" onClick={() => window.open(`http://localhost:8000/${results.files.resume_pdf}`, '_blank')}>
                        <Download className="w-4 h-4 mr-2" /> Resume
                      </Button>
                      <Button size="sm" variant="outline" onClick={() => window.open(`http://localhost:8000/${results.files.cover_letter_pdf}`, '_blank')}>
                        <Download className="w-4 h-4 mr-2" /> Cover Letter
                      </Button>
                    </div>
                  )}
                </CardTitle>
              </CardHeader>
              <CardContent className="flex-1">
                {results.decision.recommendation === 'Skip' ? (
                  <div className="h-full flex items-center justify-center text-muted-foreground">
                    Documents not generated because recommendation is Skip.
                  </div>
                ) : (
                  <Tabs defaultValue="resume" className="h-full">
                    <TabsList className="grid w-full grid-cols-2">
                      <TabsTrigger value="resume">Optimized Resume</TabsTrigger>
                      <TabsTrigger value="cover_letter">Cover Letter</TabsTrigger>
                    </TabsList>
                    <TabsContent value="resume" className="p-4 bg-muted/30 rounded-md mt-4 min-h-[500px] whitespace-pre-wrap font-mono text-sm">
                      {results.optimized_resume}
                    </TabsContent>
                    <TabsContent value="cover_letter" className="p-4 bg-muted/30 rounded-md mt-4 min-h-[500px] whitespace-pre-wrap font-mono text-sm">
                      {results.cover_letter}
                    </TabsContent>
                  </Tabs>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      )}
    </div>
  )
}

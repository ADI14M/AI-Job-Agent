import { useState } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { apiClient } from "@/api/client"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { UploadCloud, FileText, Download, Trash2, Eye } from "lucide-react"
import { toast } from "sonner"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"

export default function Resumes() {
  const [file, setFile] = useState<File | null>(null)
  const queryClient = useQueryClient()

  // Fetch Resumes
  const { data: resumes, isLoading } = useQuery({
    queryKey: ['resumes'],
    queryFn: async () => {
      // Assuming a GET endpoint exists or will exist. 
      // If not, we'll mock it for now.
      try {
        const res = await apiClient.get('/resume')
        return res.data
      } catch (e) {
        return []
      }
    }
  })

  // Upload Mutation
  const uploadMutation = useMutation({
    mutationFn: async (fileToUpload: File) => {
      const formData = new FormData()
      formData.append('file', fileToUpload)
      const res = await apiClient.post('/resume/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      return res.data
    },
    onSuccess: () => {
      toast.success("Resume uploaded and parsed successfully!")
      queryClient.invalidateQueries({ queryKey: ['resumes'] })
      setFile(null)
    },
    onError: () => {
      toast.error("Failed to upload resume. Please try again.")
    }
  })

  const handleUpload = (e: React.FormEvent) => {
    e.preventDefault()
    if (file) {
      uploadMutation.mutate(file)
    }
  }

  // Delete Mutation
  const deleteMutation = useMutation({
    mutationFn: async (id: number) => {
      const res = await apiClient.delete(`/resume/${id}`)
      return res.data
    },
    onSuccess: () => {
      toast.success("Resume deleted successfully")
      queryClient.invalidateQueries({ queryKey: ['resumes'] })
    },
    onError: () => {
      toast.error("Failed to delete resume. Please try again.")
    }
  })

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-2xl font-bold tracking-tight">Resumes & Documents</h3>
        <p className="text-muted-foreground">Manage your resumes and parsed profiles.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Upload New Resume</CardTitle>
          <CardDescription>Upload a PDF or DOCX file to let our AI agents extract and vectorize your profile.</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleUpload} className="flex items-center gap-4">
            <div className="grid w-full max-w-sm items-center gap-1.5">
              <Input 
                id="resume" 
                type="file" 
                accept=".pdf,.docx"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
              />
            </div>
            <Button type="submit" disabled={!file || uploadMutation.isPending}>
              {uploadMutation.isPending ? (
                "Processing AI Extraction..."
              ) : (
                <>
                  <UploadCloud className="mr-2 h-4 w-4" /> Upload
                </>
              )}
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Document Library</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="py-8 text-center text-muted-foreground">Loading resumes...</div>
          ) : resumes && resumes.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>File Name</TableHead>
                  <TableHead>Parsed Name</TableHead>
                  <TableHead>Skills Extracted</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {resumes.map((r: any) => (
                  <TableRow key={r.id}>
                    <TableCell className="font-medium flex items-center gap-2">
                      <FileText className="h-4 w-4 text-blue-500" />
                      {r.filename}
                    </TableCell>
                    <TableCell>{r.parsed_data?.name || "Unknown"}</TableCell>
                    <TableCell>
                      <div className="flex gap-1 flex-wrap">
                        {r.parsed_data?.skills?.slice(0, 3).map((s: string) => (
                          <Badge variant="secondary" key={s}>{s}</Badge>
                        ))}
                        {(r.parsed_data?.skills?.length || 0) > 3 && (
                          <Badge variant="outline">+{r.parsed_data.skills.length - 3}</Badge>
                        )}
                      </div>
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button variant="ghost" size="icon" title="View">
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="icon" title="Download Original">
                          <Download className="h-4 w-4" />
                        </Button>
                        
                        <AlertDialog>
                          <AlertDialogTrigger asChild>
                            <Button variant="ghost" size="icon" className="text-red-500 hover:text-red-600 hover:bg-red-100" title="Delete">
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </AlertDialogTrigger>
                          <AlertDialogContent>
                            <AlertDialogHeader>
                              <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
                              <AlertDialogDescription>
                                This action cannot be undone. This will permanently delete <strong>{r.filename}</strong> (Parsed as: {r.parsed_data?.name || "Unknown"}) and remove all its data including ATS evaluations, cover letters, and generated packages from our servers.
                              </AlertDialogDescription>
                            </AlertDialogHeader>
                            <AlertDialogFooter>
                              <AlertDialogCancel>Cancel</AlertDialogCancel>
                              <AlertDialogAction 
                                onClick={() => deleteMutation.mutate(r.id)}
                                className="bg-red-500 hover:bg-red-600"
                                disabled={deleteMutation.isPending}
                              >
                                Delete Resume
                              </AlertDialogAction>
                            </AlertDialogFooter>
                          </AlertDialogContent>
                        </AlertDialog>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <div className="py-12 text-center text-muted-foreground">
              No resumes uploaded yet.
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

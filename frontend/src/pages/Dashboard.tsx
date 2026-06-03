import { useQuery } from "@tanstack/react-query"
import { apiClient } from "@/api/client"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line
} from 'recharts'
import { Briefcase, Send, Users, Target, Activity } from "lucide-react"

export default function Dashboard() {
  // Use mock data if API is not yet ready, but try to fetch
  const { data: analytics, isLoading } = useQuery({
    queryKey: ['analytics'],
    queryFn: async () => {
      try {
        const res = await apiClient.get('/analytics/dashboard')
        return res.data
      } catch (e) {
        return {
          total_applications: 124,
          interviews: 12,
          offers: 3,
          conversion_rate: 9.6,
          funnelData: [
            { name: 'Discovered', count: 450 },
            { name: 'Matched', count: 210 },
            { name: 'Applied', count: 124 },
            { name: 'Interviews', count: 12 },
            { name: 'Offers', count: 3 },
          ],
          activityData: [
            { date: 'Mon', applications: 4 },
            { date: 'Tue', applications: 12 },
            { date: 'Wed', applications: 8 },
            { date: 'Thu', applications: 15 },
            { date: 'Fri', applications: 22 },
            { date: 'Sat', applications: 5 },
            { date: 'Sun', applications: 3 },
          ]
        }
      }
    }
  })

  if (isLoading || !analytics) {
    return <div className="py-12 text-center">Loading Analytics...</div>
  }

  const statCards = [
    { title: "Total Applied", value: analytics.total_applications, icon: Send, color: "text-blue-500" },
    { title: "Interviews", value: analytics.interviews, icon: Users, color: "text-indigo-500" },
    { title: "Offers", value: analytics.offers, icon: Briefcase, color: "text-green-500" },
    { title: "Conversion Rate", value: `${analytics.conversion_rate}%`, icon: Target, color: "text-purple-500" },
  ]

  return (
    <div className="space-y-8">
      <div>
        <h3 className="text-2xl font-bold tracking-tight">Analytics Overview</h3>
        <p className="text-muted-foreground">Monitor your AI Job Agent's performance.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {statCards.map((stat, i) => (
          <Card key={i}>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {stat.title}
              </CardTitle>
              <stat.icon className={`h-4 w-4 ${stat.color}`} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <Card className="col-span-4">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-4 w-4 text-primary" /> Application Activity
            </CardTitle>
          </CardHeader>
          <CardContent className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={analytics.activityData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" />
                <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{fill: '#6b7280', fontSize: 12}} />
                <YAxis axisLine={false} tickLine={false} tick={{fill: '#6b7280', fontSize: 12}} />
                <Tooltip 
                  contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                />
                <Line type="monotone" dataKey="applications" stroke="#6366f1" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 6 }} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card className="col-span-3">
          <CardHeader>
            <CardTitle>Conversion Funnel</CardTitle>
          </CardHeader>
          <CardContent className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={analytics.funnelData} layout="vertical" margin={{ top: 0, right: 0, left: 20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e5e7eb" />
                <XAxis type="number" axisLine={false} tickLine={false} tick={{fill: '#6b7280', fontSize: 12}} />
                <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{fill: '#374151', fontSize: 13, fontWeight: 500}} />
                <Tooltip 
                  cursor={{fill: '#f3f4f6'}}
                  contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                />
                <Bar dataKey="count" fill="#8b5cf6" radius={[0, 4, 4, 0]} barSize={24} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

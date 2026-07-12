import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'

export default function Analytics() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      <div className="container mx-auto px-6 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Analytics</h1>
          <p className="text-gray-400">Detailed threat analytics and insights</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card className="glass-card">
            <CardHeader>
              <CardTitle className="text-white">Threat Trend</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-64 flex items-center justify-center bg-slate-800/50 rounded-lg">
                <p className="text-gray-400">Chart placeholder</p>
              </div>
            </CardContent>
          </Card>

          <Card className="glass-card">
            <CardHeader>
              <CardTitle className="text-white">Category Distribution</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-64 flex items-center justify-center bg-slate-800/50 rounded-lg">
                <p className="text-gray-400">Chart placeholder</p>
              </div>
            </CardContent>
          </Card>

          <Card className="glass-card md:col-span-2">
            <CardHeader>
              <CardTitle className="text-white">Threat Heatmap</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-64 flex items-center justify-center bg-slate-800/50 rounded-lg">
                <p className="text-gray-400">Heatmap placeholder</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

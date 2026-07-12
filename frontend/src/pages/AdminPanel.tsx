import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'

export default function AdminPanel() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      <div className="container mx-auto px-6 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Admin Panel</h1>
          <p className="text-gray-400">Manage users, AI models, and system settings</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="glass-card">
            <CardHeader>
              <CardTitle className="text-white">Users</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-white">1,234</div>
              <p className="text-sm text-gray-400 mt-1">Total registered users</p>
            </CardContent>
          </Card>

          <Card className="glass-card">
            <CardHeader>
              <CardTitle className="text-white">Scans Today</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-white">567</div>
              <p className="text-sm text-gray-400 mt-1">Scans performed today</p>
            </CardContent>
          </Card>

          <Card className="glass-card">
            <CardHeader>
              <CardTitle className="text-white">System Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-400">Operational</div>
              <p className="text-sm text-gray-400 mt-1">All systems running</p>
            </CardContent>
          </Card>
        </div>

        <Card className="glass-card mt-8">
          <CardHeader>
            <CardTitle className="text-white">Recent Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="p-4 bg-slate-800/50 rounded-lg">
                <div className="text-white">New user registered: john@example.com</div>
                <div className="text-sm text-gray-400">2 minutes ago</div>
              </div>
              <div className="p-4 bg-slate-800/50 rounded-lg">
                <div className="text-white">High-risk threat detected</div>
                <div className="text-sm text-gray-400">15 minutes ago</div>
              </div>
              <div className="p-4 bg-slate-800/50 rounded-lg">
                <div className="text-white">System backup completed</div>
                <div className="text-sm text-gray-400">1 hour ago</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

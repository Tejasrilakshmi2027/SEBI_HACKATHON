import { Link } from 'react-router-dom'
import { Shield, Upload, History, BarChart3, Bell, LogOut, Settings, User } from 'lucide-react'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { useAuth } from '../context/AuthContext'

export default function Dashboard() {
  const { user, logout } = useAuth()

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      {/* Navigation */}
      <nav className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Shield className="h-8 w-8 text-blue-400" />
            <span className="text-2xl font-bold text-white">SEBI Sentinel AI</span>
          </div>
          <div className="flex items-center space-x-4">
            <Link to="/upload">
              <Button className="bg-blue-600 hover:bg-blue-700">
                <Upload className="mr-2 h-4 w-4" />
                New Scan
              </Button>
            </Link>
            <Button variant="ghost" className="text-white" onClick={logout}>
              <LogOut className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            Welcome back, {user?.full_name || 'User'}
          </h1>
          <p className="text-gray-400">Monitor your security scans and threat analytics</p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="glass-card">
            <CardHeader className="pb-3">
              <CardTitle className="text-white text-sm font-medium">Total Scans</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-white">247</div>
              <p className="text-xs text-gray-400 mt-1">+12% from last month</p>
            </CardContent>
          </Card>
          <Card className="glass-card">
            <CardHeader className="pb-3">
              <CardTitle className="text-white text-sm font-medium">High Risk</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-red-400">23</div>
              <p className="text-xs text-gray-400 mt-1">Requires attention</p>
            </CardContent>
          </Card>
          <Card className="glass-card">
            <CardHeader className="pb-3">
              <CardTitle className="text-white text-sm font-medium">Avg Trust Score</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-400">78.5</div>
              <p className="text-xs text-gray-400 mt-1">Out of 100</p>
            </CardContent>
          </Card>
          <Card className="glass-card">
            <CardHeader className="pb-3">
              <CardTitle className="text-white text-sm font-medium">Threats Blocked</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-blue-400">156</div>
              <p className="text-xs text-gray-400 mt-1">This month</p>
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Link to="/upload">
            <Card className="glass-card hover:bg-blue-600/20 transition-colors cursor-pointer">
              <CardHeader>
                <Upload className="h-12 w-12 text-blue-400 mb-2" />
                <CardTitle className="text-white">Upload & Scan</CardTitle>
                <CardDescription className="text-gray-400">
                  Upload files or URLs for security analysis
                </CardDescription>
              </CardHeader>
            </Card>
          </Link>
          <Link to="/history">
            <Card className="glass-card hover:bg-blue-600/20 transition-colors cursor-pointer">
              <CardHeader>
                <History className="h-12 w-12 text-blue-400 mb-2" />
                <CardTitle className="text-white">Scan History</CardTitle>
                <CardDescription className="text-gray-400">
                  View your past scans and results
                </CardDescription>
              </CardHeader>
            </Card>
          </Link>
          <Link to="/analytics">
            <Card className="glass-card hover:bg-blue-600/20 transition-colors cursor-pointer">
              <CardHeader>
                <BarChart3 className="h-12 w-12 text-blue-400 mb-2" />
                <CardTitle className="text-white">Analytics</CardTitle>
                <CardDescription className="text-gray-400">
                  Detailed threat analytics and insights
                </CardDescription>
              </CardHeader>
            </Card>
          </Link>
        </div>

        {/* Recent Scans */}
        <Card className="glass-card">
          <CardHeader>
            <CardTitle className="text-white">Recent Scans</CardTitle>
            <CardDescription className="text-gray-400">Your latest security scans</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                { type: 'Email', name: 'suspicious_offer.eml', risk: 'High', score: 35, time: '2 hours ago' },
                { type: 'URL', name: 'https://fake-sebi.com', risk: 'Critical', score: 15, time: '5 hours ago' },
                { type: 'PDF', name: 'investment_guide.pdf', risk: 'Low', score: 92, time: '1 day ago' },
                { type: 'Image', name: 'broker_photo.jpg', risk: 'Medium', score: 65, time: '2 days ago' },
              ].map((scan, index) => (
                <div key={index} className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg">
                  <div className="flex items-center space-x-4">
                    <div className="w-10 h-10 rounded-full bg-blue-600/20 flex items-center justify-center">
                      <Shield className="h-5 w-5 text-blue-400" />
                    </div>
                    <div>
                      <div className="text-white font-medium">{scan.name}</div>
                      <div className="text-sm text-gray-400">{scan.type} • {scan.time}</div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="text-right">
                      <div className={`text-sm font-medium ${
                        scan.risk === 'Critical' ? 'text-red-400' :
                        scan.risk === 'High' ? 'text-orange-400' :
                        scan.risk === 'Medium' ? 'text-yellow-400' :
                        'text-green-400'
                      }`}>
                        {scan.risk} Risk
                      </div>
                      <div className="text-sm text-gray-400">Score: {scan.score}</div>
                    </div>
                    <Link to={`/scan/${index + 1}`}>
                      <Button variant="outline" size="sm" className="border-blue-400 text-white">
                        View
                      </Button>
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  )
}

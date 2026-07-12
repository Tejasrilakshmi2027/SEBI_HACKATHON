import { Link } from 'react-router-dom'
import { Search, Filter, Download } from 'lucide-react'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import { Input } from '../components/ui/input'

export default function ScanHistory() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      <div className="container mx-auto px-6 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Scan History</h1>
          <p className="text-gray-400">View and manage your past security scans</p>
        </div>

        {/* Filters */}
        <Card className="glass-card mb-8">
          <CardContent className="pt-6">
            <div className="flex space-x-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                <Input
                  placeholder="Search scans..."
                  className="pl-10 bg-slate-800 border-slate-700 text-white"
                />
              </div>
              <Button variant="outline" className="border-blue-400 text-white">
                <Filter className="mr-2 h-4 w-4" />
                Filter
              </Button>
              <Button variant="outline" className="border-blue-400 text-white">
                <Download className="mr-2 h-4 w-4" />
                Export
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* History List */}
        <Card className="glass-card">
          <CardHeader>
            <CardTitle className="text-white">All Scans</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                { type: 'Email', name: 'suspicious_offer.eml', risk: 'High', score: 35, date: '2024-01-15' },
                { type: 'URL', name: 'https://fake-sebi.com', risk: 'Critical', score: 15, date: '2024-01-14' },
                { type: 'PDF', name: 'investment_guide.pdf', risk: 'Low', score: 92, date: '2024-01-13' },
                { type: 'Image', name: 'broker_photo.jpg', risk: 'Medium', score: 65, date: '2024-01-12' },
                { type: 'Video', name: 'investment_video.mp4', risk: 'Low', score: 88, date: '2024-01-11' },
              ].map((scan, index) => (
                <Link key={index} to={`/scan/${index + 1}`}>
                  <div className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg hover:bg-slate-800 transition-colors cursor-pointer">
                    <div className="flex items-center space-x-4">
                      <div className="w-10 h-10 rounded-full bg-blue-600/20 flex items-center justify-center text-blue-400 font-bold">
                        {scan.type[0]}
                      </div>
                      <div>
                        <div className="text-white font-medium">{scan.name}</div>
                        <div className="text-sm text-gray-400">{scan.type} • {scan.date}</div>
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
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

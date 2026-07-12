import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import { Button } from '../components/ui/button'
import { Download, FileText } from 'lucide-react'

export default function Reports() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      <div className="container mx-auto px-6 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Reports</h1>
          <p className="text-gray-400">Generate and download security reports</p>
        </div>

        <Card className="glass-card">
          <CardHeader>
            <CardTitle className="text-white">Generate Report</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <FileText className="h-8 w-8 text-blue-400" />
                  <div>
                    <div className="text-white font-medium">Monthly Summary Report</div>
                    <div className="text-sm text-gray-400">Comprehensive monthly analysis</div>
                  </div>
                </div>
                <Button className="bg-blue-600 hover:bg-blue-700">
                  <Download className="mr-2 h-4 w-4" />
                  Generate
                </Button>
              </div>

              <div className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <FileText className="h-8 w-8 text-blue-400" />
                  <div className>
                    <div className="text-white font-medium">Threat Analysis Report</div>
                    <div className="text-sm text-gray-400">Detailed threat breakdown</div>
                  </div>
                </div>
                <Button className="bg-blue-600 hover:bg-blue-700">
                  <Download className="mr-2 h-4 w-4" />
                  Generate
                </Button>
              </div>

              <div className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <FileText className="h-8 w-8 text-blue-400" />
                  <div className>
                    <div className="text-white font-medium">Audit Report</div>
                    <div className="text-sm text-gray-400">Security audit findings</div>
                  </div>
                </div>
                <Button className="bg-blue-600 hover:bg-blue-700">
                  <Download className="mr-2 h-4 w-4" />
                  Generate
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

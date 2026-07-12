import { Link } from 'react-router-dom'
import { Shield, AlertTriangle, CheckCircle, ArrowLeft, Download, Share2 } from 'lucide-react'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'

export default function ScanResult() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      <div className="container mx-auto px-6 py-8">
        <Link to="/dashboard">
          <Button variant="ghost" className="text-white mb-6">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Dashboard
          </Button>
        </Link>

        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Scan Results</h1>
          <p className="text-gray-400">Detailed analysis of your uploaded content</p>
        </div>

        {/* Trust Score */}
        <Card className="glass-card mb-8">
          <CardHeader>
            <CardTitle className="text-white">Trust Score</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-center">
              <div className="relative w-48 h-48">
                <div className="absolute inset-0 rounded-full border-8 border-slate-700"></div>
                <div className="absolute inset-0 rounded-full border-8 border-red-500 border-t-transparent border-l-transparent transform -rotate-45"></div>
                <div className="absolute inset-4 rounded-full bg-slate-800 flex items-center justify-center">
                  <div className="text-center">
                    <div className="text-4xl font-bold text-white">35</div>
                    <div className="text-sm text-gray-400">out of 100</div>
                  </div>
                </div>
              </div>
            </div>
            <div className="text-center mt-4">
              <span className="inline-flex items-center px-4 py-2 rounded-full bg-red-500/20 text-red-400">
                <AlertTriangle className="mr-2 h-4 w-4" />
                High Risk
              </span>
            </div>
          </CardContent>
        </Card>

        {/* Evidence */}
        <Card className="glass-card mb-8">
          <CardHeader>
            <CardTitle className="text-white">Evidence</CardTitle>
            <CardDescription className="text-gray-400">
              Suspicious patterns detected
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {[
                'Suspicious sender domain detected',
                'Urgency keywords found in subject line',
                'Non-HTTPS link detected',
                'Typosquatting attempt identified',
              ].map((evidence, index) => (
                <div key={index} className="flex items-center space-x-3 p-3 bg-red-500/10 rounded-lg">
                  <AlertTriangle className="h-5 w-5 text-red-400" />
                  <span className="text-white">{evidence}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Recommendations */}
        <Card className="glass-card mb-8">
          <CardHeader>
            <CardTitle className="text-white">Recommendations</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {[
                'Do not click on any links in this email',
                'Verify the sender through official channels',
                'Report this to your IT security team',
                'Delete the email immediately',
              ].map((recommendation, index) => (
                <div key={index} className="flex items-center space-x-3 p-3 bg-blue-500/10 rounded-lg">
                  <CheckCircle className="h-5 w-5 text-blue-400" />
                  <span className="text-white">{recommendation}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Actions */}
        <div className="flex space-x-4">
          <Button className="bg-blue-600 hover:bg-blue-700">
            <Download className="mr-2 h-4 w-4" />
            Download Report
          </Button>
          <Button variant="outline" className="border-blue-400 text-white">
            <Share2 className="mr-2 h-4 w-4" />
            Share
          </Button>
        </div>
      </div>
    </div>
  )
}

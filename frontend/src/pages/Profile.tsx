import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import { Input } from '../components/ui/input'
import { Label } from '../components/ui/label'
import { Button } from '../components/ui/button'
import { useAuth } from '../context/AuthContext'

export default function Profile() {
  const { user } = useAuth()

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      <div className="container mx-auto px-6 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Profile</h1>
          <p className="text-gray-400">Manage your account settings</p>
        </div>

        <Card className="glass-card max-w-2xl">
          <CardHeader>
            <CardTitle className="text-white">Account Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label className="text-white">Full Name</Label>
              <Input value={user?.full_name || ''} className="bg-slate-800 border-slate-700 text-white" />
            </div>
            <div className="space-y-2">
              <Label className="text-white">Email</Label>
              <Input value={user?.email || ''} className="bg-slate-800 border-slate-700 text-white" disabled />
            </div>
            <div className="space-y-2">
              <Label className="text-white">Username</Label>
              <Input value={user?.username || ''} className="bg-slate-800 border-slate-700 text-white" />
            </div>
            <div className="space-y-2">
              <Label className="text-white">Organization</Label>
              <Input placeholder="Your organization" className="bg-slate-800 border-slate-700 text-white" />
            </div>
            <Button className="bg-blue-600 hover:bg-blue-700">Save Changes</Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

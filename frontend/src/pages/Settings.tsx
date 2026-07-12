import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import { Button } from '../components/ui/button'
import { useTheme } from '../context/ThemeContext'
import { useAuth } from '../context/AuthContext'

export default function Settings() {
  const { theme, toggleTheme } = useTheme()
  const { logout } = useAuth()

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      <div className="container mx-auto px-6 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Settings</h1>
          <p className="text-gray-400">Configure your preferences</p>
        </div>

        <div className="space-y-6 max-w-2xl">
          <Card className="glass-card">
            <CardHeader>
              <CardTitle className="text-white">Appearance</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-white font-medium">Dark Mode</div>
                  <div className="text-sm text-gray-400">Toggle dark/light theme</div>
                </div>
                <Button
                  onClick={toggleTheme}
                  variant="outline"
                  className="border-blue-400 text-white"
                >
                  {theme === 'dark' ? 'Light' : 'Dark'}
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card className="glass-card">
            <CardHeader>
              <CardTitle className="text-white">Notifications</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-white font-medium">Email Notifications</div>
                    <div className="text-sm text-gray-400">Receive email alerts</div>
                  </div>
                  <Button variant="outline" className="border-blue-400 text-white">
                    Enabled
                  </Button>
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-white font-medium">Push Notifications</div>
                    <div className="text-sm text-gray-400">Browser notifications</div>
                  </div>
                  <Button variant="outline" className="border-blue-400 text-white">
                    Enabled
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="glass-card">
            <CardHeader>
              <CardTitle className="text-white">Account</CardTitle>
            </CardHeader>
            <CardContent>
              <Button
                onClick={logout}
                variant="destructive"
                className="w-full"
              >
                Sign Out
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

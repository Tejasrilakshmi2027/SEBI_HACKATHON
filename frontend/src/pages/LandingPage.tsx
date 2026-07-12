import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Shield, Zap, Lock, BarChart3, Globe, Users, ArrowRight, CheckCircle } from 'lucide-react'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'

export default function LandingPage() {
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
            <Link to="/login">
              <Button variant="ghost" className="text-white hover:text-blue-400">
                Login
              </Button>
            </Link>
            <Link to="/signup">
              <Button className="bg-blue-600 hover:bg-blue-700">
                Get Started
              </Button>
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="container mx-auto px-6 py-20">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center max-w-4xl mx-auto"
        >
          <h1 className="text-5xl md:text-7xl font-bold text-white mb-6">
            AI-Powered{' '}
            <span className="bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
              Fraud Detection
            </span>{' '}
            for Securities Markets
          </h1>
          <p className="text-xl text-gray-300 mb-8">
            Protect retail investors, brokers, and regulators from AI-generated fraud,
            deepfakes, phishing attacks, and synthetic media in the securities ecosystem.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/signup">
              <Button size="lg" className="bg-blue-600 hover:bg-blue-700 text-lg px-8">
                Start Free Trial
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
            <Button size="lg" variant="outline" className="border-blue-400 text-white hover:bg-blue-400/10">
              Watch Demo
            </Button>
          </div>
        </motion.div>
      </section>

      {/* Stats Section */}
      <section className="container mx-auto px-6 py-16">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {[
            { icon: Shield, label: 'Threats Detected', value: '10M+' },
            { icon: Users, label: 'Active Users', value: '50K+' },
            { icon: Globe, label: 'Organizations', value: '500+' },
            { icon: Zap, label: 'Scan Speed', value: '< 2s' },
          ].map((stat, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="text-center"
            >
              <stat.icon className="h-12 w-12 text-blue-400 mx-auto mb-4" />
              <div className="text-3xl font-bold text-white">{stat.value}</div>
              <div className="text-gray-400">{stat.label}</div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-6 py-20">
        <h2 className="text-4xl font-bold text-white text-center mb-12">
          Comprehensive Fraud Detection
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {[
            {
              icon: Shield,
              title: 'Email Phishing Detection',
              description: 'Analyze headers, sender domains, grammar, urgency indicators, and suspicious links.',
            },
            {
              icon: Lock,
              title: 'Deepfake Detection',
              description: 'Detect AI-generated images and videos using advanced computer vision and temporal analysis.',
            },
            {
              icon: Globe,
              title: 'URL Scanner',
              description: 'Scan URLs for SSL issues, typosquatting, domain age, WHOIS anomalies, and blacklist status.',
            },
            {
              icon: BarChart3,
              title: 'PDF Verification',
              description: 'Verify documents using OCR, logo detection, layout analysis, and signature verification.',
            },
            {
              icon: Zap,
              title: 'Voice Clone Detection',
              description: 'Identify synthetic voices using spectral analysis, pitch detection, and timbre analysis.',
            },
            {
              icon: Users,
              title: 'Social Media Scanner',
              description: 'Detect pump-and-dump schemes, fake advice, and scam language across social platforms.',
            },
          ].map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Card className="glass-card h-full">
                <CardHeader>
                  <feature.icon className="h-12 w-12 text-blue-400 mb-4" />
                  <CardTitle className="text-white">{feature.title}</CardTitle>
                  <CardDescription className="text-gray-400">
                    {feature.description}
                  </CardDescription>
                </CardHeader>
              </Card>
            </motion.div>
          ))}
        </div>
      </section>

      {/* How It Works */}
      <section className="container mx-auto px-6 py-20">
        <h2 className="text-4xl font-bold text-white text-center mb-12">
          How It Works
        </h2>
        <div className="max-w-4xl mx-auto">
          {[
            {
              step: '1',
              title: 'Upload Content',
              description: 'Upload emails, PDFs, images, videos, audio, or URLs through our secure upload center.',
            },
            {
              step: '2',
              title: 'AI Analysis',
              description: 'Our AI models analyze the content using multiple detection techniques simultaneously.',
            },
            {
              step: '3',
              title: 'Trust Score',
              description: 'Receive a comprehensive trust score with detailed evidence and recommendations.',
            },
          ].map((item, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.2 }}
              className="flex items-start space-x-6 mb-12"
            >
              <div className="flex-shrink-0 w-16 h-16 rounded-full bg-blue-600 flex items-center justify-center text-white text-2xl font-bold">
                {item.step}
              </div>
              <div>
                <h3 className="text-2xl font-bold text-white mb-2">{item.title}</h3>
                <p className="text-gray-400">{item.description}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-6 py-20">
        <Card className="glass-card text-center py-16">
          <CardContent>
            <h2 className="text-4xl font-bold text-white mb-4">
              Ready to Protect Your Investments?
            </h2>
            <p className="text-xl text-gray-400 mb-8">
              Join thousands of investors and organizations using SEBI Sentinel AI.
            </p>
            <Link to="/signup">
              <Button size="lg" className="bg-blue-600 hover:bg-blue-700 text-lg px-8">
                Get Started Free
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
          </CardContent>
        </Card>
      </section>

      {/* Footer */}
      <footer className="container mx-auto px-6 py-8 border-t border-gray-800">
        <div className="text-center text-gray-400">
          <p>&copy; 2024 SEBI Sentinel AI. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}

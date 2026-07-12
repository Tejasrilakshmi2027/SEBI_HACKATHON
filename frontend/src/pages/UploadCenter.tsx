import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useDropzone } from 'react-dropzone'
import { Upload, FileText, Image, Video, Music, Globe, Mail, X } from 'lucide-react'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Input } from '../components/ui/input'

export default function UploadCenter() {
  const [files, setFiles] = useState<File[]>([])
  const [url, setUrl] = useState('')
  const [scanType, setScanType] = useState('image')
  const [uploading, setUploading] = useState(false)
  const navigate = useNavigate()

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: (acceptedFiles) => {
      setFiles([...files, ...acceptedFiles])
    },
    accept: {
      'application/pdf': ['.pdf'],
      'image/*': ['.jpg', '.jpeg', '.png', '.gif'],
      'video/*': ['.mp4', '.avi', '.mov'],
      'audio/*': ['.mp3', '.wav'],
      'message/*': ['.eml', '.msg'],
      'text/*': ['.txt'],
    },
  })

  const handleUpload = async () => {
    if (files.length === 0 && !url) return
    
    setUploading(true)
    
    // Simulate upload and scan
    setTimeout(() => {
      setUploading(false)
      navigate('/scan/1')
    }, 2000)
  }

  const removeFile = (index: number) => {
    setFiles(files.filter((_, i) => i !== index))
  }

  const getFileIcon = (file: File) => {
    if (file.type.startsWith('image/')) return <Image className="h-8 w-8" />
    if (file.type.startsWith('video/')) return <Video className="h-8 w-8" />
    if (file.type.startsWith('audio/')) return <Music className="h-8 w-8" />
    if (file.type.includes('pdf')) return <FileText className="h-8 w-8" />
    if (file.type.includes('email') || file.name.endsWith('.eml')) return <Mail className="h-8 w-8" />
    return <FileText className="h-8 w-8" />
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      <div className="container mx-auto px-6 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Upload Center</h1>
          <p className="text-gray-400">Upload files or URLs for security analysis</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* File Upload */}
          <Card className="glass-card">
            <CardHeader>
              <CardTitle className="text-white">Upload File</CardTitle>
              <CardDescription className="text-gray-400">
                Drag and drop files or click to browse
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div
                {...getRootProps()}
                className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                  isDragActive
                    ? 'border-blue-400 bg-blue-400/10'
                    : 'border-gray-600 hover:border-blue-400'
                }`}
              >
                <input {...getInputProps()} />
                <Upload className="h-12 w-12 text-blue-400 mx-auto mb-4" />
                {isDragActive ? (
                  <p className="text-white">Drop the files here...</p>
                ) : (
                  <div>
                    <p className="text-white mb-2">
                      Drag & drop files here, or click to select
                    </p>
                    <p className="text-sm text-gray-400">
                      Supports: PDF, Images, Videos, Audio, Emails, Text
                    </p>
                  </div>
                )}
              </div>

              {/* File List */}
              {files.length > 0 && (
                <div className="mt-4 space-y-2">
                  {files.map((file, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg"
                    >
                      <div className="flex items-center space-x-3">
                        <div className="text-blue-400">{getFileIcon(file)}</div>
                        <div>
                          <div className="text-white text-sm">{file.name}</div>
                          <div className="text-xs text-gray-400">
                            {(file.size / 1024).toFixed(2)} KB
                          </div>
                        </div>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => removeFile(index)}
                        className="text-red-400 hover:text-red-300"
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* URL Scan */}
          <Card className="glass-card">
            <CardHeader>
              <CardTitle className="text-white">Scan URL</CardTitle>
              <CardDescription className="text-gray-400">
                Enter a URL for security analysis
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="relative">
                <Globe className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                <Input
                  type="url"
                  placeholder="https://example.com"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  className="pl-10 bg-slate-800 border-slate-700 text-white"
                />
              </div>

              <div>
                <label className="text-sm text-white mb-2 block">Scan Type</label>
                <select
                  value={scanType}
                  onChange={(e) => setScanType(e.target.value)}
                  className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="image">Image</option>
                  <option value="video">Video</option>
                  <option value="audio">Audio</option>
                  <option value="pdf">PDF Document</option>
                  <option value="email">Email</option>
                  <option value="url">URL</option>
                  <option value="social_media">Social Media</option>
                </select>
              </div>

              <Button
                onClick={handleUpload}
                disabled={uploading || (files.length === 0 && !url)}
                className="w-full bg-blue-600 hover:bg-blue-700"
              >
                {uploading ? 'Analyzing...' : 'Start Scan'}
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Supported Formats */}
        <Card className="glass-card mt-8">
          <CardHeader>
            <CardTitle className="text-white">Supported Formats</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { icon: <Mail />, name: 'Email', formats: '.eml, .msg' },
                { icon: <FileText />, name: 'PDF', formats: '.pdf' },
                { icon: <Image />, name: 'Images', formats: '.jpg, .png, .gif' },
                { icon: <Video />, name: 'Videos', formats: '.mp4, .avi, .mov' },
                { icon: <Music />, name: 'Audio', formats: '.mp3, .wav' },
                { icon: <FileText />, name: 'Text', formats: '.txt' },
                { icon: <Globe />, name: 'URLs', formats: 'http://, https://' },
              ].map((item, index) => (
                <div key={index} className="flex items-center space-x-3 p-3 bg-slate-800/50 rounded-lg">
                  <div className="text-blue-400">{item.icon}</div>
                  <div>
                    <div className="text-white text-sm font-medium">{item.name}</div>
                    <div className="text-xs text-gray-400">{item.formats}</div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

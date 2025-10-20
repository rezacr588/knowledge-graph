import { Activity, CheckCircle, XCircle, AlertCircle } from 'lucide-react'

export default function HealthStatus({ health }) {
  if (!health) {
    return (
      <div className="flex items-center space-x-2 text-gray-400">
        <Activity className="h-4 w-4 animate-pulse" />
        <span className="text-sm">Checking...</span>
      </div>
    )
  }

  const getStatusIcon = () => {
    switch (health.status) {
      case 'healthy':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'degraded':
        return <AlertCircle className="h-4 w-4 text-yellow-500" />
      default:
        return <XCircle className="h-4 w-4 text-red-500" />
    }
  }

  const getStatusColor = () => {
    switch (health.status) {
      case 'healthy':
        return 'text-green-600'
      case 'degraded':
        return 'text-yellow-600'
      default:
        return 'text-red-600'
    }
  }

  return (
    <div className="flex items-center space-x-2">
      {getStatusIcon()}
      <span className={`text-sm font-medium ${getStatusColor()}`}>
        {health.status.charAt(0).toUpperCase() + health.status.slice(1)}
      </span>
    </div>
  )
}

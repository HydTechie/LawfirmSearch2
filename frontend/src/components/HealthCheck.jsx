import { useState, useEffect } from 'react';
import { CheckCircle, XCircle, RefreshCw } from 'lucide-react';
import { apiService } from '../services/api';
import { LoadingSpinner } from './LoadingSpinner';

export const HealthCheck = () => {
  const [status, setStatus] = useState('unknown');
  const [loading, setLoading] = useState(false);
  const [lastChecked, setLastChecked] = useState(null);

  const checkHealth = async () => {
    setLoading(true);
    try {
      await apiService.checkHealth();
      setStatus('healthy');
      setLastChecked(new Date());
    } catch (error) {
      setStatus('unhealthy');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkHealth();
    
    // Check health every 30 seconds
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const getStatusConfig = () => {
    switch (status) {
      case 'healthy':
        return {
          icon: CheckCircle,
          color: 'text-green-600',
          bgColor: 'bg-green-50',
          text: 'API is healthy'
        };
      case 'unhealthy':
        return {
          icon: XCircle,
          color: 'text-red-600',
          bgColor: 'bg-red-50',
          text: 'API is unavailable'
        };
      default:
        return {
          icon: null,
          color: 'text-yellow-600',
          bgColor: 'bg-yellow-50',
          text: 'Checking status...'
        };
    }
  };

  const { icon: Icon, color, bgColor, text } = getStatusConfig();

  return (
    <div className={`p-4 rounded-lg border ${bgColor} border-current`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          {loading ? (
            <LoadingSpinner size="small" text="" />
          ) : Icon ? (
            <Icon className={`w-6 h-6 ${color}`} />
          ) : null}
          <div>
            <p className={`font-semibold ${color}`}>{text}</p>
            {lastChecked && (
              <p className="text-sm text-gray-600">
                Last checked: {lastChecked.toLocaleTimeString()}
              </p>
            )}
          </div>
        </div>
        <button
          onClick={checkHealth}
          disabled={loading}
          className="p-2 text-gray-600 hover:text-gray-800 disabled:opacity-50"
          title="Refresh health status"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>
    </div>
  );
};
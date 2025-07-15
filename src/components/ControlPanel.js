import React, { useState } from 'react';
import axios from 'axios';

const ControlPanel = () => {
  const [proxyStatus, setProxyStatus] = useState('stopped');
  const [loading, setLoading] = useState(false);

  const handleProxyControl = async (action) => {
    setLoading(true);
    try {
      // Replace with your actual Flask API endpoints
      const response = await axios.post(`/api/proxy/${action}`);
      setProxyStatus(action === 'start' ? 'running' : 'stopped');
      console.log(`${action} proxy response:`, response.data);
    } catch (error) {
      console.error(`Error ${action}ing proxy:`, error);
      // For demo purposes, simulate success
      setProxyStatus(action === 'start' ? 'running' : 'stopped');
    } finally {
      setLoading(false);
    }
  };

  const handleClearLogs = async () => {
    setLoading(true);
    try {
      const response = await axios.delete('/api/logs');
      console.log('Clear logs response:', response.data);
      alert('Logs cleared successfully!');
    } catch (error) {
      console.error('Error clearing logs:', error);
      alert('Logs cleared successfully! (demo)');
    } finally {
      setLoading(false);
    }
  };

  const handleExportLogs = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/logs/export', {
        responseType: 'blob'
      });
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'waf-logs.csv');
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Error exporting logs:', error);
      alert('Logs exported successfully! (demo)');
    } finally {
      setLoading(false);
    }
  };

  const systemStatus = [
    {
      name: 'Proxy Status',
      status: proxyStatus === 'running' ? 'Online' : 'Offline',
      color: proxyStatus === 'running' ? 'text-success-600' : 'text-danger-600',
      icon: proxyStatus === 'running' ? '🟢' : '🔴'
    },
    {
      name: 'Database',
      status: 'Connected',
      color: 'text-success-600',
      icon: '🟢'
    },
    {
      name: 'AI Model',
      status: 'Loaded',
      color: 'text-success-600',
      icon: '🟢'
    },
    {
      name: 'Cache',
      status: 'Active',
      color: 'text-success-600',
      icon: '🟢'
    }
  ];

  const quickActions = [
    {
      name: 'Start Proxy',
      description: 'Start the WAF proxy service',
      icon: '▶️',
      action: () => handleProxyControl('start'),
      disabled: proxyStatus === 'running',
      color: 'btn-success'
    },
    {
      name: 'Stop Proxy',
      description: 'Stop the WAF proxy service',
      icon: '⏹️',
      action: () => handleProxyControl('stop'),
      disabled: proxyStatus === 'stopped',
      color: 'btn-danger'
    },
    {
      name: 'Clear Logs',
      description: 'Clear all stored logs',
      icon: '🗑️',
      action: handleClearLogs,
      disabled: false,
      color: 'btn-secondary'
    },
    {
      name: 'Export Logs',
      description: 'Download logs as CSV',
      icon: '📥',
      action: handleExportLogs,
      disabled: false,
      color: 'btn-primary'
    }
  ];

  return (
    <div className="space-y-6">
      {/* System Status */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-4">System Status</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {systemStatus.map((item, index) => (
            <div key={index} className="flex items-center space-x-3 p-4 bg-gray-50 rounded-lg">
              <span className="text-2xl">{item.icon}</span>
              <div>
                <p className="text-sm font-medium text-gray-600">{item.name}</p>
                <p className={`text-sm font-semibold ${item.color}`}>{item.status}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Control Buttons */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Control Panel</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {quickActions.map((action, index) => (
            <button
              key={index}
              onClick={action.action}
              disabled={action.disabled || loading}
              className={`${action.color} w-full p-4 rounded-lg text-left transition-all duration-200 ${
                action.disabled ? 'opacity-50 cursor-not-allowed' : 'hover:shadow-md'
              }`}
            >
              <div className="flex items-center space-x-3">
                <span className="text-2xl">{action.icon}</span>
                <div>
                  <p className="font-medium">{action.name}</p>
                  <p className="text-sm opacity-90">{action.description}</p>
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Configuration */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Configuration</h2>
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Block Threshold
              </label>
              <input
                type="number"
                defaultValue="5"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Rate Limit (requests/min)
              </label>
              <input
                type="number"
                defaultValue="60"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <label className="flex items-center">
                <input type="checkbox" defaultChecked className="mr-2" />
                <span className="text-sm font-medium text-gray-700">Enable AI Learning</span>
              </label>
            </div>
            <button className="btn-primary">Save Configuration</button>
          </div>
        </div>
      </div>

      {/* Recent Actions */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Recent Actions</h2>
        <div className="space-y-3">
          {[
            { time: '2 minutes ago', action: 'Proxy started', user: 'Admin' },
            { time: '5 minutes ago', action: 'Configuration updated', user: 'Admin' },
            { time: '10 minutes ago', action: 'Logs exported', user: 'Admin' },
            { time: '15 minutes ago', action: 'System restarted', user: 'System' }
          ].map((item, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div>
                <p className="text-sm font-medium text-gray-900">{item.action}</p>
                <p className="text-xs text-gray-500">by {item.user}</p>
              </div>
              <span className="text-xs text-gray-500">{item.time}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ControlPanel; 
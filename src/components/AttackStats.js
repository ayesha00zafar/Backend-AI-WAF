import React from 'react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const AttackStats = () => {
  // Mock data for pie chart (Good vs Bad traffic)
  const trafficData = [
    { name: 'Safe Traffic', value: 75, color: '#22c55e' },
    { name: 'Malicious Traffic', value: 25, color: '#ef4444' }
  ];

  // Mock data for bar chart (Attack types frequency)
  const attackTypeData = [
    { type: 'SQLi', count: 45, color: '#ef4444' },
    { type: 'XSS', count: 32, color: '#f97316' },
    { type: 'CSRF', count: 18, color: '#eab308' },
    { type: 'LFI', count: 12, color: '#8b5cf6' },
    { type: 'RCE', count: 8, color: '#ec4899' },
    { type: 'Other', count: 15, color: '#6b7280' }
  ];

  // Summary statistics
  const stats = [
    {
      title: 'Total Requests',
      value: '1,234',
      change: '+12%',
      changeType: 'positive',
      icon: '📊'
    },
    {
      title: 'Blocked Attacks',
      value: '130',
      change: '+8%',
      changeType: 'positive',
      icon: '🛡️'
    },
    {
      title: 'Success Rate',
      value: '94.5%',
      change: '+2.1%',
      changeType: 'positive',
      icon: '✅'
    },
    {
      title: 'Response Time',
      value: '45ms',
      change: '-12ms',
      changeType: 'positive',
      icon: '⚡'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <div key={index} className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                <div className="flex items-center mt-1">
                  <span className={`text-sm font-medium ${
                    stat.changeType === 'positive' ? 'text-success-600' : 'text-danger-600'
                  }`}>
                    {stat.change}
                  </span>
                  <span className="text-sm text-gray-500 ml-1">from last hour</span>
                </div>
              </div>
              <div className="text-3xl">{stat.icon}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Traffic Distribution Pie Chart */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Traffic Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={trafficData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {trafficData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Attack Types Bar Chart */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Attack Types Frequency</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={attackTypeData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="type" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="count" fill="#3b82f6">
                {attackTypeData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
        <div className="space-y-3">
          {[
            { time: '2 minutes ago', event: 'SQL injection attempt blocked', severity: 'high' },
            { time: '5 minutes ago', event: 'XSS attack detected and prevented', severity: 'medium' },
            { time: '8 minutes ago', event: 'Rate limit exceeded for IP 192.168.1.100', severity: 'low' },
            { time: '12 minutes ago', event: 'Suspicious file upload attempt blocked', severity: 'high' },
            { time: '15 minutes ago', event: 'Normal traffic from 10.0.0.50', severity: 'info' }
          ].map((activity, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <div className={`w-2 h-2 rounded-full ${
                  activity.severity === 'high' ? 'bg-danger-500' :
                  activity.severity === 'medium' ? 'bg-orange-500' :
                  activity.severity === 'low' ? 'bg-yellow-500' : 'bg-blue-500'
                }`}></div>
                <span className="text-sm text-gray-900">{activity.event}</span>
              </div>
              <span className="text-xs text-gray-500">{activity.time}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default AttackStats; 
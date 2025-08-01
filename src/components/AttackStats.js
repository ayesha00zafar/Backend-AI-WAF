import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const AttackStats = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await axios.get('/api/stats');
        console.log('📊 Stats received:', res.data);
        setStats(res.data);
      } catch (err) {
        console.error('❌ Error fetching stats:', err);
        setError(`Failed to load stats: ${err.response?.data?.error || err.message}`);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
    // Refresh stats every 30 seconds
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div className="card p-8 text-center">Loading stats...</div>;
  if (error) return <div className="card p-8 text-center text-red-600">{error}</div>;
  if (!stats) return null;

  // Calculate success rate
  const successRate = stats.total_requests > 0 
    ? ((stats.benign_requests / stats.total_requests) * 100).toFixed(1)
    : 0;

  // Pie chart data for traffic distribution
  const trafficData = [
    { name: 'Benign Traffic', value: stats.benign_requests || 0, color: '#22c55e' },
    { name: 'Malicious Traffic', value: stats.malicious_requests || 0, color: '#ef4444' }
  ];

  // Bar chart data for attack types
  const attackTypeData = Object.entries(stats.attack_types || {}).map(([type, count]) => ({
    type: type.charAt(0).toUpperCase() + type.slice(1), // Capitalize first letter
    count,
    color: '#ef4444'
  }));

  // Summary statistics
  const summaryStats = [
    {
      title: 'Total Requests',
      value: stats.total_requests || 0,
      icon: '📊',
      color: 'text-blue-600'
    },
    {
      title: 'Blocked Attacks',
      value: stats.blocked_requests || 0,
      icon: '🛡️',
      color: 'text-red-600'
    },
    {
      title: 'Allowed Requests',
      value: stats.allowed_requests || 0,
      icon: '✅',
      color: 'text-green-600'
    },
    {
      title: 'Success Rate',
      value: `${successRate}%`,
      icon: '📈',
      color: 'text-purple-600'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {summaryStats.map((stat, index) => (
          <div key={index} className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                <p className={`text-2xl font-bold ${stat.color}`}>{stat.value}</p>
              </div>
              <div className="text-3xl">{stat.icon}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Recent Activity */}
      {stats.recent_activity && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">{stats.recent_activity.last_hour || 0}</p>
              <p className="text-sm text-gray-600">Last Hour</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">{stats.recent_activity.last_24_hours || 0}</p>
              <p className="text-sm text-gray-600">Last 24 Hours</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-purple-600">{stats.recent_activity.last_7_days || 0}</p>
              <p className="text-sm text-gray-600">Last 7 Days</p>
            </div>
          </div>
        </div>
      )}

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Traffic Distribution Pie Chart */}
        <div className="bg-white rounded-lg shadow p-6">
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
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Attack Types Frequency</h3>
          {attackTypeData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={attackTypeData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="type" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="count" fill="#ef4444" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-64 text-gray-500">
              <p>No attack data available</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AttackStats; 
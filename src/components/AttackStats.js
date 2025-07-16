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
        setStats(res.data);
      } catch (err) {
        setError('Failed to load stats');
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
    // Optionally, refresh stats every 30s
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div className="card p-8 text-center">Loading stats...</div>;
  if (error) return <div className="card p-8 text-center text-danger-600">{error}</div>;
  if (!stats) return null;

  // Pie chart data
  const trafficData = [
    { name: 'Safe Traffic', value: stats.safe_count || 0, color: '#22c55e' },
    { name: 'Malicious Traffic', value: stats.malicious_count || 0, color: '#ef4444' }
  ];

  // Bar chart data
  const attackTypeData = Object.entries(stats.attack_types || {}).map(([type, count]) => ({
    type,
    count,
    color: type === 'blocked' ? '#ef4444' : '#22c55e'
  }));

  // Summary statistics
  const summaryStats = [
    {
      title: 'Total Requests',
      value: stats.total_requests,
      icon: '📊'
    },
    {
      title: 'Blocked Attacks',
      value: stats.malicious_count,
      icon: '🛡️'
    },
    {
      title: 'Success Rate',
      value: `${stats.success_rate?.toFixed(1) || 0}%`,
      icon: '✅'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {summaryStats.map((stat, index) => (
          <div key={index} className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
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
                  <Cell key={`cell-bar-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default AttackStats; 
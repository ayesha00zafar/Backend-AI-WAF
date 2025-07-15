import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import io from 'socket.io-client';

const LogTable = () => {
  const [logs, setLogs] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(10);
  const [loading, setLoading] = useState(false);
  const [socket, setSocket] = useState(null);

  // Mock data for demonstration
  const mockLogs = [
    {
      id: 1,
      timestamp: '2024-01-15 14:30:25',
      ipAddress: '192.168.1.100',
      url: 'https://example.com/login',
      method: 'POST',
      label: 'Malicious',
      type: 'SQLi',
      status: 'Blocked'
    },
    {
      id: 2,
      timestamp: '2024-01-15 14:29:18',
      ipAddress: '10.0.0.50',
      url: 'https://example.com/api/users',
      method: 'GET',
      label: 'Safe',
      type: 'Normal',
      status: 'Allowed'
    },
    {
      id: 3,
      timestamp: '2024-01-15 14:28:45',
      ipAddress: '203.0.113.25',
      url: 'https://example.com/search?q=<script>alert("xss")</script>',
      method: 'GET',
      label: 'Malicious',
      type: 'XSS',
      status: 'Blocked'
    },
    {
      id: 4,
      timestamp: '2024-01-15 14:27:32',
      ipAddress: '172.16.0.75',
      url: 'https://example.com/products',
      method: 'GET',
      label: 'Safe',
      type: 'Normal',
      status: 'Allowed'
    },
    {
      id: 5,
      timestamp: '2024-01-15 14:26:15',
      ipAddress: '198.51.100.10',
      url: 'https://example.com/admin?user=admin\' OR \'1\'=\'1',
      method: 'GET',
      label: 'Malicious',
      type: 'SQLi',
      status: 'Blocked'
    }
  ];

  // Initialize Socket.IO connection
  useEffect(() => {
    const newSocket = io();
    
    newSocket.on('connect', () => {
      console.log('Connected to Socket.IO server');
    });

    newSocket.on('new_log', (newLog) => {
      console.log('New log received:', newLog);
      setLogs(prevLogs => [newLog, ...prevLogs.slice(0, -1)]); // Add new log at the beginning
    });

    newSocket.on('logs_cleared', (data) => {
      console.log('Logs cleared:', data);
      setLogs([]);
    });

    newSocket.on('disconnect', () => {
      console.log('Disconnected from Socket.IO server');
    });

    setSocket(newSocket);

    return () => {
      newSocket.close();
    };
  }, []);

  // Fetch logs from Flask API
  const fetchLogs = useCallback(async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/logs', {
        params: {
          page: currentPage,
          per_page: itemsPerPage
        }
      });
      setLogs(response.data.logs || mockLogs);
    } catch (error) {
      console.error('Error fetching logs:', error);
      // Use mock data if API is not available
      setLogs(mockLogs);
    } finally {
      setLoading(false);
    }
  }, [currentPage, itemsPerPage]);

  // Fetch data every 5 seconds
  useEffect(() => {
    fetchLogs();
    const interval = setInterval(fetchLogs, 5000);
    return () => clearInterval(interval);
  }, [fetchLogs]);

  // Pagination
  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentLogs = logs.slice(indexOfFirstItem, indexOfLastItem);
  const totalPages = Math.ceil(logs.length / itemsPerPage);

  const getStatusColor = (status) => {
    switch (status) {
      case 'Blocked':
        return 'bg-danger-100 text-danger-800';
      case 'Allowed':
        return 'bg-success-100 text-success-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getLabelColor = (label) => {
    switch (label) {
      case 'Malicious':
        return 'bg-danger-100 text-danger-800';
      case 'Safe':
        return 'bg-success-100 text-success-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getTypeColor = (type) => {
    switch (type) {
      case 'SQLi':
        return 'bg-red-100 text-red-800';
      case 'XSS':
        return 'bg-orange-100 text-orange-800';
      case 'Normal':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Live Logs</h2>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-success-500 rounded-full animate-pulse"></div>
          <span className="text-sm text-gray-600">Real-time updates</span>
        </div>
      </div>

      {loading && (
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>
      )}

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Timestamp
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                IP Address
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                URL
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Method
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Label
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Type
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {currentLogs.map((log) => (
              <tr key={log.id} className="table-row-hover">
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {log.timestamp}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {log.ipAddress}
                </td>
                <td className="px-6 py-4 text-sm text-gray-900 max-w-xs truncate">
                  {log.url}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    {log.method}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getLabelColor(log.label)}`}>
                    {log.label}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getTypeColor(log.type)}`}>
                    {log.type}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(log.status)}`}>
                    {log.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between mt-6">
          <div className="text-sm text-gray-700">
            Showing {indexOfFirstItem + 1} to {Math.min(indexOfLastItem, logs.length)} of {logs.length} results
          </div>
          <div className="flex space-x-2">
            <button
              onClick={() => setCurrentPage(currentPage - 1)}
              disabled={currentPage === 1}
              className="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            <span className="px-3 py-2 text-sm font-medium text-gray-700">
              Page {currentPage} of {totalPages}
            </span>
            <button
              onClick={() => setCurrentPage(currentPage + 1)}
              disabled={currentPage === totalPages}
              className="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default LogTable; 
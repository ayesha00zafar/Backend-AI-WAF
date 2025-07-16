import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import io from 'socket.io-client';

const LogTable = () => {
  const [logs, setLogs] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(10);
  const [loading, setLoading] = useState(false);
  const [socket, setSocket] = useState(null);
  const [total, setTotal] = useState(0);

  // Initialize Socket.IO connection
  useEffect(() => {
    const newSocket = io('http://localhost:5000');
    newSocket.on('connect', () => {
      console.log('Connected to Socket.IO server');
    });
    newSocket.on('new_log', (newLog) => {
      setLogs(prevLogs => [newLog, ...prevLogs]);
      setTotal(prevTotal => prevTotal + 1);
    });
    newSocket.on('logs_cleared', () => {
      setLogs([]);
      setTotal(0);
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
      setLogs(response.data.logs || []);
      setTotal(response.data.total || 0);
    } catch (error) {
      console.error('Error fetching logs:', error);
      setLogs([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }, [currentPage, itemsPerPage]);

  useEffect(() => {
    fetchLogs();
    // Optionally, refresh logs every 30s for pagination
    const interval = setInterval(fetchLogs, 30000);
    return () => clearInterval(interval);
  }, [fetchLogs]);

  // Pagination
  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentLogs = logs.slice(indexOfFirstItem, indexOfLastItem);
  const totalPages = Math.ceil(total / itemsPerPage);

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
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Timestamp</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">URL</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Method</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Prediction</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {currentLogs.map((log, idx) => (
              <tr key={log.id || idx}>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{log.timestamp ? new Date(log.timestamp).toLocaleString() : ''}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-blue-700 break-all">{log.url}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{log.method}</td>
                <td className={`px-6 py-4 whitespace-nowrap text-sm font-semibold ${getStatusColor(log.status)}`}>{log.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {/* Pagination controls */}
      <div className="flex justify-end mt-4 space-x-2">
        <button onClick={() => setCurrentPage(p => Math.max(1, p - 1))} disabled={currentPage === 1} className="btn-secondary">Prev</button>
        <span className="text-sm">Page {currentPage} of {totalPages}</span>
        <button onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))} disabled={currentPage === totalPages} className="btn-secondary">Next</button>
      </div>
    </div>
  );
};

export default LogTable; 
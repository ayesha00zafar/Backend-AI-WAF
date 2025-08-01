
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import LogTable from './components/LogTable';
import AttackStats from './components/AttackStats';
import ControlPanel from './components/ControlPanel';
import TestComponent from './components/TestComponent';
import { useEffect, useState } from "react";
import { io } from "socket.io-client";

function App() {
  const [activeSection, setActiveSection] = useState('logs');
  const [socket, setSocket] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');

  useEffect(() => {
    // Initialize SocketIO connection
    const newSocket = io("http://localhost:5000", {
      transports: ['websocket', 'polling'],
      timeout: 20000,
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000
    });

    newSocket.on('connect', () => {
      console.log('✅ Connected to SocketIO server');
      setConnectionStatus('connected');
    });

    newSocket.on('disconnect', () => {
      console.log('❌ Disconnected from SocketIO server');
      setConnectionStatus('disconnected');
    });

    newSocket.on('connect_error', (error) => {
      console.log('❌ SocketIO connection error:', error);
      setConnectionStatus('error');
    });

    newSocket.on('status', (data) => {
      console.log('📡 SocketIO status:', data);
    });

    setSocket(newSocket);

    return () => {
      if (newSocket) {
        newSocket.disconnect();
      }
    };
  }, []);

  const renderMainContent = () => {
    switch (activeSection) {
      case 'logs':
        return <LogTable socket={socket} />;
      case 'stats':
        return <AttackStats />;
      case 'control':
        return <ControlPanel />;
      case 'test':
        return <TestComponent />;
      default:
        return <LogTable socket={socket} />;
    }
  };

  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar activeSection={activeSection} setActiveSection={setActiveSection} />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header connectionStatus={connectionStatus} />
        <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-100 p-6">
          {renderMainContent()}
        </main>
      </div>
    </div>
  );
}

export default App;

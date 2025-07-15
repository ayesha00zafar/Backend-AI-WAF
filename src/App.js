import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import LogTable from './components/LogTable';
import AttackStats from './components/AttackStats';
import ControlPanel from './components/ControlPanel';
import TestComponent from './components/TestComponent';

function App() {
  const [activeSection, setActiveSection] = useState('test');

  const renderMainContent = () => {
    switch (activeSection) {
      case 'logs':
        return <LogTable />;
      case 'stats':
        return <AttackStats />;
      case 'control':
        return <ControlPanel />;
      case 'test':
        return <TestComponent />;
      default:
        return <TestComponent />;
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <Sidebar activeSection={activeSection} setActiveSection={setActiveSection} />
      
      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <Header />
        
        {/* Main Content Area */}
        <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-50 p-6">
          <div className="max-w-7xl mx-auto">
            {renderMainContent()}
          </div>
        </main>
      </div>
    </div>
  );
}

export default App; 
import React from 'react';

const Sidebar = ({ activeSection, setActiveSection }) => {
  const menuItems = [
    {
      id: 'test',
      name: 'Tailwind Test',
      icon: '🧪',
      description: 'Test Tailwind CSS'
    },
    {
      id: 'logs',
      name: 'Live Logs',
      icon: '📊',
      description: 'Real-time request logs'
    },
    {
      id: 'stats',
      name: 'Attack Stats',
      icon: '📈',
      description: 'Analytics and charts'
    },
    {
      id: 'control',
      name: 'Control Panel',
      icon: '⚙️',
      description: 'System controls'
    }
  ];

  return (
    <div className="w-64 bg-white shadow-lg hidden md:block">
      <div className="p-6">
        <div className="flex items-center mb-8">
          <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center mr-3">
            <span className="text-white font-bold text-sm">WAF</span>
          </div>
          <h1 className="text-xl font-bold text-gray-900">AI WAF Dashboard</h1>
        </div>
        
        <nav className="space-y-2">
          {menuItems.map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveSection(item.id)}
              className={`w-full flex items-center p-3 rounded-lg transition-colors duration-200 ${
                activeSection === item.id
                  ? 'bg-primary-50 text-primary-700 border-r-2 border-primary-600'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              }`}
            >
              <span className="text-xl mr-3">{item.icon}</span>
              <div className="text-left">
                <div className="font-medium">{item.name}</div>
                <div className="text-xs text-gray-500">{item.description}</div>
              </div>
            </button>
          ))}
        </nav>
      </div>
      
      {/* Mobile menu button */}
      <div className="md:hidden fixed top-4 left-4 z-50">
        <button className="bg-white p-2 rounded-lg shadow-lg">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
      </div>
    </div>
  );
};

export default Sidebar; 
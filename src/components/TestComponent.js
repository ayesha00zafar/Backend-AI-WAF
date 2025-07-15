import React from 'react';

const TestComponent = () => {
  return (
    <div className="p-8 bg-blue-500 text-white rounded-lg shadow-lg">
      <h1 className="text-3xl font-bold mb-4">Tailwind CSS Test</h1>
      <p className="text-lg">If you can see this styled text, Tailwind is working!</p>
      <button className="mt-4 bg-green-500 hover:bg-green-600 px-4 py-2 rounded">
        Test Button
      </button>
    </div>
  );
};

export default TestComponent; 
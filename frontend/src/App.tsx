import React, { useState } from 'react';
import { Dashboard } from './pages/Dashboard';
import { FeedbackDemo } from './pages/FeedbackDemo';

type Page = 'dashboard' | 'demo';

function App() {
  const [currentPage, setCurrentPage] = useState<Page>('demo');

  return (
    <div>
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex space-x-8">
              <button
                onClick={() => setCurrentPage('demo')}
                className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${
                  currentPage === 'demo'
                    ? 'border-blue-500 text-gray-900'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                API Demo
              </button>
              <button
                onClick={() => setCurrentPage('dashboard')}
                className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${
                  currentPage === 'dashboard'
                    ? 'border-blue-500 text-gray-900'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Dashboard
              </button>
            </div>
            <div className="flex items-center">
              <span className="text-sm text-gray-500">AI Feedback Triage System</span>
            </div>
          </div>
        </div>
      </nav>

      {/* Page Content */}
      {currentPage === 'demo' ? <FeedbackDemo /> : <Dashboard />}
    </div>
  );
}

export default App;

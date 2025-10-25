import React from 'react';
import type { Feedback } from '../types';

interface HeaderProps {
  feedbacks: Feedback[];
}

export const Header: React.FC<HeaderProps> = ({ feedbacks }) => {
  const totalCount = feedbacks.length;
  const highUrgencyCount = feedbacks.filter(
    f => f.analysis?.urgency_level === 'high'
  ).length;

  const negativeSentimentCount = feedbacks.filter(
    f => f.analysis?.sentiment === 'negative'
  ).length;

  const negativePercentage = totalCount > 0
    ? ((negativeSentimentCount / totalCount) * 100).toFixed(1)
    : '0';

  return (
    <div className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">
          AI Feedback Triage Dashboard
        </h1>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="card">
            <div className="text-sm font-medium text-gray-500">Total Messages</div>
            <div className="mt-2 text-3xl font-bold text-gray-900">{totalCount}</div>
          </div>

          <div className="card">
            <div className="text-sm font-medium text-gray-500">High Urgency</div>
            <div className="mt-2 text-3xl font-bold text-red-600">{highUrgencyCount}</div>
          </div>

          <div className="card">
            <div className="text-sm font-medium text-gray-500">Negative Sentiment</div>
            <div className="mt-2 text-3xl font-bold text-orange-600">{negativePercentage}%</div>
          </div>
        </div>
      </div>
    </div>
  );
};

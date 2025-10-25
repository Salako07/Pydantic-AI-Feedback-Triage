import React from 'react';
import type { Feedback, Sentiment, Urgency } from '../types';

interface TicketTableProps {
  feedbacks: Feedback[];
  onSelectFeedback: (feedback: Feedback) => void;
}

const getSentimentBadgeClass = (sentiment: Sentiment): string => {
  const classes = {
    positive: 'badge-positive',
    neutral: 'badge-neutral',
    negative: 'badge-negative',
  };
  return `badge ${classes[sentiment]}`;
};

const getUrgencyBadgeClass = (urgency: Urgency): string => {
  const classes = {
    low: 'badge-low',
    medium: 'badge-medium',
    high: 'badge-high',
  };
  return `badge ${classes[urgency]}`;
};

export const TicketTable: React.FC<TicketTableProps> = ({ feedbacks, onSelectFeedback }) => {
  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  };

  return (
    <div className="card">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Customer Feedback</h2>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Customer
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Email
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Sentiment
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Urgency
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Category
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Summary
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Created
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {feedbacks.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-6 py-8 text-center text-gray-500">
                  No feedback messages found
                </td>
              </tr>
            ) : (
              feedbacks.map((feedback) => (
                <tr
                  key={feedback.id}
                  onClick={() => onSelectFeedback(feedback)}
                  className="hover:bg-gray-50 cursor-pointer transition-colors"
                >
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {feedback.customer_name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {feedback.email}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {feedback.analysis ? (
                      <span className={getSentimentBadgeClass(feedback.analysis.sentiment)}>
                        {feedback.analysis.sentiment}
                      </span>
                    ) : (
                      <span className="badge bg-gray-100 text-gray-500">N/A</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {feedback.analysis ? (
                      <span className={getUrgencyBadgeClass(feedback.analysis.urgency_level)}>
                        {feedback.analysis.urgency_level}
                      </span>
                    ) : (
                      <span className="badge bg-gray-100 text-gray-500">N/A</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {feedback.analysis?.category || 'N/A'}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500 max-w-md truncate">
                    {feedback.analysis?.summary || 'Analysis pending...'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {formatDate(feedback.created_at)}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

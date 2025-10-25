import React from 'react';
import type { Feedback } from '../types';

interface TicketDetailProps {
  feedback: Feedback | null;
  onClose: () => void;
}

export const TicketDetail: React.FC<TicketDetailProps> = ({ feedback, onClose }) => {
  if (!feedback) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-start mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Feedback Details</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div className="space-y-6">
            <div>
              <h3 className="text-sm font-medium text-gray-500 mb-2">Customer Information</h3>
              <div className="bg-gray-50 rounded-lg p-4 space-y-2">
                <div>
                  <span className="font-medium">Name:</span> {feedback.customer_name}
                </div>
                <div>
                  <span className="font-medium">Email:</span> {feedback.email}
                </div>
                <div>
                  <span className="font-medium">Created:</span>{' '}
                  {new Date(feedback.created_at).toLocaleString()}
                </div>
              </div>
            </div>

            <div>
              <h3 className="text-sm font-medium text-gray-500 mb-2">Message</h3>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-gray-900 whitespace-pre-wrap">{feedback.message}</p>
              </div>
            </div>

            {feedback.analysis ? (
              <>
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-2">AI Analysis</h3>
                  <div className="bg-blue-50 rounded-lg p-4 space-y-3">
                    <div className="grid grid-cols-3 gap-4">
                      <div>
                        <div className="text-xs text-gray-500 mb-1">Sentiment</div>
                        <div className="font-medium capitalize">{feedback.analysis.sentiment}</div>
                      </div>
                      <div>
                        <div className="text-xs text-gray-500 mb-1">Urgency</div>
                        <div className="font-medium capitalize">{feedback.analysis.urgency_level}</div>
                      </div>
                      <div>
                        <div className="text-xs text-gray-500 mb-1">Category</div>
                        <div className="font-medium capitalize">{feedback.analysis.category}</div>
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500 mb-1">Summary</div>
                      <p className="text-gray-900">{feedback.analysis.summary}</p>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500 mb-1">Recommended Action</div>
                      <p className="text-gray-900 font-medium">{feedback.analysis.recommended_action}</p>
                    </div>
                  </div>
                </div>

                <div className="flex gap-3">
                  <button className="btn btn-primary flex-1">
                    Mark as Resolved
                  </button>
                  <button className="btn btn-secondary">
                    Assign to Team
                  </button>
                </div>
              </>
            ) : (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <p className="text-yellow-800">
                  {feedback.analysis_error
                    ? `Analysis failed: ${feedback.analysis_error}`
                    : 'AI analysis is pending...'}
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

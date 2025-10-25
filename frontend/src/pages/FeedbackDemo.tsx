import React, { useState } from 'react';
import { feedbackApi } from '../services/api';
import type { Feedback } from '../types';

export const FeedbackDemo: React.FC = () => {
  const [formData, setFormData] = useState({
    customer_name: '',
    email: '',
    message: '',
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<Feedback | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await feedbackApi.create(formData);
      setResult(response);
      // Clear form after successful submission
      setFormData({ customer_name: '', email: '', message: '' });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to submit feedback');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const exampleMessages = [
    {
      name: 'Positive',
      message: "I absolutely love your product! It has made my workflow so much more efficient. The interface is intuitive and the features are exactly what I needed.",
    },
    {
      name: 'Urgent Billing',
      message: "I've been trying to access my premium account for the past 2 hours but keep getting an error. This is completely unacceptable as I paid for this service. I need this resolved immediately!",
    },
    {
      name: 'Technical Issue',
      message: "The recent update broke several features I use daily. The export function no longer works and the app crashes when I try to sync.",
    },
    {
      name: 'Feature Request',
      message: "It would be great if you could add a dark mode option. I often work late at night and the bright interface strains my eyes.",
    },
  ];

  const loadExample = (message: string) => {
    setFormData({
      customer_name: 'Demo User',
      email: 'demo@example.com',
      message: message,
    });
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Feedback API Demo</h1>
          <p className="mt-2 text-gray-600">
            Test the AI-powered feedback analysis API in real-time
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column - Form */}
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Submit Feedback</h2>

            {/* Example Messages */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Quick Examples:
              </label>
              <div className="grid grid-cols-2 gap-2">
                {exampleMessages.map((example) => (
                  <button
                    key={example.name}
                    type="button"
                    onClick={() => loadExample(example.message)}
                    className="btn btn-secondary text-sm"
                  >
                    {example.name}
                  </button>
                ))}
              </div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label htmlFor="customer_name" className="block text-sm font-medium text-gray-700 mb-2">
                  Customer Name *
                </label>
                <input
                  type="text"
                  id="customer_name"
                  name="customer_name"
                  value={formData.customer_name}
                  onChange={handleChange}
                  required
                  className="input"
                  placeholder="John Doe"
                />
              </div>

              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                  Email *
                </label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  className="input"
                  placeholder="john@example.com"
                />
              </div>

              <div>
                <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-2">
                  Message * <span className="text-gray-500 font-normal">(max 8000 characters)</span>
                </label>
                <textarea
                  id="message"
                  name="message"
                  value={formData.message}
                  onChange={handleChange}
                  required
                  rows={8}
                  maxLength={8000}
                  className="input resize-none"
                  placeholder="Describe your issue, feedback, or question..."
                />
                <div className="mt-1 text-xs text-gray-500 text-right">
                  {formData.message.length} / 8000 characters
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <span className="flex items-center justify-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Analyzing with AI...
                  </span>
                ) : (
                  'Submit & Analyze'
                )}
              </button>
            </form>

            {error && (
              <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-red-800 text-sm">{error}</p>
              </div>
            )}
          </div>

          {/* Right Column - Results */}
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">AI Analysis Result</h2>

            {!result && (
              <div className="text-center py-12 text-gray-500">
                <svg className="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <p>Submit feedback to see AI analysis</p>
              </div>
            )}

            {result && (
              <div className="space-y-4">
                {/* Feedback Info */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="text-sm font-medium text-gray-700 mb-2">Feedback Details</h3>
                  <div className="space-y-2 text-sm">
                    <div>
                      <span className="font-medium">ID:</span> <span className="font-mono text-xs">{result.id}</span>
                    </div>
                    <div>
                      <span className="font-medium">Customer:</span> {result.customer_name}
                    </div>
                    <div>
                      <span className="font-medium">Email:</span> {result.email}
                    </div>
                    <div>
                      <span className="font-medium">Submitted:</span> {new Date(result.created_at).toLocaleString()}
                    </div>
                  </div>
                </div>

                {/* Original Message */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="text-sm font-medium text-gray-700 mb-2">Original Message</h3>
                  <p className="text-sm text-gray-900 whitespace-pre-wrap">{result.message}</p>
                </div>

                {/* AI Analysis */}
                {result.analysis ? (
                  <div className="bg-blue-50 rounded-lg p-4 space-y-3">
                    <h3 className="text-sm font-medium text-gray-700 mb-3">AI Analysis</h3>

                    <div className="grid grid-cols-3 gap-4">
                      <div>
                        <div className="text-xs text-gray-600 mb-1">Sentiment</div>
                        <span className={`badge badge-${result.analysis.sentiment} text-sm`}>
                          {result.analysis.sentiment}
                        </span>
                      </div>
                      <div>
                        <div className="text-xs text-gray-600 mb-1">Urgency</div>
                        <span className={`badge badge-${result.analysis.urgency_level} text-sm`}>
                          {result.analysis.urgency_level}
                        </span>
                      </div>
                      <div>
                        <div className="text-xs text-gray-600 mb-1">Category</div>
                        <span className="badge bg-purple-100 text-purple-800 text-sm">
                          {result.analysis.category}
                        </span>
                      </div>
                    </div>

                    <div>
                      <div className="text-xs text-gray-600 mb-1">Summary</div>
                      <p className="text-sm text-gray-900">{result.analysis.summary}</p>
                    </div>

                    <div>
                      <div className="text-xs text-gray-600 mb-1">Recommended Action</div>
                      <p className="text-sm text-gray-900 font-medium bg-yellow-50 border border-yellow-200 rounded p-2">
                        💡 {result.analysis.recommended_action}
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                    <p className="text-yellow-800 text-sm">
                      {result.analysis_error
                        ? `Analysis failed: ${result.analysis_error}`
                        : 'AI analysis is pending...'}
                    </p>
                  </div>
                )}

                {/* JSON Response */}
                <div>
                  <details className="group">
                    <summary className="cursor-pointer text-sm font-medium text-gray-700 hover:text-gray-900 flex items-center">
                      <svg className="w-4 h-4 mr-1 transform group-open:rotate-90 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                      View Raw JSON Response
                    </summary>
                    <pre className="mt-2 p-4 bg-gray-900 text-gray-100 rounded-lg overflow-x-auto text-xs">
                      {JSON.stringify(result, null, 2)}
                    </pre>
                  </details>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* API Information */}
        <div className="mt-8 card">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">API Information</h2>
          <div className="space-y-4 text-sm">
            <div>
              <h3 className="font-medium text-gray-900 mb-2">Endpoint</h3>
              <code className="bg-gray-100 px-3 py-2 rounded block">POST http://localhost:8000/api/feedback</code>
            </div>

            <div>
              <h3 className="font-medium text-gray-900 mb-2">Request Body</h3>
              <pre className="bg-gray-100 px-3 py-2 rounded overflow-x-auto text-xs">
{`{
  "customer_name": "string (1-200 chars)",
  "email": "valid email address",
  "message": "string (1-8000 chars)"
}`}
              </pre>
            </div>

            <div>
              <h3 className="font-medium text-gray-900 mb-2">Response</h3>
              <p className="text-gray-600 mb-2">Returns the created feedback with AI analysis:</p>
              <pre className="bg-gray-100 px-3 py-2 rounded overflow-x-auto text-xs">
{`{
  "id": "unique_id",
  "customer_name": "string",
  "email": "string",
  "message": "string",
  "created_at": "ISO 8601 timestamp",
  "analysis": {
    "sentiment": "positive" | "neutral" | "negative",
    "urgency_level": "low" | "medium" | "high",
    "category": "string",
    "summary": "string",
    "recommended_action": "string"
  }
}`}
              </pre>
            </div>

            <div>
              <h3 className="font-medium text-gray-900 mb-2">cURL Example</h3>
              <pre className="bg-gray-900 text-gray-100 px-3 py-2 rounded overflow-x-auto text-xs">
{`curl -X POST http://localhost:8000/api/feedback \\
  -H "Content-Type: application/json" \\
  -d '{
    "customer_name": "John Doe",
    "email": "john@example.com",
    "message": "I love your product!"
  }'`}
              </pre>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

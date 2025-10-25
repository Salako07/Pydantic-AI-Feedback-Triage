import React, { useState, useEffect, useCallback } from 'react';
import { Header } from '../components/Header';
import { Filters } from '../components/Filters';
import { TicketTable } from '../components/TicketTable';
import { TicketDetail } from '../components/TicketDetail';
import { Charts } from '../components/Charts';
import { feedbackApi } from '../services/api';
import { feedbackWebSocket } from '../services/websocket';
import type { Feedback, FeedbackFilters } from '../types';

export const Dashboard: React.FC = () => {
  const [feedbacks, setFeedbacks] = useState<Feedback[]>([]);
  const [filteredFeedbacks, setFilteredFeedbacks] = useState<Feedback[]>([]);
  const [filters, setFilters] = useState<FeedbackFilters>({});
  const [selectedFeedback, setSelectedFeedback] = useState<Feedback | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const categories = Array.from(
    new Set(
      feedbacks
        .map(f => f.analysis?.category)
        .filter((c): c is string => !!c)
    )
  ).sort();

  const loadFeedbacks = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await feedbackApi.list(filters, 100, 0);
      setFeedbacks(response.feedbacks);
      setFilteredFeedbacks(response.feedbacks);
    } catch (err) {
      console.error('Error loading feedbacks:', err);
      setError('Failed to load feedbacks. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    loadFeedbacks();
  }, [loadFeedbacks]);

  useEffect(() => {
    feedbackWebSocket.connect();

    const unsubscribe = feedbackWebSocket.subscribe((newFeedback: Feedback) => {
      setFeedbacks(prev => [newFeedback, ...prev]);
      setFilteredFeedbacks(prev => [newFeedback, ...prev]);
    });

    return () => {
      unsubscribe();
      feedbackWebSocket.disconnect();
    };
  }, []);

  const handleFiltersChange = (newFilters: FeedbackFilters) => {
    setFilters(newFilters);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header feedbacks={filteredFeedbacks} />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Charts feedbacks={filteredFeedbacks} />

        <Filters
          filters={filters}
          onFiltersChange={handleFiltersChange}
          categories={categories}
        />

        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {loading ? (
          <div className="card text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600">Loading feedbacks...</p>
          </div>
        ) : (
          <TicketTable
            feedbacks={filteredFeedbacks}
            onSelectFeedback={setSelectedFeedback}
          />
        )}
      </div>

      <TicketDetail
        feedback={selectedFeedback}
        onClose={() => setSelectedFeedback(null)}
      />
    </div>
  );
};

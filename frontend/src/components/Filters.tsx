import React from 'react';
import type { FeedbackFilters, Sentiment, Urgency } from '../types';

interface FiltersProps {
  filters: FeedbackFilters;
  onFiltersChange: (filters: FeedbackFilters) => void;
  categories: string[];
}

export const Filters: React.FC<FiltersProps> = ({ filters, onFiltersChange, categories }) => {
  const handleChange = (key: keyof FeedbackFilters, value: string | boolean) => {
    onFiltersChange({
      ...filters,
      [key]: value === '' ? undefined : value,
    });
  };

  return (
    <div className="card mb-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Filters</h2>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Urgency
          </label>
          <select
            className="select"
            value={filters.urgency || ''}
            onChange={(e) => handleChange('urgency', e.target.value as Urgency)}
          >
            <option value="">All</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Sentiment
          </label>
          <select
            className="select"
            value={filters.sentiment || ''}
            onChange={(e) => handleChange('sentiment', e.target.value as Sentiment)}
          >
            <option value="">All</option>
            <option value="positive">Positive</option>
            <option value="neutral">Neutral</option>
            <option value="negative">Negative</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Category
          </label>
          <select
            className="select"
            value={filters.category || ''}
            onChange={(e) => handleChange('category', e.target.value)}
          >
            <option value="">All</option>
            {categories.map(cat => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
        </div>

        <div className="flex items-end">
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              checked={filters.unresolvedOnly || false}
              onChange={(e) => handleChange('unresolvedOnly', e.target.checked)}
            />
            <span className="text-sm font-medium text-gray-700">
              Unresolved only
            </span>
          </label>
        </div>
      </div>
    </div>
  );
};

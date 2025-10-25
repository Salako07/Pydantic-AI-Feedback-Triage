import React, { useMemo } from 'react';
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import type { Feedback } from '../types';

interface ChartsProps {
  feedbacks: Feedback[];
}

const COLORS = {
  positive: '#10b981',
  neutral: '#6b7280',
  negative: '#ef4444',
  low: '#3b82f6',
  medium: '#f59e0b',
  high: '#ef4444',
};

const PIE_COLORS = ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#6366f1'];

export const Charts: React.FC<ChartsProps> = ({ feedbacks }) => {
  const categoryData = useMemo(() => {
    const categoryCounts = feedbacks.reduce((acc, f) => {
      if (f.analysis?.category) {
        const category = f.analysis.category;
        acc[category] = (acc[category] || 0) + 1;
      }
      return acc;
    }, {} as Record<string, number>);

    return Object.entries(categoryCounts)
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 6);
  }, [feedbacks]);

  const urgencyData = useMemo(() => {
    const urgencyCounts = { low: 0, medium: 0, high: 0 };
    feedbacks.forEach(f => {
      if (f.analysis?.urgency_level) {
        urgencyCounts[f.analysis.urgency_level]++;
      }
    });

    return [
      { name: 'Low', value: urgencyCounts.low, color: COLORS.low },
      { name: 'Medium', value: urgencyCounts.medium, color: COLORS.medium },
      { name: 'High', value: urgencyCounts.high, color: COLORS.high },
    ];
  }, [feedbacks]);

  const sentimentTrendData = useMemo(() => {
    const sortedFeedbacks = [...feedbacks]
      .filter(f => f.analysis)
      .sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());

    const grouped = sortedFeedbacks.reduce((acc, f) => {
      const date = new Date(f.created_at).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric'
      });

      if (!acc[date]) {
        acc[date] = { date, positive: 0, neutral: 0, negative: 0 };
      }

      if (f.analysis) {
        acc[date][f.analysis.sentiment]++;
      }

      return acc;
    }, {} as Record<string, { date: string; positive: number; neutral: number; negative: number }>);

    return Object.values(grouped).slice(-7);
  }, [feedbacks]);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Issues by Category</h3>
        <ResponsiveContainer width="100%" height={250}>
          <PieChart>
            <Pie
              data={categoryData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {categoryData.map((_, index) => (
                <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>

      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Urgency Breakdown</h3>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={urgencyData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="value" fill="#8884d8">
              {urgencyData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Sentiment Trend</h3>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={sentimentTrendData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="positive" stroke={COLORS.positive} strokeWidth={2} />
            <Line type="monotone" dataKey="neutral" stroke={COLORS.neutral} strokeWidth={2} />
            <Line type="monotone" dataKey="negative" stroke={COLORS.negative} strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { Dashboard } from '../pages/Dashboard';
import { feedbackApi } from '../services/api';
import type { Feedback } from '../types';

vi.mock('../services/api');
vi.mock('../services/websocket', () => ({
  feedbackWebSocket: {
    connect: vi.fn(),
    disconnect: vi.fn(),
    subscribe: vi.fn(() => vi.fn()),
  },
}));

const mockFeedbacks: Feedback[] = [
  {
    id: '1',
    customer_name: 'John Doe',
    email: 'john@example.com',
    message: 'Great product!',
    created_at: new Date().toISOString(),
    analysis: {
      sentiment: 'positive',
      urgency_level: 'low',
      category: 'product',
      summary: 'Customer is satisfied',
      recommended_action: 'Send thank you note',
    },
  },
  {
    id: '2',
    customer_name: 'Jane Smith',
    email: 'jane@example.com',
    message: 'Billing issue',
    created_at: new Date().toISOString(),
    analysis: {
      sentiment: 'negative',
      urgency_level: 'high',
      category: 'billing',
      summary: 'Customer has billing problem',
      recommended_action: 'Contact immediately',
    },
  },
];

describe('Dashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders dashboard header', async () => {
    vi.mocked(feedbackApi.list).mockResolvedValue({
      feedbacks: mockFeedbacks,
      total: 2,
    });

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('AI Feedback Triage Dashboard')).toBeInTheDocument();
    });
  });

  it('displays feedback statistics', async () => {
    vi.mocked(feedbackApi.list).mockResolvedValue({
      feedbacks: mockFeedbacks,
      total: 2,
    });

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('Total Messages')).toBeInTheDocument();
      expect(screen.getByText('2')).toBeInTheDocument();
      expect(screen.getByText('High Urgency')).toBeInTheDocument();
      expect(screen.getByText('1')).toBeInTheDocument();
    });
  });

  it('renders feedback table with data', async () => {
    vi.mocked(feedbackApi.list).mockResolvedValue({
      feedbacks: mockFeedbacks,
      total: 2,
    });

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('Jane Smith')).toBeInTheDocument();
      expect(screen.getByText('john@example.com')).toBeInTheDocument();
      expect(screen.getByText('jane@example.com')).toBeInTheDocument();
    });
  });

  it('shows loading state initially', () => {
    vi.mocked(feedbackApi.list).mockImplementation(
      () => new Promise(() => {}) // Never resolves
    );

    render(<Dashboard />);

    expect(screen.getByText('Loading feedbacks...')).toBeInTheDocument();
  });

  it('displays error message on API failure', async () => {
    vi.mocked(feedbackApi.list).mockRejectedValue(new Error('API Error'));

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText(/Failed to load feedbacks/i)).toBeInTheDocument();
    });
  });

  it('renders filter components', async () => {
    vi.mocked(feedbackApi.list).mockResolvedValue({
      feedbacks: mockFeedbacks,
      total: 2,
    });

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('Filters')).toBeInTheDocument();
      expect(screen.getByLabelText('Urgency')).toBeInTheDocument();
      expect(screen.getByLabelText('Sentiment')).toBeInTheDocument();
      expect(screen.getByLabelText('Category')).toBeInTheDocument();
    });
  });

  it('renders chart components', async () => {
    vi.mocked(feedbackApi.list).mockResolvedValue({
      feedbacks: mockFeedbacks,
      total: 2,
    });

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('Issues by Category')).toBeInTheDocument();
      expect(screen.getByText('Urgency Breakdown')).toBeInTheDocument();
      expect(screen.getByText('Sentiment Trend')).toBeInTheDocument();
    });
  });
});

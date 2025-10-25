import axios from 'axios';
import type { Feedback, FeedbackFilters } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface FeedbackListResponse {
  feedbacks: Feedback[];
  total: number;
}

export interface CreateFeedbackRequest {
  customer_name: string;
  email: string;
  message: string;
}

export const feedbackApi = {
  create: async (data: CreateFeedbackRequest): Promise<Feedback> => {
    const response = await api.post<Feedback>('/api/feedback', data);
    return response.data;
  },

  list: async (filters: FeedbackFilters = {}, limit = 50, skip = 0): Promise<FeedbackListResponse> => {
    const params = new URLSearchParams();
    params.append('limit', limit.toString());
    params.append('skip', skip.toString());

    if (filters.urgency) params.append('urgency', filters.urgency);
    if (filters.category) params.append('category', filters.category);
    if (filters.sentiment) params.append('sentiment', filters.sentiment);
    if (filters.unresolvedOnly) params.append('unresolved_only', 'true');

    const response = await api.get<FeedbackListResponse>('/api/feedback', { params });
    return response.data;
  },

  getById: async (id: string): Promise<Feedback> => {
    const response = await api.get<Feedback>(`/api/feedback/${id}`);
    return response.data;
  },
};

export default api;

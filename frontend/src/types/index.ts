export type Sentiment = "positive" | "neutral" | "negative";
export type Urgency = "low" | "medium" | "high";

export interface FeedbackAnalysis {
  sentiment: Sentiment;
  urgency_level: Urgency;
  category: string;
  summary: string;
  recommended_action: string;
}

export interface Feedback {
  id: string;
  customer_name: string;
  email: string;
  message: string;
  created_at: string;
  analysis: FeedbackAnalysis | null;
  analysis_error?: string;
}

export interface FeedbackFilters {
  urgency?: Urgency;
  category?: string;
  sentiment?: Sentiment;
  unresolvedOnly?: boolean;
}

"""
Phase 2: Slack webhook integration.
Send alerts for high urgency feedback and weekly summary reports.
"""
import os
import logging
import requests
from typing import Optional, Dict, Any
from .schemas import FeedbackDB, AccuracyMetrics, UrgencyBreakdown

logger = logging.getLogger(__name__)

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")


def send_slack_notification(feedback: FeedbackDB) -> bool:
    """
    Send Slack notification for high urgency feedback.

    Args:
        feedback: FeedbackDB object with analysis

    Returns:
        True if sent successfully, False otherwise
    """
    if not SLACK_WEBHOOK_URL:
        logger.warning("SLACK_WEBHOOK_URL not configured, skipping notification")
        return False

    if not feedback.analysis or feedback.analysis.urgency_level != "high":
        return False

    # Format Slack message
    message = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🚨 High Urgency Feedback Alert",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Customer:*\n{feedback.customer_name}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Email:*\n{feedback.email}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Sentiment:*\n{feedback.analysis.sentiment.upper()}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Category:*\n{feedback.analysis.category}"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Summary:*\n{feedback.analysis.summary}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Recommended Action:*\n{feedback.analysis.recommended_action}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Original Message:*\n```{feedback.message[:300]}{'...' if len(feedback.message) > 300 else ''}```"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Feedback ID: {feedback.id} | Created: {feedback.created_at.strftime('%Y-%m-%d %H:%M UTC')}"
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(
            SLACK_WEBHOOK_URL,
            json=message,
            timeout=10
        )
        response.raise_for_status()
        logger.info(f"Slack notification sent for feedback {feedback.id}")
        return True
    except Exception as e:
        logger.error(f"Failed to send Slack notification: {e}")
        return False


def send_weekly_summary_to_slack(
    accuracy: AccuracyMetrics,
    urgency: UrgencyBreakdown,
    report_path: Optional[str] = None
) -> bool:
    """
    Send weekly summary report to Slack.

    Args:
        accuracy: AccuracyMetrics object
        urgency: UrgencyBreakdown object
        report_path: Optional path to JSON report file

    Returns:
        True if sent successfully, False otherwise
    """
    if not SLACK_WEBHOOK_URL:
        logger.warning("SLACK_WEBHOOK_URL not configured, skipping summary")
        return False

    # Format category accuracy for display
    category_text = "\n".join([
        f"• {cat}: {acc:.1%}"
        for cat, acc in sorted(accuracy.by_category.items(), key=lambda x: x[1], reverse=True)[:5]
    ]) or "No category data"

    message = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📊 Weekly AI Agent Performance Report",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Overall Accuracy:*\n{accuracy.overall_accuracy:.1%}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Total Processed:*\n{accuracy.total_processed}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Total Overridden:*\n{accuracy.total_overridden}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Override Rate:*\n{(accuracy.total_overridden / max(accuracy.total_processed, 1)):.1%}"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Top Categories by Accuracy:*\n{category_text}"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*High Urgency:*\n{urgency.high} ({urgency.high / max(urgency.total, 1):.1%})"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Medium Urgency:*\n{urgency.medium} ({urgency.medium / max(urgency.total, 1):.1%})"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Low Urgency:*\n{urgency.low} ({urgency.low / max(urgency.total, 1):.1%})"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Total Feedback:*\n{urgency.total}"
                    }
                ]
            }
        ]
    }

    if report_path:
        message["blocks"].append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"Full report saved to: `{report_path}`"
                }
            ]
        })

    try:
        response = requests.post(
            SLACK_WEBHOOK_URL,
            json=message,
            timeout=10
        )
        response.raise_for_status()
        logger.info("Weekly summary sent to Slack")
        return True
    except Exception as e:
        logger.error(f"Failed to send weekly summary to Slack: {e}")
        return False

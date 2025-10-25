#!/usr/bin/env python3
"""
Seed script to populate the database with sample feedback data.
Run this after starting the services with docker-compose.
"""

import requests
import time
from typing import List, Dict

API_URL = "http://localhost:8000/api/feedback"

SAMPLE_FEEDBACKS: List[Dict[str, str]] = [
    {
        "customer_name": "Alice Johnson",
        "email": "alice.johnson@example.com",
        "message": "I absolutely love your product! It has made my workflow so much more efficient. The interface is intuitive and the features are exactly what I needed. Keep up the great work!"
    },
    {
        "customer_name": "Bob Martinez",
        "email": "bob.martinez@example.com",
        "message": "I've been trying to access my premium account for the past 2 hours but keep getting an error. This is completely unacceptable as I paid for this service. I need this resolved immediately or I want a refund!"
    },
    {
        "customer_name": "Carol White",
        "email": "carol.white@example.com",
        "message": "The recent update broke several features I use daily. The export function no longer works and the app crashes when I try to sync. Please fix this ASAP."
    },
    {
        "customer_name": "David Chen",
        "email": "david.chen@example.com",
        "message": "It would be great if you could add a dark mode option. I often work late at night and the bright interface strains my eyes. Just a suggestion for future updates."
    },
    {
        "customer_name": "Emma Davis",
        "email": "emma.davis@example.com",
        "message": "I was charged twice for my monthly subscription. I've checked my bank statement and there are definitely two charges for the same amount on the same day. Please refund one of them."
    },
    {
        "customer_name": "Frank Wilson",
        "email": "frank.wilson@example.com",
        "message": "The customer support team was incredibly helpful when I had an issue last week. Sarah went above and beyond to resolve my problem. Thank you so much!"
    },
    {
        "customer_name": "Grace Lee",
        "email": "grace.lee@example.com",
        "message": "How do I export my data to CSV format? I couldn't find this option in the settings. Is this feature available?"
    },
    {
        "customer_name": "Henry Brown",
        "email": "henry.brown@example.com",
        "message": "My shipment hasn't arrived yet and it's been 2 weeks since I placed the order. The tracking number shows it's stuck at the distribution center. Can someone look into this?"
    },
    {
        "customer_name": "Iris Taylor",
        "email": "iris.taylor@example.com",
        "message": "The new collaboration features are amazing! Being able to share projects with my team in real-time has transformed how we work together. This is a game-changer."
    },
    {
        "customer_name": "Jack Anderson",
        "email": "jack.anderson@example.com",
        "message": "I'm experiencing slow performance when uploading large files. Files over 100MB take forever to upload. Is there a way to optimize this or increase the upload speed?"
    },
    {
        "customer_name": "Karen Thompson",
        "email": "karen.thompson@example.com",
        "message": "I can't log into my account! I've tried resetting my password three times but I'm not receiving the reset email. This is preventing me from accessing important documents for a client meeting in 1 hour!"
    },
    {
        "customer_name": "Liam Garcia",
        "email": "liam.garcia@example.com",
        "message": "Just wanted to say thank you for the excellent service. The product does exactly what it promises and the price is very reasonable. I've recommended it to several colleagues."
    },
    {
        "customer_name": "Maya Rodriguez",
        "email": "maya.rodriguez@example.com",
        "message": "The mobile app keeps crashing on my Android phone (Samsung Galaxy S23). It crashes every time I try to open the analytics dashboard. Please fix this bug."
    },
    {
        "customer_name": "Nathan Kim",
        "email": "nathan.kim@example.com",
        "message": "Is there an API available for integrating your service with our internal tools? I looked through the documentation but couldn't find any information about API access."
    },
    {
        "customer_name": "Olivia Martinez",
        "email": "olivia.martinez@example.com",
        "message": "I'm very disappointed with the customer service. I've been waiting 3 days for a response to my support ticket and still haven't heard back. This is unacceptable for a paid service."
    },
]


def seed_database():
    """Send sample feedback to the API."""
    print(f"Seeding database with {len(SAMPLE_FEEDBACKS)} sample feedbacks...")
    print(f"Target API: {API_URL}\n")

    successful = 0
    failed = 0

    for i, feedback in enumerate(SAMPLE_FEEDBACKS, 1):
        try:
            print(f"[{i}/{len(SAMPLE_FEEDBACKS)}] Creating feedback from {feedback['customer_name']}...", end=" ")

            response = requests.post(API_URL, json=feedback, timeout=30)
            response.raise_for_status()

            data = response.json()
            analysis = data.get("analysis", {})

            if analysis:
                print(f"✓ [{analysis.get('sentiment', 'N/A')}] [{analysis.get('urgency_level', 'N/A')}] {analysis.get('category', 'N/A')}")
            else:
                print("✓ (analysis pending)")

            successful += 1

            # Small delay to avoid overwhelming the API
            time.sleep(0.5)

        except requests.exceptions.RequestException as e:
            print(f"✗ Error: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
            failed += 1

    print(f"\n{'='*60}")
    print(f"Seeding complete!")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"{'='*60}")
    print(f"\nVisit http://localhost:5173 to view the dashboard")


if __name__ == "__main__":
    print("Waiting for services to be ready...")
    time.sleep(3)

    try:
        seed_database()
    except KeyboardInterrupt:
        print("\n\nSeeding interrupted by user")
    except Exception as e:
        print(f"\n\nFatal error: {e}")

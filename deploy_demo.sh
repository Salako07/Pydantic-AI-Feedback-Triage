#!/bin/bash

# Phase 2: Demo deployment script
# Automates building, starting, and seeding the demo environment

set -e

echo "====================================="
echo "AI Feedback Triage - Demo Deployment"
echo "Phase 2 - Production Ready"
echo "====================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Warning: .env file not found${NC}"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo -e "${YELLOW}Please edit .env and add your API keys before continuing${NC}"
    echo ""
    read -p "Press Enter once you've configured .env, or Ctrl+C to exit..."
fi

echo -e "${BLUE}Step 1: Stopping existing containers...${NC}"
docker compose down

echo ""
echo -e "${BLUE}Step 2: Building images...${NC}"
docker compose build

echo ""
echo -e "${BLUE}Step 3: Starting services...${NC}"
docker compose up -d

echo ""
echo -e "${BLUE}Step 4: Waiting for services to be ready...${NC}"
sleep 10

echo ""
echo -e "${BLUE}Step 5: Checking service health...${NC}"
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}Backend is ready!${NC}"
        break
    fi
    attempt=$((attempt + 1))
    echo "Waiting for backend... ($attempt/$max_attempts)"
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo -e "${YELLOW}Warning: Backend health check timed out${NC}"
    echo "Check logs with: docker compose logs backend"
fi

echo ""
echo -e "${BLUE}Step 6: Seeding demo data...${NC}"
docker compose exec -T backend python -m app.seed.seed_demo

echo ""
echo -e "${GREEN}====================================="
echo "Deployment Complete!"
echo "=====================================${NC}"
echo ""
echo -e "Frontend:       ${BLUE}http://localhost:5173${NC}"
echo -e "Backend API:    ${BLUE}http://localhost:8000${NC}"
echo -e "API Docs:       ${BLUE}http://localhost:8000/docs${NC}"
echo -e "Health Check:   ${BLUE}http://localhost:8000/health${NC}"
echo ""
echo -e "${GREEN}Phase 2 Features:${NC}"
echo "  - AI-powered feedback analysis"
echo "  - Human override system with audit trail"
echo "  - Metrics endpoints (accuracy, urgency, sentiment)"
echo "  - Slack integration for high-urgency alerts"
echo "  - Weekly analytics job"
echo "  - Dynamic prompt configuration"
echo ""
echo -e "${YELLOW}Useful Commands:${NC}"
echo "  View logs:        docker compose logs -f"
echo "  Stop services:    docker compose down"
echo "  Restart:          docker compose restart"
echo "  Clear demo data:  docker compose exec backend python -m app.seed.seed_demo --clear"
echo ""
echo -e "${GREEN}Test the metrics endpoints:${NC}"
echo "  curl http://localhost:8000/api/metrics/accuracy"
echo "  curl http://localhost:8000/api/metrics/urgency-breakdown"
echo "  curl http://localhost:8000/api/metrics/sentiment-trend?days=7"
echo ""

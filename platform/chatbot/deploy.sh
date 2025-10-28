#!/bin/bash

# Deploy script for FacilIAuto WhatsApp Chatbot
# Usage: ./deploy.sh [environment]
# Example: ./deploy.sh production

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-production}
COMPOSE_FILE="docker-compose.prod.yml"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}FacilIAuto WhatsApp Chatbot Deployment${NC}"
echo -e "${GREEN}Environment: ${ENVIRONMENT}${NC}"
echo -e "${GREEN}========================================${NC}\n"

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}❌ Error: .env file not found${NC}"
    echo -e "${YELLOW}Please copy .env.production to .env and configure it${NC}"
    echo -e "${YELLOW}cp .env.production .env${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} .env file found"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Error: Docker is not installed${NC}"
    echo -e "${YELLOW}Please install Docker first${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Docker is installed"

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Error: Docker Compose is not installed${NC}"
    echo -e "${YELLOW}Please install Docker Compose first${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Docker Compose is installed"

# Create necessary directories
echo -e "\n${YELLOW}Creating directories...${NC}"
mkdir -p logs data

# Pull latest images
echo -e "\n${YELLOW}Pulling latest images...${NC}"
docker-compose -f ${COMPOSE_FILE} pull

# Build images
echo -e "\n${YELLOW}Building images...${NC}"
docker-compose -f ${COMPOSE_FILE} build

# Stop existing containers
echo -e "\n${YELLOW}Stopping existing containers...${NC}"
docker-compose -f ${COMPOSE_FILE} down

# Start PostgreSQL first
echo -e "\n${YELLOW}Starting PostgreSQL...${NC}"
docker-compose -f ${COMPOSE_FILE} up -d postgres

# Wait for PostgreSQL to be ready
echo -e "${YELLOW}Waiting for PostgreSQL to be ready...${NC}"
sleep 10

# Check PostgreSQL health
until docker-compose -f ${COMPOSE_FILE} exec -T postgres pg_isready -U faciliauto > /dev/null 2>&1; do
    echo -e "${YELLOW}Waiting for PostgreSQL...${NC}"
    sleep 2
done

echo -e "${GREEN}✓${NC} PostgreSQL is ready"

# Run database migrations
echo -e "\n${YELLOW}Running database migrations...${NC}"
docker-compose -f ${COMPOSE_FILE} run --rm chatbot-api alembic upgrade head

echo -e "${GREEN}✓${NC} Migrations completed"

# Start Redis
echo -e "\n${YELLOW}Starting Redis...${NC}"
docker-compose -f ${COMPOSE_FILE} up -d redis

# Wait for Redis to be ready
echo -e "${YELLOW}Waiting for Redis to be ready...${NC}"
sleep 5

until docker-compose -f ${COMPOSE_FILE} exec -T redis redis-cli ping > /dev/null 2>&1; do
    echo -e "${YELLOW}Waiting for Redis...${NC}"
    sleep 2
done

echo -e "${GREEN}✓${NC} Redis is ready"

# Start all services
echo -e "\n${YELLOW}Starting all services...${NC}"
docker-compose -f ${COMPOSE_FILE} up -d

# Wait for services to start
echo -e "${YELLOW}Waiting for services to start...${NC}"
sleep 10

# Check service health
echo -e "\n${YELLOW}Checking service health...${NC}"

# Check API health
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} API is healthy"
else
    echo -e "${RED}❌${NC} API health check failed"
fi

# Check Celery worker
if docker-compose -f ${COMPOSE_FILE} ps celery-worker | grep -q "Up"; then
    echo -e "${GREEN}✓${NC} Celery worker is running"
else
    echo -e "${RED}❌${NC} Celery worker is not running"
fi

# Check Redis
if docker-compose -f ${COMPOSE_FILE} exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Redis is running"
else
    echo -e "${RED}❌${NC} Redis is not running"
fi

# Check PostgreSQL
if docker-compose -f ${COMPOSE_FILE} exec -T postgres pg_isready -U faciliauto > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} PostgreSQL is running"
else
    echo -e "${RED}❌${NC} PostgreSQL is not running"
fi

# Show running containers
echo -e "\n${YELLOW}Running containers:${NC}"
docker-compose -f ${COMPOSE_FILE} ps

# Show logs
echo -e "\n${YELLOW}Recent logs:${NC}"
docker-compose -f ${COMPOSE_FILE} logs --tail=20

# Final instructions
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Deployment completed!${NC}"
echo -e "${GREEN}========================================${NC}\n"

echo -e "${YELLOW}Next steps:${NC}"
echo -e "1. Configure webhook in Meta Business Manager:"
echo -e "   URL: https://your-domain.com/webhook/whatsapp"
echo -e "   Verify Token: (from your .env file)"
echo -e ""
echo -e "2. Monitor services:"
echo -e "   - API: http://localhost:8000/health"
echo -e "   - Flower: http://localhost:5555"
echo -e "   - Logs: docker-compose -f ${COMPOSE_FILE} logs -f"
echo -e ""
echo -e "3. Test by sending a WhatsApp message to your business number"
echo -e ""
echo -e "${GREEN}Happy chatting! 🚀${NC}\n"

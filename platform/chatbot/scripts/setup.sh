#!/bin/bash
# Setup script for FacilIAuto Chatbot development environment

set -e

echo "=========================================="
echo "FacilIAuto Chatbot - Setup Script"
echo "=========================================="
echo ""

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry is not installed."
    echo "Please install Poetry: https://python-poetry.org/docs/#installation"
    exit 1
fi
echo "✅ Poetry is installed"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed."
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi
echo "✅ Docker is installed"

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed."
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi
echo "✅ Docker Compose is installed"

echo ""
echo "📦 Installing Python dependencies..."
poetry install

echo ""
echo "🔧 Installing pre-commit hooks..."
poetry run pre-commit install

echo ""
echo "📥 Downloading spaCy Portuguese model..."
poetry run python -m spacy download pt_core_news_lg || echo "⚠️  spaCy model download failed. You can install it later."

echo ""
echo "📋 Creating .env file from template..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env file. Please edit it with your configuration."
else
    echo "⚠️  .env file already exists. Skipping."
fi

echo ""
echo "🐳 Starting Docker services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your WhatsApp API credentials"
echo "2. Run 'make dev' to start the development server"
echo "3. Run 'make test' to run tests"
echo "4. Visit http://localhost:8000/docs for API documentation"
echo ""
echo "Useful commands:"
echo "  make help       - Show all available commands"
echo "  make docker-up  - Start Docker services"
echo "  make dev        - Run development server"
echo "  make test       - Run tests"
echo ""

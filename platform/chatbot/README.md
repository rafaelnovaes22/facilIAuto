# FacilIAuto WhatsApp Chatbot

Intelligent WhatsApp chatbot for vehicle recommendations and lead qualification, integrated with the FacilIAuto platform.

## Features

- 🤖 Natural language processing in Portuguese (PT-BR)
- 🚗 Personalized vehicle recommendations
- 📊 Intelligent lead qualification and scoring
- 💬 Context-aware conversations with memory
- 🔄 Seamless integration with existing FacilIAuto backend
- 📈 Real-time metrics and monitoring
- 🔒 LGPD compliant with data encryption
- ⚡ High-performance async architecture

## Tech Stack

- **Framework**: FastAPI
- **AI/ML**: PydanticAI, LangGraph, spaCy, Transformers
- **Storage**: Redis (cache/sessions), PostgreSQL (persistent), DuckDB (analytics)
- **Task Queue**: Celery
- **Monitoring**: Prometheus, Grafana
- **Testing**: pytest, pytest-asyncio

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Poetry (Python package manager)

### Installation

1. Clone the repository and navigate to the chatbot directory:
```bash
cd platform/chatbot
```

2. Copy environment variables:
```bash
cp .env.example .env
```

3. Edit `.env` and configure your WhatsApp Business API credentials and other settings.

4. Start services with Docker Compose:
```bash
docker-compose up -d
```

5. Install dependencies (for local development):
```bash
poetry install
```

6. Install pre-commit hooks:
```bash
poetry run pre-commit install
```

7. Run database migrations:
```bash
poetry run alembic upgrade head
```

### Development

Run the API server locally:
```bash
poetry run uvicorn src.main:app --reload --port 8000
```

Run Celery worker:
```bash
poetry run celery -A src.tasks.celery_app worker --loglevel=info
```

Run tests:
```bash
poetry run pytest
```

Run tests with coverage:
```bash
poetry run pytest --cov=src --cov-report=html
```

### Code Quality

Format code:
```bash
poetry run black src/ tests/
```

Lint code:
```bash
poetry run flake8 src/ tests/
```

Type check:
```bash
poetry run mypy src/
```

Run all checks:
```bash
poetry run pre-commit run --all-files
```

## Project Structure

```
platform/chatbot/
├── src/                    # Source code
│   ├── api/               # API endpoints
│   ├── services/          # Business logic services
│   ├── models/            # Data models
│   ├── tasks/             # Celery tasks
│   └── utils/             # Utility functions
├── tests/                 # Test suite
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── e2e/              # End-to-end tests
├── config/               # Configuration files
├── docs/                 # Documentation
├── data/                 # Local data storage
├── docker-compose.yml    # Docker services
├── Dockerfile           # Container definition
├── pyproject.toml       # Dependencies & config
└── README.md            # This file
```

## API Endpoints

- `POST /webhook/whatsapp` - Receive WhatsApp messages
- `GET /webhook/whatsapp` - Webhook verification
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics

See [API documentation](docs/api.md) for details.

## Configuration

Key environment variables:

- `WHATSAPP_ACCESS_TOKEN` - WhatsApp Business API token
- `WHATSAPP_VERIFY_TOKEN` - Webhook verification token
- `REDIS_URL` - Redis connection string
- `POSTGRES_URL` - PostgreSQL connection string
- `BACKEND_API_URL` - FacilIAuto backend API URL
- `OPENAI_API_KEY` - OpenAI API key for LLM

See `.env.example` for all available options.

## Testing

The project follows XP methodology with comprehensive test coverage:

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **E2E Tests**: Test complete user journeys

Run specific test types:
```bash
poetry run pytest tests/unit/
poetry run pytest tests/integration/
poetry run pytest tests/e2e/
```

## Monitoring

Access monitoring dashboards:

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

## Documentation

Detailed documentation is available in the `docs/` directory:

- [Setup Guide](docs/setup.md)
- [Architecture](docs/architecture.md)
- [API Reference](docs/api.md)
- [Development Guide](docs/development.md)
- [Deployment Guide](docs/deployment.md)

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests and code quality checks
4. Submit a pull request

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for details.

## License

See [LICENSE](../../LICENSE) file.

## Support

For issues or questions:
- Check [troubleshooting guide](docs/troubleshooting.md)
- Review [requirements](../../.kiro/specs/whatsapp-chatbot/requirements.md)
- Contact the development team

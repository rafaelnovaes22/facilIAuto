# RobustCar Production Scraper

Enterprise-grade web scraping system for extracting vehicle data from RobustCar dealership website.

## Project Structure

```
platform/scrapers/
├── scraper/              # Main scraper package
│   ├── __init__.py
│   ├── models/          # Data models (Pydantic)
│   ├── services/        # Core services
│   ├── utils/           # Utility functions
│   └── orchestrator.py  # Main orchestrator
├── config/              # Configuration files
│   ├── __init__.py
│   └── config.yaml      # Default configuration
├── tests/               # Test suite
│   ├── __init__.py
│   └── test_*.py        # Test files
├── cache/               # HTTP cache (created at runtime)
├── state/               # SQLite state database (created at runtime)
├── logs/                # Log files (created at runtime)
├── output/              # Scraped data output (created at runtime)
├── requirements.txt     # Python dependencies
└── README-SCRAPER.md    # This file
```

## Installation

### Prerequisites

- Python 3.10+
- pip

### Setup

```bash
# Navigate to scrapers directory
cd platform/scrapers

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Configuration is managed through `config/config.yaml`. Key settings:

- **HTTP**: Timeout, retries, user agent
- **Rate Limiting**: Requests per minute, delays
- **Workers**: Concurrent workers, queue size
- **Cache**: TTL, max size
- **Output**: Format, compression
- **Quality**: Minimum completeness, fail threshold
- **Logging**: Level, format, file location
- **Metrics**: Prometheus export

You can also override settings using environment variables:
```bash
export SCRAPER_HTTP_TIMEOUT=60
export SCRAPER_WORKERS_MAX_CONCURRENT=5
```

## Usage

### Full Scraping Mode

Extract all vehicles from the website:

```bash
python -m scraper.orchestrator --mode full
```

### Incremental Mode

Extract only new or modified vehicles:

```bash
python -m scraper.orchestrator --mode incremental
```

### Resume from Checkpoint

Resume a previous execution:

```bash
python -m scraper.orchestrator --resume checkpoint_123
```

### Dry Run

Test without saving data:

```bash
python -m scraper.orchestrator --mode full --dry-run
```

### Custom Configuration

Use a custom config file:

```bash
python -m scraper.orchestrator --config custom_config.yaml
```

## Output

Scraped data is exported to `output/` directory:

- **vehicles.json.gz**: Compressed JSON with all vehicles
- **rejected.json**: Vehicles that failed validation
- **metadata.json**: Execution statistics and metrics

### Output Format

```json
{
  "metadata": {
    "schema_version": "1.0",
    "scraper_version": "1.0.0",
    "timestamp": "2025-10-30T14:30:00Z",
    "total_vehicles": 73,
    "source": "robustcar.com.br"
  },
  "vehicles": [
    {
      "id": "robust_1_0_1757696379",
      "nome": "Toyota Corolla GLi",
      "marca": "Toyota",
      "modelo": "Corolla",
      "ano": 2022,
      "preco": 95000.0,
      "quilometragem": 45000,
      "combustivel": "Flex",
      "cambio": "Automático CVT",
      "cor": "Prata",
      "portas": 4,
      "categoria": "Sedan",
      "imagens": ["url1", "url2"],
      "descricao": "...",
      "url_original": "...",
      "data_scraping": "2025-10-30T14:25:00Z",
      "content_hash": "abc123..."
    }
  ]
}
```

## Testing

Run the test suite:

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=scraper --cov-report=term-missing

# Specific test file
pytest tests/test_parser.py -v
```

## Monitoring

Prometheus metrics are exposed at `http://localhost:9090/metrics` when enabled.

Key metrics:
- `scraper_vehicles_processed_total`
- `scraper_vehicles_success_total`
- `scraper_vehicles_error_total`
- `scraper_request_duration_seconds`

## Logging

Logs are written to `logs/scraper.log` in JSON format:

```json
{
  "timestamp": "2025-10-30T14:30:00Z",
  "level": "INFO",
  "message": "Scraping started",
  "mode": "full",
  "version": "1.0.0"
}
```

## Troubleshooting

### Rate Limiting (429 Errors)

If you encounter 429 errors, adjust rate limiting in config:

```yaml
rate_limiting:
  requests_per_minute: 30  # Reduce from 60
  delay_between_requests: 2.0  # Increase from 1.0
```

### Parsing Errors

If selectors fail, update `config.yaml` selectors section with correct CSS selectors.

### Memory Issues

Reduce concurrent workers:

```yaml
workers:
  max_concurrent: 2  # Reduce from 3
```

## Development

### Code Quality

```bash
# Format code
black .

# Lint
flake8 .

# Type check
mypy .
```

### Adding New Features

1. Create feature branch
2. Write tests first (TDD)
3. Implement feature
4. Run tests and quality checks
5. Update documentation

## Architecture

See `.kiro/specs/scraper-robustcar-producao/design.md` for detailed architecture documentation.

## Requirements

See `.kiro/specs/scraper-robustcar-producao/requirements.md` for complete requirements specification.

## License

Internal use only - FacilIAuto platform.

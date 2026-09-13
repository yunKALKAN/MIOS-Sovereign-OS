# Getting Started

## Prerequisites

- Python 3.10+
- pip
- Git

## Quick Start

```bash
git clone https://github.com/yunKALKAN/web4-engine.git
cd web4-engine
pip install -r requirements.txt
python -m uvicorn apps.api.main:app --port 5002
```

## Verify

```bash
curl http://127.0.0.1:5002/api/v1/health
```

## API Documentation

Once running, visit:

- Swagger: http://127.0.0.1:5002/docs
- ReDoc: http://127.0.0.1:5002/redoc

## Run Tests

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

## Next Steps

- Read [ARCHITECTURE.md](../ARCHITECTURE.md)
- Review [API.md](../API.md)
- Check [ROADMAP.md](../ROADMAP.md)

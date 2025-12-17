# Roofing Books CFO

AI-powered bookkeeping and fractional CFO for roofing contractors.

## Quick Start

### Option 1: Docker (Recommended)

```bash
# 1. Clone repo
git clone https://github.com/YOUR_USERNAME/roofing-books-cfo.git
cd roofing-books-cfo

# 2. Configure environment
cp .env.example .env
# Edit .env with your credentials (see below)

# 3. Set up database
# Copy contents of supabase/schema.sql to Supabase SQL editor and run

# 4. Start with Docker
docker-compose up

# Access:
# - Dashboard: http://localhost:8503
# - API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

See [DOCKER_SETUP.md](DOCKER_SETUP.md) for detailed Docker instructions.

### Option 2: Local Development

```bash
# 1. Clone repo
git clone https://github.com/YOUR_USERNAME/roofing-books-cfo.git
cd roofing-books-cfo

# 2. Set up Python environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your credentials (see below)

# 4. Set up database
# Copy contents of supabase/schema.sql to Supabase SQL editor and run

# 5. Start the API
python src/main.py

# 6. Start the dashboard (separate terminal)
streamlit run src/dashboard/owner.py --server.port 8503
```

## Required Credentials

| Service | Get From | Required For |
|---------|----------|--------------|
| QuickBooks Online | [developer.intuit.com](https://developer.intuit.com) | Transaction sync |
| Supabase | [supabase.com](https://supabase.com) | Database |
| Anthropic | [console.anthropic.com](https://console.anthropic.com) | AI classification |
| Slack | [api.slack.com](https://api.slack.com/apps) | Notifications |

## Project Structure

```
roofing-books-cfo/
├── src/
│   ├── main.py                 # FastAPI application
│   ├── services/
│   │   ├── qbo/                # QuickBooks integration
│   │   ├── classification/     # AI transaction classifier
│   │   └── forecasting/        # Cash flow forecasting
│   ├── dashboard/
│   │   └── owner.py            # Streamlit owner dashboard
│   ├── models/                 # Pydantic models
│   └── utils/                  # Helpers
├── supabase/
│   └── schema.sql              # Database schema
├── tests/                      # Test files
├── docs/                       # Spec kit & documentation
│   ├── prd/                    # Product requirements
│   ├── system-design/          # Technical specs
│   └── automations/            # Workflow definitions
├── .env.example                # Environment template
├── requirements.txt            # Core Python dependencies (~1.5GB images)
├── requirements-full.txt       # Full deps with OCR (~3.7GB images)
├── Dockerfile                  # Development Docker image
├── Dockerfile.prod             # Production Docker image
├── docker-compose.yml          # Docker Compose config
└── README.md                   # This file
```

## Development Workflow

### Option 1: Docker (Recommended)

```bash
# Start all services
docker-compose up

# Start only API and Dashboard (uses Supabase)
docker-compose up api dashboard

# View logs
docker-compose logs -f

# See DOCKER_SETUP.md for detailed instructions
```

### Option 2: Local Development

```bash
# API server (auto-reloads)
uvicorn src.main:app --reload --port 8000

# Dashboard (auto-reloads)
streamlit run src/dashboard/owner.py --server.port 8503

# Run tests
pytest tests/
```

## Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/auth/qbo/connect` | GET | Start QBO OAuth |
| `/auth/qbo/callback` | GET | QBO OAuth callback |
| `/api/sync/qbo` | POST | Sync transactions from QBO |
| `/api/transactions` | GET | List transactions |
| `/api/transactions/{id}/classify` | POST | Classify transaction |
| `/api/transactions/classify/batch` | POST | Batch classify transactions |
| `/api/jobs` | GET | List jobs |
| `/api/cash/position` | GET | Current cash position |
| `/api/cash/forecast` | GET | 13-week forecast |

## Supabase Storage (Deal Room)

- **Bucket**: create a private bucket named `deal-room`
- **Used by**: `POST /api/valuation/exit-readiness/upload` for Exit Readiness due diligence uploads
- **Metadata table**: `public.exit_readiness_documents`

## Environment-specific configs

| Variable | Development | Production |
|----------|-------------|------------|
| `APP_ENV` | development | production |
| `QBO_ENVIRONMENT` | sandbox | production |
| `LOG_LEVEL` | DEBUG | INFO |

## Docker Image Sizes

- **Core** (`requirements.txt`): ~1.46GB - Recommended for most use cases
- **Full** (`requirements-full.txt`): ~3.7GB - Only needed when OCR is implemented

See [DOCKER_OPTIMIZATION.md](DOCKER_OPTIMIZATION.md) for details.

## Documentation

Full specifications in `/docs`:
- **PRDs**: Product requirements
- **System Design**: Data models, agents
- **Automations**: Workflow YAML specs
- **Implementation Guide**: OSS tool mapping

Additional guides:
- [DOCKER_SETUP.md](DOCKER_SETUP.md) - Docker usage guide
- [DOCKER_OPTIMIZATION.md](DOCKER_OPTIMIZATION.md) - Image size optimization
- [TESTING_SETUP.md](TESTING_SETUP.md) - QBO testing setup
- [SYNC_USAGE.md](SYNC_USAGE.md) - Transaction sync guide
- [NEXT_STEPS_SUMMARY.md](NEXT_STEPS_SUMMARY.md) - Implementation status

## Contributing

1. Create feature branch from `develop`
2. Make changes
3. Run tests: `pytest`
4. Submit PR to `develop`

## License

Proprietary - All rights reserved

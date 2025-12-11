# Roofing Books CFO

AI-powered bookkeeping and fractional CFO for roofing contractors.

## Quick Start

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
streamlit run src/dashboard/owner.py
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
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Development Workflow

### Running locally

```bash
# API server (auto-reloads)
uvicorn src.main:app --reload --port 8000

# Dashboard (auto-reloads)
streamlit run src/dashboard/owner.py

# Run tests
pytest tests/
```

### Database migrations

Currently using raw SQL. Run new migrations in Supabase SQL editor.

### Adding a new service

1. Create folder in `src/services/`
2. Add router to `src/main.py`
3. Add tests in `tests/`

## Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/auth/qbo/connect` | GET | Start QBO OAuth |
| `/auth/qbo/callback` | GET | QBO OAuth callback |
| `/api/transactions` | GET | List transactions |
| `/api/transactions/classify` | POST | Classify transaction |
| `/api/jobs` | GET | List jobs |
| `/api/cash/position` | GET | Current cash position |
| `/api/cash/forecast` | GET | 13-week forecast |

## Environment-specific configs

| Variable | Development | Production |
|----------|-------------|------------|
| `APP_ENV` | development | production |
| `QBO_ENVIRONMENT` | sandbox | production |
| `LOG_LEVEL` | DEBUG | INFO |

## Documentation

Full specifications in `/docs`:
- **PRDs**: Product requirements
- **System Design**: Data models, agents
- **Automations**: Workflow YAML specs
- **Implementation Guide**: OSS tool mapping

## Contributing

1. Create feature branch from `develop`
2. Make changes
3. Run tests: `pytest`
4. Submit PR to `develop`

## License

Proprietary - All rights reserved
